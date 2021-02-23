from os.path import exists
from os import mkdir

import asyncio
import datetime

from concurrent.futures import ProcessPoolExecutor

from period.daily import Daily
from period.weekly import Weekly

from telegram.telegram import telegram_start

from announce import Announce


async def db_update():
    daily = Daily()
    weekly = Weekly()
    await daily.start()
    await weekly.start()
    offset = datetime.timezone(datetime.timedelta(hours=3))
    while True:
        now = datetime.datetime.now(offset)
        if now.strftime("%H:%M") == '23:30':  # Daily update time
            print('Time is 23:30, updating...')
            await daily.update_cache()
        elif now.strftime("%H:%M") == '04:30' and now.weekday() == 4:  # Weekly update time
            weekly.update_cache()
        await asyncio.sleep(60)


def db_update_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(db_update())


def announce_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(Announce().start())

if __name__ == '__main__':
    if not exists('logs'):
        mkdir('logs')
    if not exists('cache'):
        mkdir('cache')
    if not exists('xmls'):
        mkdir('xmls')
    executor = ProcessPoolExecutor(2)
    asyncio.get_event_loop().run_in_executor(executor, db_update_loop)
    asyncio.get_event_loop().run_in_executor(executor, announce_loop)
    telegram_start()
