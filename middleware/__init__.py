from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

import db.database as db


class UserIsAdminMiddleware(BaseMiddleware):
    '''
    Проверяем, админ ли юзер
    '''

    def __init__(self):
        super(UserIsAdminMiddleware, self).__init__()
    
    async def on_process_message(self, message: types.Message, data: dict):
        data['is_admin'] = False
        admin = await db.get_admin_by_tg_id(message.from_user.id)
        if admin:
            data['is_admin'] = True
        return
