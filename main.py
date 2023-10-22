from ast import Return
from doctest import master
import telebot
from telebot import types
import sqlite3
from conversion import text_to_rating
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
import string
import nltk
from nltk.corpus import stopwords
import joblib

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

snowball = SnowballStemmer(language="russian")
russian_stop_words = stopwords.words("russian")

def tokenize_sentence(sentence: str, remove_stop_words: bool = True):
    tokens = word_tokenize(sentence, language="russian")
    tokens = [i for i in tokens if i not in string.punctuation]
    if remove_stop_words:
        tokens = [i for i in tokens if i not in russian_stop_words]
    tokens = [snowball.stem(i) for i in tokens]
    return tokens

def tokenize(x):
  return tokenize_sentence(x, remove_stop_words=True)

loaded = joblib.load('model_nlp_persited.joblib')

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

sql.execute("""CREATE TABLE IF NOT EXISTS users(
    ID TEXT,
    Отзыв TEXT,
    Окраска INT,
    Потенциал INT,
    Производительность INT
)""")
db.commit()

bot = telebot.TeleBot('6670755134:AAFytKlfLEtiyTHsAcXtxCrQ50MYCqiJpJU')

mm = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
button1 = types.KeyboardButton("Написать отзыв")
button2 = types.KeyboardButton("Запросить данные по ID")
button3 = types.KeyboardButton("Запросить отзывы по ID")
button4 = types.KeyboardButton("Запросить отзывы по имени")
button5 = types.KeyboardButton("Запросить данные по имени")
button6 = types.KeyboardButton("Запросить данные по отзывам от пользователя")
mm.add(button1, button2, button3, button4, button5, button6)


def create_rating():
    rating = types.ReplyKeyboardMarkup(row_width=3)

    lower_than_average = types.KeyboardButton('Ниже среднего')
    average = types.KeyboardButton('Средняя')
    greater_than_average = types.KeyboardButton('Выше среднего')
    rating.add(lower_than_average)
    rating.add(average)
    rating.add(greater_than_average)
    return rating

rating = create_rating()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вас приветствует бот создания и получения"
                                      " отзывов о сотрудниках компании ГринСайт."
                                      " Он предоставляет доступ к базе данных", reply_markup=mm)  
    
    master_id = str(message.from_user.id)
    if check_user_id(master_id):
        bot.send_message(message.chat.id, "Вашего id нет в базе данных, введите своё имя: ", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, add_user_id, "add_user_id")

def add_user_id(message, whataheeeelllomagad):                                                               # whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad 
    text = message.text
    master_id = str(message.from_user.id)
    if check_cheating_one(text, master_id):
        bot.send_message(message.chat.id, "Дурак, в бан!!!", reply_markup=mm)
    else:   
        new_worker_id = get_ids() + 1
        sql.execute(f"INSERT INTO names VALUES(?,?,?)", (new_worker_id, text, master_id))
        db.commit()


@bot.message_handler(content_types=['text'])
def handler(message):
    if message.text == "Написать отзыв":
        master_id = message.from_user.id
        bot.send_message(message.chat.id, "Введите ID пользователя, на которого хотите написать отзыв",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "add", master_id)

    if message.text == "Запросить данные по ID":
        bot.send_message(message.chat.id, "Введите ID пользователя, для которого нужно вывести данные",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "get_avg_id")

    if message.text == "Запросить отзывы по ID":
        bot.send_message(message.chat.id, "Введите ID пользователя, для которого нужно вывести данные",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "get_review_id")
    
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
        if check_name(message, worker_id):
            bot.send_message(message.chat.id, f"Фамилия сотрудника с ID не найдена, добавьте нового сотрудника: ", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, add_name, worker_id)
        else:
            bot.send_message(message.chat.id, f"Введите оценку продуктивности сотрудника {worker_id}",
                             reply_markup=rating)
            bot.register_next_step_handler(message, set_productivity, worker_id, master_id)

    elif mode == "get_avg_id":
        get_summary_ID(message, worker_id)

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
    sql.execute(f"INSERT INTO names VALUES(?,?)", (worker_id, name))
    db.commit()
    bot.send_message(message.chat.id, f"Введите оценку продуктивности сотрудника {worker_id}",
                             reply_markup=rating)
    bot.register_next_step_handler(message, set_productivity, worker_id, master_id)


def set_productivity(message, worker_id, master_id):
    productivity = text_to_rating(message.text)
    bot.send_message(message.chat.id, f"Введите оценку потенциала сотрудника {worker_id}",
                     reply_markup=rating)
    bot.register_next_step_handler(message, set_potential, worker_id, productivity,master_id)


def set_potential(message, worker_id, productivity, master_id):
    potential = text_to_rating(message.text)
    bot.send_message(message.chat.id, f"Введите отзыв на сотрудника {worker_id}", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, add_review_to_db, worker_id, productivity, potential, master_id)


def add_review_to_db(message, worker_id, productivity, potential, master_id):
    text = message.text
    tone = int(loaded['model'].predict([text])[0])
    sql.execute(f"INSERT INTO users VALUES(?,?,?,?,?,?)", (worker_id, text, tone, potential, productivity, master_id))
    db.commit()
    bot.send_message(message.chat.id, f"Отзыв на сотрудника {worker_id} добавлен!", reply_markup=mm)


def check_name(message, id):
    ids = sql.execute(f"SELECT names.id FROM names INNER JOIN users ON users.ID = names.ID").fetchall()
    ids = [' '.join(t) for t in ids]
    return message.text not in ids


def get_joined_ids():
    names = sql.execute(f"SELECT names.ID, names.name FROM names INNER JOIN users ON users.ID = names.ID").fetchall() # Уже не понимаю почему так написано, мб баг
    return names

def get_joined_master_ids():
    master_ids = sql.execute(f"SELECT users.master_id, names.name FROM names INNER JOIN users ON users.master_id = names.master_id").fetchall()
    return master_ids

def get_ids():                                                                                                      
    names_len = len(sql.execute(f"SELECT names.ID FROM names").fetchall())
    return names_len

def get_names():
    names = sql.execute(f"SELECT names.name FROM names").fetchall()
    names = ''.join(str(x[0] + '\n\n') for x in names)
    return names


def get_masters():
    masters = sql.execute(f"SELECT names.master_id FROM names ").fetchall()
    masters = ''.join(str(x[0] + '\n\n') for x in masters)
    return masters


def check_user_id(master_id):
    names = sql.execute(f"SELECT master_id FROM names").fetchall()
    names = ''.join(str(x[0] + '\n\n') for x in names)
    if names != 0:
        return master_id not in names
    else:
        return 0


def get_summary_ID(message, worker_id):
    # for review in sql.execute(f"SELECT Потенциал FROM users WHERE ID = '{worker_id}'"):
    #     bot.send_message(message.chat.id, review, reply_markup=mm)
    msg = ''

    avg_potential = sql.execute(f"SELECT Avg(Потенциал) FROM users WHERE ID = '{worker_id}'")
    msg += 'Средний потенциал: ' + str(round(float(avg_potential.fetchone()[0])/3 * 100, 1)) + '%\n'
    avg_tone = sql.execute(f"SELECT Avg(Окраска) FROM users WHERE ID = '{worker_id}'")
    msg += 'Средняя мнение: ' + str(round(float(avg_tone.fetchone()[0])/2 * 100, 1)) + '%\n'
    avg_productivity = sql.execute(f"SELECT Avg(Производительность) FROM users WHERE ID = '{worker_id}'")
    msg += 'Средняя производительность: ' + str(round(float(avg_productivity.fetchone()[0])/3 * 100, 1)) + '%\n'
    
    bot.send_message(message.chat.id, msg, reply_markup=mm)


def get_summary_name(message, worker_id):
    # for review in sql.execute(f"SELECT Потенциал FROM users WHERE ID = '{worker_id}'"):
    #     bot.send_message(message.chat.id, review, reply_markup=mm)
    worker_name = message.text
    names = get_joined_ids()
    names =  {s.pop(): s.pop() for s in map(set, names)}
    names = {str(v): k for k, v in names.items()}
    msg = ''

    avg_potential = sql.execute(f"SELECT Avg(Потенциал) FROM users WHERE ID = '{names[worker_name]}'")
    msg += 'Средний потенциал: ' + str(round(float(avg_potential.fetchone()[0])/3 * 100, 1)) + '%\n'
    avg_tone = sql.execute(f"SELECT Avg(Окраска) FROM users WHERE ID = '{names[worker_name]}'")
    msg += 'Средняя мнение: ' + str(round(float(avg_tone.fetchone()[0])/2 * 100, 1)) + '%\n'
    avg_productivity = sql.execute(f"SELECT Avg(Производительность) FROM users WHERE ID = '{names[worker_name]}'")
    msg += 'Средняя производительность: ' + str(round(float(avg_productivity.fetchone()[0])/3 * 100, 1)) + '%\n'
    
    bot.send_message(message.chat.id, msg, reply_markup=mm)


def get_review_id(message, worker_id):
    text = sql.execute(f"SELECT Отзыв FROM users WHERE ID = '{worker_id}'")
    text = ''.join(str(x[0] + '\n\n') for x in text.fetchall())
    bot.send_message(message.chat.id, text, reply_markup=mm)
    

def get_review_name(message, whataheeeelllomagad):                      # whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad 
    worker_name = message.text
    names = get_joined_ids()
    names =  {s.pop(): s.pop() for s in map(set, names)}

    text = sql.execute(f"SELECT Отзыв FROM users WHERE ID = '{names[worker_name]}'")
    text = ''.join(str(x[0] + '\n\n') for x in text.fetchall())
    bot.send_message(message.chat.id, text, reply_markup=mm)

def check_cheating_one(name, master_id):
    return name in get_names() and master_id not in get_masters() or name not in get_names() and master_id in get_masters()


def get_reviews_master_id(message, whataheeeelllomagad):                 # whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad whataheeeelllomagad 
    worker_name = message.text
    master_ids = get_joined_master_ids()
    master_ids =  {s.pop(): s.pop() for s in map(set, master_ids)}
    master_ids = {str(v): k for k, v in master_ids.items()}

    text = sql.execute(f"SELECT Отзыв FROM users WHERE master_id = '{master_ids[worker_name]}'")
    text = ''.join(str(x[0] + '\n\n') for x in text)
    bot.send_message(message.chat.id, text, reply_markup=mm)


bot.polling(none_stop=True)
