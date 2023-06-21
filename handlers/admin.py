import asyncio
from typing import List, Optional

from aiogram import types
from aiogram.dispatcher import FSMContext

import db.database as db
from db.models import ChannelModel
from keyboards.inline import get_channels_buttons
from keyboards.reply import get_admin_menu_buttons
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
    await state.finish()
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


async def edit_channel_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool,
):
    if not is_admin:
        return
    await state.finish()
    await message.answer("Редактировать канал", reply_markup=await get_channels_buttons())


async def edit_channel_handler(
    callback: types.CallbackQuery,
    state: FSMContext
):
    channel_id = int(callback.data.lstrip("channel-"))
    await edit_channel_step1_command(
        callback.message,
        state,
        channel_id
    )
    await callback.answer()


async def edit_channel_step1_command(
    message: types.Message,
    state: FSMContext,
    channel_id: int,
):
    channel = await db.get_channel_by_id(channel_id)
    if not channel:
        await message.answer(f"Канал под номером: {channel_id} - не найден!")
        return
    await state.set_data({'channel_id': int(channel_id)})
    await state.set_state(AppStates.STATE_EDIT_CHANNEL_LINK)
    await message.answer(f"Введите ссылку для привязки к каналу {channel['link']} в формате @username")


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
    await state.finish()
    await message.answer('Отправьте пост')
    await state.set_state(AppStates.STATE_SEND_POST)


async def send_post_step2_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool,
    album: Optional[List[types.Message]] = None,
    one_photo: Optional[types.Message] = None
):
    if not is_admin:
        return
    data = {
        'text': '',
        'media': album
    }
    if one_photo:
        _data = await state.get_data()
        if _data:
            data = _data['data']
        if not data['media']:
            data['media'] = [one_photo]
        else:
            data['media'].append(one_photo)
        await state.set_data({'data': data})
        print(len(data['media']))
        try:
            data['text'] = message.html_text
        except Exception:
            return
    try:
        data['text'] = message.html_text
    except Exception:
        pass
    # if message.photo:
    #     data['photo'] = [p.file_id for p in message.photo]
    # elif message.video:
    #     data.video_id = message.video.file_id

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
                if message.text != '0':
                    _btns_list = message.text.splitlines()
                    _btns = []
                    for btn in _btns_list:
                        _btns_urls = btn.split(" - ")
                        if len(_btns_urls) > 1:
                            btn_text, btn_url = _btns_urls
                            _btns.append({'text': btn_text, 'url': btn_url})
                        else:
                            _btns.append({'text': btn, 'url': channel['btn_link_url']})
                    _kb = kb.kb_mass_send(_btns)

            if _data['data']['media'] and len(_data['data']['media']) == 1:
                mes = _data['data']['media'][0]
                if mes.photo:
                    await bot.send_photo(channel['tg_id'], photo=mes.photo[-1].file_id, caption=_text, reply_markup=_kb, parse_mode=types.ParseMode.HTML)
                elif mes.video:
                    await bot.send_video(channel['tg_id'], video=mes.video.file_id, caption=_text, reply_markup=_kb, parse_mode=types.ParseMode.HTML)
                elif mes.video_note:
                    await bot.send_video_note(channel['tg_id'], video_note=mes.video_note.file_id, reply_markup=_kb)
                elif mes.animation:
                    await bot.send_animation(channel['tg_id'], animation=mes.animation.file_id, caption=_text, reply_markup=_kb, parse_mode=types.ParseMode.HTML)
                elif mes.voice:
                    await bot.send_voice(channel['tg_id'], voice=mes.voice.file_id, duration=mes.voice.duration, caption=_text, reply_markup=_kb, parse_mode=types.ParseMode.HTML)
                elif mes.audio:
                    await bot.send_audio(channel['tg_id'], audio=mes.audio.file_id, duration=mes.audio.duration, caption=_text, reply_markup=_kb, parse_mode=types.ParseMode.HTML)
            elif _data['data']['media']:
                media_group = types.MediaGroup()
                for _i, obj in enumerate(_data['data']['media']):
                    if obj.photo:
                        file_id = obj.photo[-1].file_id
                    else:
                        file_id = obj[obj.content_type].file_id

                    try:
                        # We can also add a caption to each file by specifying `"caption": "text"`
                        
                        if obj.content_type=='animation' or obj.content_type=='video_note':
                            _type = 'video'
                        else:
                            _type = obj.content_type
                        if _i == 0 and _text:
                            media_group.attach(
                                {
                                    "media": file_id, 
                                    "type": _type,
                                    "caption": _text,
                                    "parse_mode": types.ParseMode.HTML,
                                    "reply_markup": _kb
                                }
                            )
                        else:
                            media_group.attach(
                                {
                                    "media": file_id, 
                                    "type": _type
                                }
                            )
                    except ValueError:
                        pass
                await bot.send_media_group(channel['tg_id'], media=media_group)
            else:
                await bot.send_message(channel['tg_id'], text=_text, reply_markup=_kb, parse_mode=types.ParseMode.HTML)
        except Exception as e:
            print(e)
        await asyncio.sleep(0.5)
    await message.answer('Рассылка успешно завершена ✅')

    await state.reset_data()
    await state.reset_state()


async def start_command(
    message: types.Message,
    state: FSMContext,
    is_admin: bool
):
    if not is_admin:
        await message.answer("Привет! Вы не админ.")
        return

    await state.finish()
    await message.answer("Меню:", reply_markup=get_admin_menu_buttons())
