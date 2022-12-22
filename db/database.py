from settings import db_connection, COLLECTION_CHANNELS, COLLECTION_ADMIN
from db.models import ChannelModel


async def get_admin_by_tg_id(tg_id: int):
    col = db_connection[COLLECTION_ADMIN]
    return await col.find_one(filter={'tg_id': tg_id})


async def get_channel_by_id(channel_id):
    col = db_connection[COLLECTION_CHANNELS]
    return await col.find_one(filter={'channel_id': int(channel_id)})


async def get_all_channels():
    col = db_connection[COLLECTION_CHANNELS]
    return await col.find({}).to_list(9999)


async def create_channel(channel: ChannelModel):
    col = db_connection[COLLECTION_CHANNELS]
    await col.insert_one(channel.dict())


async def update_channel(channel_id: int, data: dict):
    col = db_connection[COLLECTION_CHANNELS]
    await col.find_one_and_update(
        {'channel_id': channel_id}, {'$set': data}
    )
