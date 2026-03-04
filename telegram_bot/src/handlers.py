import logging
from datetime import datetime

from aiogram import Router, types, F
from aiogram.filters import Command 
from aiogram.utils.formatting import Bold, as_list, as_marked_section, as_key_value, TextLink, Italic

from request import request
router = Router()

@router.message(Command('start'))
async def start(message: types.Message):
    await message.answer('Добро пожаловать в наш сервис!')


@router.message(Command('shorten'))
async def shorten(message: types.Message):
    try:
        url = message.text.split(' ')[1]
    except IndexError:
        return await message.answer('Вы не указали url!')

    response = request.shorten(url)

    content = as_list(
        Bold(f"✅ {response['message']}"),
        Bold("📌 Ваша ссылка:"),
        TextLink("👉 Нажмите чтобы перейти", url=f"http://127.0.0.1:8000/api/{response['body']['slug']}"),
        Bold("📎 Оригинал:"),
        f"👉 {response['body']['long_url'][:50]}{'...' if len(response['body']['long_url']) > 50 else ''}",
        Italic("⚡️ Ссылка готова к использованию!"),
        sep='\n\n'
    )
        
    return await message.answer(**content.as_kwargs())

@router.message(Command('info'))
async def info(message: types.Message):
    try: 
        url = message.text.split(' ')[1]
    except IndexError:
        return await message.answer("Вы не указали url!")
    
    response = request.info(url)

    date_created = response["body"]["date_created"]
    if date_created != "-":
        date_created = datetime.fromisoformat(date_created)
        date_created = datetime.strftime(date_created, "%d.%m.%Y")

    content = as_list(
        Bold(f"{response["message"]}"),
            as_key_value("Короткий url", f"http://127.0.0.1:8000/api/{response["body"]["slug"]}"),
            as_key_value("Длинный url", response["body"]["long_url"]),
            as_key_value("Количество переходов", response["body"]["count_clicks"]),
            as_key_value("Дата создания", date_created),
        sep="\n"
    )

    await message.answer(**content.as_kwargs())

@router.message(Command('get'))
async def get(message: types.Message):
    await message.answer('Вы решили получить ссылку!')

@router.message(Command('top'))
async def top(message: types.Message):
    await message.answer('Вы решили получить топ ссылок :)')

