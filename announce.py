from datetime import datetime

import json
import asyncio
import logging

import emoji

from aiogram.utils.markdown import escape_md, italic as italic_md, bold as bold_md

from defines import ZODIACS, MONTH_RU, OFFSET, FORMATTER

from telegram.telegram import send_msg, send_error_msg

LOG_NAME = "ANNOUNCE.PY"


class Announce():
    """Анонс ежедневного горосокпа в канал"""
    file_handler = None

    log = logging.getLogger(LOG_NAME)
    log.setLevel(logging.DEBUG)

    def __init__(self):
        self.read_config()

    def read_config(self):
        """Читаем конфиг"""
        self.file_handler = logging.FileHandler('logs/announce.log')
        self.file_handler.setFormatter(FORMATTER)

        self.log.addHandler(self.file_handler)

    async def start(self):
        """Запуск таймера анонса в телеграм"""
        func_name = "[ANNOUNCE] "
        self.log.debug('%sStart', func_name)
        try:
            while True:
                now = datetime.now(OFFSET)
                if now.strftime("%H:%M") == '01:00':
                    self.log.info('%sTime to announce', func_name)
                    msg = await self.parse_cache()
                    await send_msg(''.join(msg))
                await asyncio.sleep(60)
        except Exception as error:
            await self.report_error(func_name, error)

    async def parse_cache(self):
        """Парсим кэш"""
        func_name = "[PARSE CACHE] "
        self.log.debug('%sStart', func_name)
        text = []
        try:
            json_text = ''
            with open('cache/daily.json', 'r', encoding='utf-8') as file:
                json_text = json.load(file)
            # Date
            date = datetime.strptime(json_text[str(2)]['date'], '%d.%m.%Y')
            text.append(bold_md(
                'Ежедневный гороскоп на сегодня ({0} {1}, {2})\n\n'.format(
                    date.strftime('%d'),
                    MONTH_RU[date.month],
                    date.strftime('%A')
            )))
            # Zodiacs
            for zodiac in ZODIACS:
                horo_emoji = zodiac[0]
                if zodiac[0] == 'scorpio':
                    horo_emoji = 'scorpius'
                text.append(emoji.emojize(
                    ':{0}: {1} \\({2}\\) :{0}:\n{3}\n\n'.format(
                        horo_emoji,
                        zodiac[1],
                        italic_md(zodiac[2]),
                        escape_md(json_text[str(2)][zodiac[0]])
                    ), use_aliases=True
                ))
            self.log.debug('%sEnd', func_name)
            return text
        except Exception as error:
            raise Exception(func_name + str(error)) from error

    async def report_error(self, function: str, error: Exception):
        """Отправляем в телегу ошибку"""
        print(str(error))
        self.log.error(str(error), exc_info=True)
        await send_error_msg(LOG_NAME, function, str(error))
