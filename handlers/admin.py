import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext

import db.database as db
from db.models import ChannelModel
from states import AppStates
from settings import bot

import utils
import keyboards as kb


async def create_channel_step1_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    await state.set_state(AppStates.STATE_WAIT_CHANNEL_NUMBER)
    await message.answer('Введите номер канала')


async def create_channel_step2_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    if not message.text.isdigit():
        await message.answer('Номер канала должен быть числом')
        return
    channel = await db.get_channel_by_id(message.text)
    if channel:
        await message.answer(f'Канал ID: {message.text} - уже существует! Введите другой номер канала')
        return
    await state.set_data({'channel_id': int(message.text)})
    await state.set_state(AppStates.STATE_WAIT_CHANNEL_LINK)
    await message.answer('Введите ссылку канала')


async def create_channel_step3_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    await state.update_data({'channel_link': message.text})
    await state.set_state(AppStates.STATE_WAIT_CHANNEL_ID)
    await message.answer('Введите JSON ID канала')


async def create_channel_step4_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return

    _data = await state.get_data()
    await db.create_channel(
        ChannelModel(
            channel_id=_data['channel_id'],
            link = _data['channel_link'],
            tg_id=int(message.text)
        )
    )

    await message.answer(f"Канал {_data['channel_id']} успешно добавлен. Не забудьте сделать бота админом в канале {_data['channel_link']}.")
    await state.reset_data()
    await state.reset_state()


async def edit_channel_step1_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    channel_id = message.text.split('_')[-1]
    channel = await db.get_channel_by_id(channel_id)
    if not channel:
        await message.answer(f"Канал под номером: {channel_id} - не найден!")
        return
    await state.set_data({'channel_id': int(channel_id)})
    await state.set_state(AppStates.STATE_EDIT_CHANNEL_LINK)
    await message.answer('Введите ссылку для привязки к каналу link в формате @username')


async def edit_channel_step2_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    await state.update_data({'link': message.text})
    await state.set_state(AppStates.STATE_EDIT_CHANNEL_BUTTON)
    await message.answer('Введите ссылку для генерации кнопки.')


async def edit_channel_step3_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    _data_state = await state.get_data()
    _data = {
        'btn_link_text': _data_state['link'],
        'btn_link_url': message.text
    }
    await db.update_channel(_data_state['channel_id'], _data)
    await message.answer('Ссылки успешно сохранены ✅')
    await state.reset_data()
    await state.reset_state()


async def send_post_step1_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    await message.answer('Отправьте пост')
    await state.set_state(AppStates.STATE_SEND_POST)


async def send_post_step2_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    data = {
        'text': '',
        'photo': [],
        'video_id': None
    }
    try:
        data['text'] = message.html_text
    except Exception:
        pass
    if message.photo:
        data['photo'] = [p.file_id for p in message.photo]
    elif message.video:
        data.video_id = message.video.file_id
    await state.set_data({'data': data})
    await state.set_state(AppStates.STATE_SEND_POST_BUTTONS)
    await message.answer('Введите название кнопок')


async def send_post_step3_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        return
    channels = await db.get_all_channels()
    _data = await state.get_data()
    for channel in channels:
        try:
            _text = utils.replace_in_message(_data['data']['text'], 'link', channel['btn_link_text'])
            _kb = None
            if channel['btn_link_url']:
                _btns_list = message.text.split(',')
                _btns = list(map(lambda s: {'text': s, 'url': channel['btn_link_url']}, _btns_list))
                _kb = kb.kb_mass_send(_btns)
            if _data['data']['video_id'] or _data['data']['photo']:
                media = types.MediaGroup()
                if _data['data']['photo']:
                    for p in _data['data']['photo']:
                        media.attach_photo(photo=p)
                if _data['data']['video_id']:
                    media.attach_video(_data['data']['video_id'])
                await bot.send_media_group(channel['tg_id'], media=media)
            if _text:
                await bot.send_message(channel['tg_id'], text=_text, reply_markup=_kb, parse_mode=types.ParseMode.HTML)
        except Exception as e:
            print(e)
        await asyncio.sleep(0.5)
    await message.answer('Рассылка успешно завершена ✅')

    await state.reset_data()
    await state.reset_state()
