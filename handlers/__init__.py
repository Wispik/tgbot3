from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text

import handlers.admin as h_admin

from states import AppStates


def setup_handlers(dp: Dispatcher):
    dp.register_message_handler(h_admin.create_channel_step1_command, commands=['add_channel'])
    dp.register_message_handler(h_admin.create_channel_step2_command, state=[AppStates.STATE_WAIT_CHANNEL_NUMBER])
    dp.register_message_handler(h_admin.create_channel_step3_command, state=[AppStates.STATE_WAIT_CHANNEL_LINK])
    dp.register_message_handler(h_admin.create_channel_step4_command, state=[AppStates.STATE_WAIT_CHANNEL_ID])

    dp.register_message_handler(h_admin.edit_channel_step1_command, Text(startswith='/edit_link_'))
    dp.register_message_handler(h_admin.edit_channel_step2_command, state=[AppStates.STATE_EDIT_CHANNEL_LINK])
    dp.register_message_handler(h_admin.edit_channel_step3_command, state=[AppStates.STATE_EDIT_CHANNEL_BUTTON])

    dp.register_message_handler(h_admin.send_post_step1_command, commands=['send_post'])
    dp.register_message_handler(h_admin.send_post_step2_command, content_types=['text', 'photo', 'video', 'video_note', 'animation'], state=[AppStates.STATE_SEND_POST])
    dp.register_message_handler(h_admin.send_post_step3_command, state=[AppStates.STATE_SEND_POST_BUTTONS])