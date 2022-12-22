from aiogram.utils.helper import Helper, HelperMode, Item


class AppStates(Helper):
    mode = HelperMode.snake_case

    STATE_WAIT_CHANNEL_NUMBER = Item()
    STATE_WAIT_CHANNEL_LINK = Item()
    STATE_WAIT_CHANNEL_ID = Item()
    STATE_EDIT_CHANNEL_LINK = Item()
    STATE_EDIT_CHANNEL_BUTTON = Item()
    STATE_SEND_POST = Item()
    STATE_SEND_POST_BUTTONS = Item()