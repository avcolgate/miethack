from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
import string
import nltk
from nltk.corpus import stopwords
import joblib


def tokenize(x):
    return PredictModel.tokenize_sentence(x, remove_stop_words=True)

class PredictModel:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

    snowball = SnowballStemmer(language="russian")
    russian_stop_words = stopwords.words("russian")

    neg = joblib.load('models/model_neg.joblib')
    pos = joblib.load('models/model_pos.joblib')
    posneg = joblib.load('models/model_nlp_persited_binarka.joblib')

    @classmethod
    def get_neg(cls, text):
        return cls.neg['model'].predict([text])[0]

    @classmethod
    def get_pos(cls, text):
        return cls.pos['model'].predict([text])[0]

    @classmethod
    def get_posneg(cls, text):
        return cls.posneg['model'].predict([text])[0]

    @classmethod
    def get_snowball(cls):
        return cls.snowball

    @classmethod
    def get_stopwords(cls):
        return cls.russian_stop_words

    @classmethod
    def tokenize_sentence(cls, sentence: str, remove_stop_words: bool = True):
        tokens = word_tokenize(sentence, language="russian")
        tokens = [i for i in tokens if i not in string.punctuation]
        if remove_stop_words:
            tokens = [i for i in tokens if i not in cls.get_stopwords()]
        tokens = [cls.get_snowball().stem(i) for i in tokens]
        return tokens


    @staticmethod
    def get_predict(sentense):
        return int(PredictModel.res(PredictModel.get_pos(sentense),
                                    PredictModel.get_neg(sentense),
                                    PredictModel.get_pos(sentense)))

    @staticmethod
    def res(pred_bin_pos, pred_bin_neg, pred_bin_posneg):
        if pred_bin_pos == pred_bin_posneg == 1:
            return 1
        elif pred_bin_neg == pred_bin_posneg == -1:
            return -1
        elif pred_bin_pos == pred_bin_neg == 0:
            return 0
        elif pred_bin_pos == 0 and pred_bin_neg == -1 and pred_bin_posneg == -1:
            return -1
        elif pred_bin_pos == 1 and pred_bin_neg == 0 and pred_bin_posneg == 1:
            return 1
        elif pred_bin_pos == 0 and pred_bin_neg == -1 and pred_bin_posneg == 1:
            return -1
        elif pred_bin_pos == 1 and pred_bin_neg == 0 and pred_bin_posneg == -1:
            return 1

def predict(text):
    return PredictModel.get_predict(text)

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

@bot.message_handler(content_types=['text'])
def handler(message):
    master_id = message.from_user.id
    if message.text == "Написать отзыв":
        bot.send_message(message.chat.id, "Введите ID пользователя, на которого хотите написать отзыв",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "add", master_id)
    elif message.text == "Запросить средние показатели":
        bot.send_message(message.chat.id, "Введите ID пользователя, для которого нужно вывести данные",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "get_avg_id", master_id)
    elif message.text == "Запросить отзывы":
        bot.send_message(message.chat.id, "Введите ID пользователя, для которого нужно вывести данные",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "get_review_id", master_id)
    elif message.text == "Запросить данные по отзывам от пользователя":
        get_reviews_master_id(message)


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



categories = {
    ("Высокий", "Низкий"): ("Неоткрывшийся талант", "Человек, который показывает большие перспективы, но в настоящее время не демонстрирует высокой производительности."),
    ("Высокий", "Средний"): ("Высокий потенциал", "Сотрудник, обладающий способностью расти и улучшать свои результаты."),
    ("Высокий", "Высокий"): ("Звезда", "Лучший сотрудник с большим потенциалом для будущих ролей."),
    ("Средний", "Низкий"): ("Непостоянный сотрудник", "Человек, который иногда соответствует ожиданиям, но не обладает постоянством."),
    ("Средний", "Средний"): ("Стабильный сотрудник", "Надежный сотрудник с стабильной производительностью."),
    ("Средний", "Высокий"): ("Высокая производительность", "Регулярно превосходит ожидания и имеет потенциал для роста."),
    ("Низкий", "Низкий"): ("Требует внимания", "Сотрудник с ограниченным потенциалом и производительностью."),
    ("Низкий", "Средний"): ("Средний исполнитель", "Человек, который часто соответствует базовым требованиям."),
    ("Низкий", "Высокий"): ("Надежный исполнитель", "Превосходно справляется со своей текущей ролью, но не имеет потенциала для будущего роста.")
}


def determine_category(performance, potential):
    performance_level = get_level(performance)
    potential_level = get_level(potential)

    category, description = categories.get((potential_level, performance_level), ("Неизвестно", "Описание неизвестно"))
    return f"{category}: {description}"

def get_level(value):
    if value <= 41.5:
        return "Низкий"
    elif value <= 58.5:
        return "Средний"
    else:
        return "Высокий"


def get_summary(message, worker_id):
    msg = ''
    avg_tone = sql.execute(f"SELECT Avg(Окраска) FROM users WHERE ID = '{worker_id}'")
    msg += 'Мнение о сотруднике: ' + str(round(float(avg_tone.fetchone()[0]) / 2 * 100, 1)) + '%\n'
    avg_productivity = sql.execute(f"SELECT Avg(Производительность) FROM users WHERE ID = '{worker_id}'")
    float_productivity = round(float(avg_productivity.fetchone()[0]) / 3 * 100, 1)
    msg += 'Средняя продуктивость: ' + str(float_productivity) + '%\n'
    avg_potential = sql.execute(f"SELECT Avg(Потенциал) FROM users WHERE ID = '{worker_id}'")
    float_potential = round(float(avg_potential.fetchone()[0]) / 3 * 100, 1)
    msg += 'Средний потенциал: ' + str(float_potential) + '%\n'
    category = determine_category(float_productivity, float_potential)
    msg += category
    bot.send_message(message.chat.id, msg, reply_markup=default_kb)



def get_review_id(message, worker_id):
    text = sql.execute(f"SELECT Отзыв FROM users WHERE ID = '{worker_id}'")
    text = ''.join(str(x[0] + '\n\n') for x in text.fetchall())
    bot.send_message(message.chat.id, text, reply_markup=default_kb)



def get_reviews_master_id(message):
    worker_name = message.text

    text = sql.execute(f"SELECT Отзыв FROM users WHERE master_id = '{message.from_user.id}'")
    text = ''.join(str(x[0] + '\n\n') for x in text)
    bot.send_message(message.chat.id, text, reply_markup=default_kb)


bot.polling(none_stop=True)