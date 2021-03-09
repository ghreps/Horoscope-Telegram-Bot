from aiogram.types import InlineKeyboardButton as Button
from aiogram.utils.callback_data import CallbackData
from aiogram import types

cb = CallbackData('post','params','action')  # post:<id>:<action>

weekly_menu = [
    Button('Обычный', callback_data=cb.new('common', action='get_weekly')),
    Button('Бизнес', callback_data=cb.new('business', action='get_weekly')),
    Button('Любовный', callback_data=cb.new('love', action='get_weekly')),
    Button('Здоровья', callback_data=cb.new('health', action='get_weekly')),
    Button('Автомобильный', callback_data=cb.new('car', action='get_weekly')),
    Button('Красоты', callback_data=cb.new('beauty', action='get_weekly')),
    Button('Эротический', callback_data=cb.new('erotic', action='get_weekly')),
    Button('Ювелирный', callback_data=cb.new('gold', action='get_weekly')),
]

def daily_types_btns(day):
    return [
        Button('Обычный', callback_data=cb.new(day+',common', action='get_daily')),
        Button('Любовный', callback_data=cb.new(day+',love', action='get_daily')),
        Button('Бизнес', callback_data=cb.new(day+',business', action='get_daily')),
        Button('Кулинарный', callback_data=cb.new(day+',cooking', action='get_daily')),
        Button('Здоровья', callback_data=cb.new(day+',health', action='get_daily')),
        Button('Эротический', callback_data=cb.new(day+',erotic', action='get_daily')),
        Button('Антигороскоп', callback_data=cb.new(day+',anti', action='get_daily')),
        Button('Мобильный', callback_data=cb.new(day+',mobile', action='get_daily'))
    ]

personal_settings_menu = [
    Button('Выбрать знак зодиака', callback_data=cb.new('common', action='get_weekly')),
]

pick_zodiac_menu = [
    Button('Обычный', callback_data=cb.new('common', action='get_weekly')),
    Button('Бизнес', callback_data=cb.new('business', action='get_weekly')),
    Button('Любовный', callback_data=cb.new('love', action='get_weekly')),
    Button('Здоровья', callback_data=cb.new('health', action='get_weekly')),
    Button('Автомобильный', callback_data=cb.new('car', action='get_weekly')),
    Button('Красоты', callback_data=cb.new('beauty', action='get_weekly')),
    Button('Эротический', callback_data=cb.new('erotic', action='get_weekly')),
    Button('Ювелирный', callback_data=cb.new('gold', action='get_weekly')),
]

# Главное меню
main_menu_btns = [
    Button('Гороскоп на сегодня', callback_data=cb.new('1,common', action='get_daily')),
    Button('Гороскоп на завтра', callback_data=cb.new('2,common', action='get_daily')),
    Button('Ежедневные гороскопы', callback_data=cb.new([], action='daily_menu')),
    Button('Еженедельные гороскопы', callback_data=cb.new([], action='weekly_menu')),
    Button('Мои гороскопы', callback_data=cb.new([], action='my_horoscopes')),
    Button('Подписка', callback_data=cb.new([], action='subscribe'))
]
main_menu = types.InlineKeyboardMarkup(row_width=1)
main_menu.add(*main_menu_btns)

#  Ежедневные гороскопы
daily_menu_btns = [
    Button('Сегодня', callback_data=cb.new('1', action='daily_submenu')),
    Button('Завтра', callback_data=cb.new('2', action='daily_submenu')),
    Button('Послезавтра', callback_data=cb.new('3', action='daily_submenu'))
]
daily_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
daily_menu = types.InlineKeyboardMarkup(row_width=2)
daily_menu.add(*daily_menu_btns)

#  Мои настройки
personal_daily_menu_btns = [
    Button('Сегодня', callback_data=cb.new('1', action='daily_personal')),
    Button('Завтра', callback_data=cb.new('2', action='daily_personal')),
    Button('Послезавтра', callback_data=cb.new('3', action='daily_personal'))
]
personal_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
personal_menu = types.InlineKeyboardMarkup(row_width=3)
personal_menu.row(Button('Ежедневные гороскопы на...', callback_data='#'))
personal_menu.row(*personal_daily_menu_btns)
personal_menu.row(Button('Еженедельные гороскопы', callback_data='#'))
personal_menu.row(Button('Настройки', callback_data=cb.new(' ', action='personal_settings')))