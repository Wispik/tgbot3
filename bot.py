from aiogram.utils import executor

from handlers import setup_handlers
from settings import dp
import middleware


def on_startup():
    setup_handlers(dp)


if __name__ == '__main__':
    on_startup()
    dp.middleware.setup(middleware.UserIsAdminMiddleware())

    executor.start_polling(dp)
