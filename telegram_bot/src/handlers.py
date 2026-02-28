from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command('start'))
async def start(message: types.Message):
    await message.answer('Добро пожаловать в наш сервис!')

@router.message(Command('cutback'))
async def cutback(message: types.Message):
    await message.answer('Вы решили сократить ссылку :)')

@router.message(Command('info'))
async def info(message: types.Message):
    await message.answer("Вы хотите получить информацию об ссылке")

@router.message(Command('get'))
async def get(message: types.Message):
    await message.answer('Вы решили получить ссылку!')

@router.message(Command('top'))
async def top(message: types.Message):
    await message.answer('Вы решили получить топ ссылок :)')