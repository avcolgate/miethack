import telebot
from telebot import types
import sqlite3

db = sqlite3.connect('users.db', check_same_thread=False)
sql = db.cursor()

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
mm.add(button1, button2)

# Переместил Ваши кнопки и клавиатуры отдельно от кода.
rating = types.InlineKeyboardMarkup(row_width=5)
one = types.InlineKeyboardButton(text='1', callback_data=1)
two = types.InlineKeyboardButton(text='2', callback_data=2)
three = types.InlineKeyboardButton(text='3', callback_data=3)
four = types.InlineKeyboardButton(text='4', callback_data=4)
five = types.InlineKeyboardButton(text='5', callback_data=5)
rating.add(one)
rating.add(two)
rating.add(three)
rating.add(four)
rating.add(five)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Что будем делать?", reply_markup=mm)


@bot.message_handler(content_types=['text'])
def handler(message):
    if message.text == "Написать отзыв":
        bot.send_message(message.chat.id, "Введите ID пользователя, на которого хотите написать отзыв",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "add")

    if message.text == "Запросить данные по ID":
        bot.send_message(message.chat.id, "Введите ID пользователя, для которого нужно вывести данные",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, collect_id, "get")


def collect_id(message, mode):
    worker_id = message.text
    if mode == "add":
        bot.send_message(message.chat.id, f"Введите отзыв на сотрудника {worker_id}", reply_markup=rating)
        bot.register_next_step_handler(message, add_review_to_db, worker_id)
    elif mode == "get":
        get_summary(message, worker_id)


def add_review_to_db(message, worker_id):
    text = message.text
    print(worker_id, text)
    sql.execute(f"INSERT INTO users VALUES(?,?,?,?,?)", (worker_id, text, 1, 2, 3))
    db.commit()
    bot.send_message(message.chat.id, f"Отзыв на сотрудника {worker_id} добавлен!", reply_markup=mm)


def get_summary(message, worker_id):
    for review in sql.execute(f"SELECT Отзыв FROM users WHERE ID = '{worker_id}'"):
        bot.send_message(message.chat.id, review, reply_markup=mm)


bot.polling(none_stop=True)