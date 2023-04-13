from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_admin_menu_buttons():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    add_channel = KeyboardButton("Подключить канал")
    send_post = KeyboardButton("Отправить сообщение")
    edit_link = KeyboardButton("Изменить ссылку")
    markup.add(add_channel)
    markup.add(send_post)
    markup.add(edit_link)
    return markup
