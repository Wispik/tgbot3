from aiogram.types import  InlineKeyboardButton, InlineKeyboardMarkup


def kb_mass_send(buttons):
    kb = InlineKeyboardMarkup(row_width=1)
    
    for btn in buttons:
        kb.add(
            InlineKeyboardButton(btn['text'], url=btn['url'])
        )

    return kb