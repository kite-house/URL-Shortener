import logging

from aiogram import Router, types
from aiogram.filters import Command

from request import request
router = Router()

@router.message(Command('start'))
async def start(message: types.Message):
    await message.answer('Добро пожаловать в наш сервис!')

@router.message(Command('cutback'))
async def cutback(message: types.Message):
    try:
        url = message.text.split(' ')[1]
    except IndexError:
        return await message.answer('Вы не указали url!')

    response_status_code, response = request.cutback(url)
    if response_status_code == 200:
        return await message.answer(f'Статус: {response['message']} \nКороткий URL: https://backend:8000/api/{response['body']['slug']}')
    elif response_status_code == 208:
        return await message.answer(f'Статус: {response['detail']['message']} \nКороткий URL: https://backend:8000/api/{response['detail']['slug']}')

@router.message(Command('info'))
async def info(message: types.Message):
    await message.answer("Вы хотите получить информацию об ссылке")

@router.message(Command('get'))
async def get(message: types.Message):
    await message.answer('Вы решили получить ссылку!')

@router.message(Command('top'))
async def top(message: types.Message):
    await message.answer('Вы решили получить топ ссылок :)')