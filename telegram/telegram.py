import logging
import locale
import typing
import emoji
import json

from datetime import datetime

from aiogram import Bot, types
from aiogram.types import ParseMode
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.markdown import escape_md, bold as bold_md, text as text_md
from aiogram.utils.callback_data import CallbackData

from defines import ZODIACS, MONTH_RU, DAILY

from config import Config

from .buttons import *

DAY_TEXT = [
    'вчера',
    'сегодня',
    'завтра',
    'послезавтра'
]

locale.setlocale(locale.LC_ALL, ('ru_RU', 'utf-8'))

config = Config()

CHANNEL_ID = config.get_int('TELEGRAM', 'channel_id')
ADMIN_ID = config.get_int('TELEGRAM', 'admin_id')
TOKEN = config.get('TELEGRAM', 'token')

bot = Bot(token=TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
dp = Dispatcher(bot)

async def send_msg(msg):
    try:
        await bot.send_message(CHANNEL_ID, msg)
    except Exception as error:
        print(error)

async def send_error_msg(file, function, msg):
    print(file, function)
    text = '`[{0}][{1}] {2}`'.format(
        file, function, escape_md(msg)
    )
    try:
        await bot.send_message(ADMIN_ID, text)
    except Exception as error:
        print(error)

@dp.message_handler(commands=['start'])
async def call_start_command(message: types.Message):
    await message.answer(
        'Приветствую\\! Алалала тут будет текст приветствия',
        reply_markup=main_menu
    )

# Главное -> Ежедневные гороскопы
@dp.callback_query_handler(cb.filter(action='daily_menu'))
async def call_daily_menu(call: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    await bot.send_message(
        call.from_user.id,
        escape_md('Ежедневный гороскоп на...'),
        reply_markup=daily_menu
    )

# Главное -> Ежедневные гороскопы -> сегодня/завтра/послезавтра
@dp.callback_query_handler(cb.filter(action='daily_submenu'))
async def call_daily_submenu(call: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*daily_types_btns(callback_data['params']))
    msg = 'Гороскоп на {0}...'.format(DAY_TEXT[int(callback_data['params'])])
    await bot.send_message(
        call.from_user.id,
        escape_md(msg),
        reply_markup=keyboard
    )

@dp.callback_query_handler(cb.filter(action='get_daily'))
async def call_query_view(call: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    msg = ''
    params = callback_data['params'].split(',')
    with open('cache/daily.json', 'r', encoding='utf-8') as f:
            msg = parse_daily(f, params)
    await bot.send_message(
        call.from_user.id,
        ''.join(msg),
        reply_markup=main_menu
    )

@dp.callback_query_handler(cb.filter(action='weekly_menu'))
async def call_weekly_menu(call: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    await bot.send_message(
        call.from_user.id,
        'Будет позже'
    )

@dp.callback_query_handler(cb.filter(action='subscribe'))
async def call_subscribe_menu(call: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    await bot.send_message(
        call.from_user.id,
        'Будет позже'
    )


def parse_daily(file, params):
    text = []
    json_text = json.load(file)
    # Get horo_id
    horo_id = ''
    for i, row in enumerate(DAILY):
        if row[0] == 'daily_'+params[1]:
            horo_id = str(i+1)
    day = int(params[0])
    for foo, root_value in json_text.items():
        if root_value['horo_id'] == horo_id:
            if root_value['day'] == str(day):
                # Date
                date = datetime.strptime(root_value['date'], '%d.%m.%Y')
                msg_date = '({0} {1}, {2})'.format(
                    date.strftime('%d'),
                    MONTH_RU[date.month],
                    date.strftime('%A')
                )
                text.append(
                    bold_md(
                        'Ежедневный {0} гороскоп на {1} {2}'.format(
                        DAILY[int(horo_id)-1][2],
                        DAY_TEXT[day],
                        msg_date
                    )) + '\n\n'
                )
                # Zodiacs
                for zodiac in ZODIACS:
                    horo_emoji = zodiac[0]
                    if zodiac[0] == 'scorpio':
                        horo_emoji = 'scorpius'
                    text.append(emoji.emojize(
                        ':{0}: {1} :{0}:\n{2}\n\n'.format(
                            horo_emoji,
                            zodiac[1],
                            escape_md(root_value[zodiac[0]])
                        ), use_aliases=True
                    ))
    return text

def telegram_start():
    executor.start_polling(dp)