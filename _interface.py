from telebot import types, telebot
from init_keyboards import default_keyboard, create_rating
from conversion import text_to_rating
from nlp_model import PredictModel
from nlp_model import tokenize
import database
import sqlite3
from bot_token import *

"""
Creating/initializing database and bot 
"""
db = sqlite3.connect('usersDB.db', check_same_thread=False)
sql = db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS users(
    ID TEXT,
    Отзыв TEXT,
    Окраска INT,
    Потенциал INT,
    Производительность INT
)""")
db.commit()

sql.execute("""CREATE TABLE IF NOT EXISTS names(
    ID TEXT,
    name TEXT,
    master_id TEXT
)""")
db.commit()

bot = telebot.TeleBot(token_anton)

"""
Creating/initializing keyboards
"""
default_kb = default_keyboard()
rating_kb = create_rating()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вас приветствует бот создания и получения"
                                      " отзывов о сотрудниках компании ГринСайт."
                                      " Он предоставляет доступ к базе данных", reply_markup=default_kb)

    master_id = str(message.from_user.id)
    if database.check_user_id(sql, master_id):
        bot.send_message(message.chat.id, "Вашего id нет в базе данных, введите своё имя: ", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, add_user_id)

def add_user_id(message):                                                               # whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad
    text = message.text
    master_id = str(message.from_user.id)
    if check_cheating_one(text, master_id):
        bot.send_message(message.chat.id, "Дурак, в бан!!!", reply_markup=default_kb)
    else:
        new_worker_id = database.get_ids(sql) + 1
        sql.execute(f"INSERT INTO names VALUES(?,?,?)", (new_worker_id, text, master_id))
        db.commit()
        msg = "Что будем делать дальше?"
        bot.send_message(message.chat.id, msg, reply_markup=default_kb)


@bot.message_handler(content_types=['text'])
def handler(message):
    master_id = message.from_user.id
    if message.text == "Написать отзыв":
        bot.send_message(message.chat.id, "Введите ID пользователя, на которого хотите написать отзыв",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "add", master_id)
    if message.text == "Запросить данные по ID":
        bot.send_message(message.chat.id, "Введите ID пользователя, для которого нужно вывести данные",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "get_avg_id", master_id)
    if message.text == "Запросить отзывы по ID":
        bot.send_message(message.chat.id, "Введите ID пользователя, для которого нужно вывести данные",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "get_review_id", master_id)
    if message.text == "Запросить отзывы по имени":
        bot.send_message(message.chat.id, "Введите имя пользователя, для которого нужно вывести отзывы",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_review_name, "get_review_name")
    if message.text == "Запросить данные по имени":
        bot.send_message(message.chat.id, "Введите имя пользователя, для которого нужно вывести данные",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_summary_name, "get_avg_name")
    if message.text == "Запросить данные по отзывам от пользователя":
        bot.send_message(message.chat.id, "Введите имя пользователя, для которого нужно вывести данные",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_reviews_master_id, "get_reviews_master_id")


def collect_id(message, mode, master_id):
    worker_id = message.text
    if mode == "add":
        if check_name(message):
            bot.send_message(message.chat.id,
                             f"Фамилия сотрудника с ID не найдена, введите имя нового сотрудника: ",
                             reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, add_name, worker_id, master_id)
        else:
            bot.send_message(message.chat.id, f"Введите оценку продуктивности сотрудника {worker_id}",
                             reply_markup=rating_kb)
            bot.register_next_step_handler(message, set_productivity, worker_id, master_id)
    elif mode == "get_avg_id":
        get_summary(message, worker_id)
    elif mode == "get_review_id":
        get_review_id(message, worker_id)
    elif mode == "get_review_name":
        bot.send_message(message.chat.id, f"Введите имя сотрудника: ", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_review_name, worker_id)
    elif mode == "get_avg_name":
        bot.send_message(message.chat.id, f"Введите имя сотрудника: ", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_summary_name, worker_id)
    elif mode == "get_reviews_master_id":
        bot.send_message(message.chat.id, f"Введите имя сотрудника: ", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_reviews_master_id, worker_id)


def add_name(message, worker_id, master_id):
    name = message.text
    sql.execute(f"INSERT INTO names VALUES(?,?,?)", (worker_id, name, master_id))
    db.commit()
    bot.send_message(message.chat.id, f"Введите оценку продуктивности сотрудника {worker_id}",
                     reply_markup=rating_kb)
    bot.register_next_step_handler(message, set_productivity, worker_id, master_id)


def set_productivity(message, worker_id, master_id):
    productivity = text_to_rating(message.text)
    bot.send_message(message.chat.id, f"Введите оценку потенциала сотрудника {worker_id}",
                     reply_markup=rating_kb)
    bot.register_next_step_handler(message, set_potential, worker_id, productivity,master_id)


def set_potential(message, worker_id, productivity, master_id):
    potential = text_to_rating(message.text)
    bot.send_message(message.chat.id, f"Введите отзыв на сотрудника {worker_id}", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, add_review_to_db, worker_id, productivity, potential, master_id)


def add_review_to_db(message, worker_id, productivity, potential, master_id):
    text = message.text
    tone = PredictModel.get_predict(text)
    sql.execute(f"INSERT INTO users VALUES(?,?,?,?,?,?)", (worker_id, text, tone, potential, productivity, master_id))
    db.commit()
    bot.send_message(message.chat.id, f"Отзыв на сотрудника {worker_id} добавлен!", reply_markup=default_kb)


def check_name(message):
    ids = sql.execute(f"SELECT names.id FROM names INNER JOIN users ON users.ID = names.ID").fetchall()
    ids = [' '.join(t) for t in ids]
    return message.text not in ids



def get_summary_name(message, worker_id):
    # for review in sql.execute(f"SELECT Потенциал FROM users WHERE ID = '{worker_id}'"):
    #     bot.send_message(message.chat.id, review, reply_markup=mm)
    worker_name = message.text
    names = database.get_joined_ids(sql)
    names =  {s.pop(): s.pop() for s in map(set, names)}
    names = {str(v): k for k, v in names.items()}

    if worker_name in names:
        get_summary(message, names[worker_name])
    else:
        bot.send_message(message.chat.id, "Пользователь с указанным именем не найден", reply_markup=default_kb)


def get_summary(message, worker_id):
    msg = ''
    avg_potential = sql.execute(f"SELECT Avg(Потенциал) FROM users WHERE ID = '{worker_id}'")
    msg += 'Средний потенциал: ' + str(round(float(avg_potential.fetchone()[0]) / 3 * 100, 1)) + '%\n'
    avg_tone = sql.execute(f"SELECT Avg(Окраска) FROM users WHERE ID = '{worker_id}'")
    msg += 'Средняя мнение: ' + str(round(float(avg_tone.fetchone()[0]) / 2 * 100, 1)) + '%\n'
    avg_productivity = sql.execute(f"SELECT Avg(Производительность) FROM users WHERE ID = '{worker_id}'")

    bot.send_message(message.chat.id, msg, reply_markup=default_kb)




def get_review_id(message, worker_id):
    text = sql.execute(f"SELECT Отзыв FROM users WHERE ID = '{worker_id}'")
    text = ''.join(str(x[0] + '\n\n') for x in text.fetchall())
    bot.send_message(message.chat.id, text, reply_markup=default_kb)


def get_review_name(message, whataheeeelllomagad):                      # whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad
    worker_name = message.text
    names = database.get_joined_ids(sql)
    names =  {s.pop(): s.pop() for s in map(set, names)}
    names = {str(v): k for k, v in names.items()}

    if worker_name in names:
        text = sql.execute(f"SELECT Отзыв FROM users WHERE ID = '{names[worker_name]}'")
        text = ''.join(str(x[0] + '\n\n') for x in text.fetchall())
        bot.send_message(message.chat.id, text, reply_markup=default_kb)
    else:
        bot.send_message(message.chat.id, 'Пользователь с указанным именем не найден', reply_markup=default_kb)

def check_cheating_one(name, master_id):
    return (name in database.get_names(sql) and master_id not in database.get_masters(sql)
            or name not in database.get_names(sql) and master_id in database.get_masters(sql))


def get_reviews_master_id(message, whataheeeelllomagad):                 # whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad
    worker_name = message.text
    master_ids = database.get_joined_master_ids(sql)
    master_ids =  {s.pop(): s.pop() for s in map(set, master_ids)}

    text = sql.execute(f"SELECT Отзыв FROM users WHERE master_id = '{master_ids[worker_name]}'")
    text = ''.join(str(x[0] + '\n\n') for x in text)
    bot.send_message(message.chat.id, text, reply_markup=default_kb)


bot.polling(none_stop=True)
