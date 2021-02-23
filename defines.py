from logging import Formatter
from datetime import timezone, timedelta

FORMATTER = Formatter('[%(asctime)s][%(levelname)s][%(name)s]%(message)s')
SQLALCHEMY_ERROR_SUB = r'(\n\(Background on this error at)(.*)'
OFFSET = timezone(timedelta(hours=3))

DAILY = [
    ['daily_common', 'com.xml', 'обычный', 'обыч'],
    ['daily_love', 'lov.xml', 'любовный', 'люб', 'лав'],
    ['daily_business', 'bus.xml', 'бизнес', 'биз'],
    ['daily_cooking', 'cook.xml', 'кулинарный', 'кул'],
    ['daily_health', 'hea.xml', 'здоровья', 'здоровья', 'здор'],
    ['daily_erotic', 'ero.xml', 'эротический', 'эротик', 'эро'],
    ['daily_anti', 'anti.xml', 'анти'],
    ['daily_mobile', 'mob.xml', 'мобильный', 'моб']
]

WEEKLY = [
    ['weekly_business', 'бизнес'],
    ['weekly_common', 'общий'],
    ['weekly_love', 'любовный'],
    ['weekly_health', ' здоровья'],
    ['weekly_car', 'автомобильный'],
    ['weekly_beauty', ' красоты'],
    ['weekly_erotic', 'эротический'],
    ['weekly_gold', 'ювелирный']
]

ZODIACS = [
    ['aries', 'Овен', '21 марта — 19 апреля'],
    ['taurus', 'Телец', '20 апреля — 20 мая'],
    ['gemini', 'Близнецы', '21 мая — 20 июня'],
    ['cancer', 'Рак', '21 июня — 22 июля'],
    ['leo', 'Лев', '23 июля — 22 августа'],
    ['virgo', 'Дева', '23 августа — 22 сентября'],
    ['libra', 'Весы', '23 сентября — 22 октября'],
    ['scorpio', 'Скорпион', '23 октября — 21 ноября'],
    ['sagittarius', 'Стрелец', '22 ноября — 21 декабря'],
    ['capricorn', 'Козерог', '22 декабря — 19 января'],
    ['aquarius', 'Водолей', '20 января — 18 февраля'],
    ['pisces', 'Рыбы', '19 февраля — 20 марта']
]

MONTH_RU = [
    'Января',
    'Февраля',
    'Марта',
    'Апреля',
    'Мая',
    'Июня',
    'Июля',
    'Августа',
    'Сентября',
    'Октября',
    'Ноября',
    'Декабря'
]
