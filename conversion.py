def text_to_rating(text: str):
    if text == 'Ниже среднего':
        return 1
    if text == 'Средняя':
        return 2
    if text == 'Выше среднего':
        return 3