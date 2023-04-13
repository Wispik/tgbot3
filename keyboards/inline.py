from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db.database import get_all_channels


async def get_channels_buttons():
    markup = InlineKeyboardMarkup()
    channels = await get_all_channels()
    if not channels:
        print(channels)
        return
    buttons = []
    for channel in channels:
        buttons.append(
            InlineKeyboardButton(
                channel["channel_id"],
                callback_data="channel-" + str(channel["channel_id"]),
            )
        )
    markup.add(*buttons)
    return markup
