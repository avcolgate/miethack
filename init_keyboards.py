from telebot import types

def default_keyboard():
    mm = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton("Написать отзыв")
    button2 = types.KeyboardButton("Запросить отзывы")
    button3 = types.KeyboardButton("Запросить средние показатели")
    button4 = types.KeyboardButton("Запросить данные по отзывам от пользователя")
    mm.add(button1, button2, button3, button4)
    return mm

def create_rating():
    rating = types.ReplyKeyboardMarkup(row_width=3)

    lower_than_average = types.KeyboardButton('Ниже среднего')
    average = types.KeyboardButton('Средняя')
    greater_than_average = types.KeyboardButton('Выше среднего')
    rating.add(lower_than_average)
    rating.add(average)
    rating.add(greater_than_average)
    return rating