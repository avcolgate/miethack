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
    Производительность INT,
    master_id INT
)""")
db.commit()

bot = telebot.TeleBot(token_yarik)

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

@bot.message_handler(content_types=['text'])
def handler(message):
    master_id = message.from_user.id
    if message.text == "Написать отзыв":
        bot.send_message(message.chat.id, "Введите ID пользователя, на которого хотите написать отзыв",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "add", master_id)
    elif message.text == "Запросить данные":
        bot.send_message(message.chat.id, "Введите ID пользователя, для которого нужно вывести данные",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "get_avg_id", master_id)
    elif message.text == "Запросить отзывы":
        bot.send_message(message.chat.id, "Введите ID пользователя, для которого нужно вывести данные",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "get_review_id", master_id)
    elif message.text == "Запросить данные по отзывам от пользователя":
        bot.send_message(message.chat.id, "Введите ID пользователя, для которого нужно вывести данные",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "get_reviews_master_id", master_id)


def collect_id(message, mode, master_id):
    worker_id = message.text
    if mode == "add":
        bot.send_message(message.chat.id, f"Введите оценку продуктивности сотрудника {worker_id}",
                             reply_markup=rating_kb)
        bot.register_next_step_handler(message, set_productivity, worker_id, master_id)
    elif mode == "get_avg_id":
        get_summary(message, worker_id)
    elif mode == "get_review_id":
        get_review_id(message, worker_id)
    elif mode == "get_reviews_master_id":
        get_reviews_master_id(message)


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



def get_summary(message, worker_id):
    msg = ''
    avg_tone = sql.execute(f"SELECT Avg(Окраска) FROM users WHERE ID = '{worker_id}'")
    msg += 'Мнение о сотруднике: ' + str(round(float(avg_tone.fetchone()[0]) / 2 * 100, 1)) + '%\n'
    avg_productivity = sql.execute(f"SELECT Avg(Производительность) FROM users WHERE ID = '{worker_id}'")
    msg += 'Средняя продуктивость: ' + str(round(float(avg_productivity.fetchone()[0]) / 3 * 100, 1)) + '%\n'
    avg_potential = sql.execute(f"SELECT Avg(Потенциал) FROM users WHERE ID = '{worker_id}'")
    msg += 'Средний потенциал: ' + str(round(float(avg_potential.fetchone()[0]) / 3 * 100, 1)) + '%\n'

    bot.send_message(message.chat.id, msg, reply_markup=default_kb)



def get_review_id(message, worker_id):
    text = sql.execute(f"SELECT Отзыв FROM users WHERE ID = '{worker_id}'")
    text = ''.join(str(x[0] + '\n\n') for x in text.fetchall())
    bot.send_message(message.chat.id, text, reply_markup=default_kb)



def get_reviews_master_id(message):
    worker_name = message.text
    master_ids = database.get_joined_master_ids(sql)
    master_ids =  {s.pop(): s.pop() for s in map(set, master_ids)}
    master_ids = {str(v): k for k, v in master_ids.items()}

    text = sql.execute(f"SELECT Отзыв FROM users WHERE master_id = '{master_ids[worker_name]}'")
    text = ''.join(str(x[0] + '\n\n') for x in text)
    bot.send_message(message.chat.id, text, reply_markup=default_kb)


bot.polling(none_stop=True)
