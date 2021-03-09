import asyncio
import datetime

from concurrent.futures import ProcessPoolExecutor

from period.daily import Daily
from period.weekly import Weekly

from config import Config

from telegram.telegram import telegram_start
from defines import OFFSET
from announce import Announce

async def db_update(config):
    while True:
        now = datetime.datetime.now(OFFSET)
        if now.strftime("%H:%M") == '23:30':  # Daily update time
            print('Time is 23:30, updating...')
            await Daily(config).update_cache()
        elif now.strftime("%H:%M") == '04:30' and now.weekday() == 4:  # Weekly update time
            await Weekly(config).update_cache()
        await asyncio.sleep(60)

def db_update_loop(config):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(db_update(config))


def announce_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(Announce().start())

async def start(config):
    await Daily(config).start()
    await Weekly(config).start()

if __name__ == '__main__':
    config = Config()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start(config))
    
    executor = ProcessPoolExecutor(2)
    asyncio.get_event_loop().run_in_executor(executor, db_update_loop, config)
    asyncio.get_event_loop().run_in_executor(executor, announce_loop)
    telegram_start()
