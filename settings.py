from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from motor.motor_asyncio import (AsyncIOMotorClient, AsyncIOMotorDatabase)


TOKEN=''

MONGO_DB = 'channels'
MONGO_URI = f'mongodb://localhost:27017'


COLLECTION_ADMIN = 'admins'
COLLECTION_CHANNELS = 'channels'


def _connect_to_db() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    return db


db_connection = _connect_to_db()


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())