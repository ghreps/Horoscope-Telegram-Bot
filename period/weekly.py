from re import sub, search
from os.path import exists
from xml.etree import ElementTree as ET
from logging import Formatter, getLogger, FileHandler

import json
import aiohttp
import datetime

from sqlalchemy import update

from defines import WEEKLY, ZODIACS, SQLALCHEMY_ERROR_SUB, OFFSET, MONTH_RU

from config import Config
from db.database import Database
from db.models import WeeklyModel, TypesModel
from telegram.telegram import send_error_msg


LOG_NAME = "WEEKLY.PY"


class Weekly:
    """
    Функции еженедельного гороскопа:
    Скачивание, парсинг, запись в базу/кэш, обновление
    """
    log = getLogger(LOG_NAME)

    config = None

    def __init__(self, config):
        self.config: Config = config
        self.read_config()

    def read_config(self):
        """Читаем конфиг"""
        formatter = self.config.get('APP', 'formatter').replace('(', '%(')
        file_handler = FileHandler('logs/weekly.log')
        file_handler.setFormatter(Formatter(formatter))

        self.log.addHandler(file_handler)
        self.log.setLevel(self.config.get_int('WEEKLY', 'log_level'))

    async def start(self):
        """Я сказал стартуем"""
        func_name = "START"
        self.log.info(' Start')
        try:
            database = Database()
            sql = database.query(TypesModel).filter_by(file=WEEKLY[0][0]).one_or_none()
            if sql is None:  # if first run
                await self.insert_default_rows(database)  # Fill sql with default data
                xml = await self.download_xml()  # Fill sql with actual data
                await self.parse_xml(xml, database)
            else:
                await self.check_for_relevance(database)
            await self.write_to_cache(database)
        except Exception as error:
            await self.report_error(func_name, error)
        else:
            database.close()
            self.log.debug(' End')

    async def check_for_relevance(self, database: Database, force=False):
        """Проверка локальных гороскопов на актуальность"""
        func_name = "[CHECK FOR REVELANCE] "
        self.log.info('%sStart', func_name)
        is_actual = False
        try:
            
            if not exists('xmls/weekly.xml') or force:
                self.log.info('%sFile not exist, downloading...', func_name)
                xml = await self.download_xml()
                await self.parse_xml(xml, database)
            else:  # Parse stored sql date
                now = datetime.datetime.now(OFFSET)
                sql: WeeklyModel = database.query(WeeklyModel).first()

                day_span= search(' \d+', sql.horo_date)
                day = sql.horo_date[
                    day_span.start():day_span.end()
                ].replace(' ', '')

                month_span = search('[а-яА-Я]*$', sql.horo_date)
                month = MONTH_RU.index(
                    sql.horo_date[month_span.start():].capitalize()
                ) + 1

                sql_date = '{0}{1}{2}'.format(
                    now.year,
                    month,
                    day
                )
                last_date = datetime.datetime.strptime(sql_date, '%Y%m%d').date()
                days_between = now.date() - last_date
                if days_between.days >= -2:  # Check date in local file
                    xml = await self.download_xml()
                    await self.parse_xml(xml, database)
                else:
                    is_actual = True
                    self.log.info('%sData is actual in local file ', func_name)
        except Exception as error:
            raise Exception(func_name + str(error)) from error
        else:
            self.log.debug('%sEnd', func_name)
            return is_actual

    async def download_xml(self):
        """Скачиваем xml с сайта"""
        func_name = "[DOWNLOAD XML] "
        self.log.debug('%sStart', func_name)
        url = 'https://ignio.com/r/export/utf/xml/weekly/cur.xml'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    self.log.info('%sWeekly file cur.xml downloaded', func_name)
                    self.log.debug('%sEnd', func_name)
                    return ET.fromstring(await response.read())
        except Exception as error:
            raise Exception(func_name + str(error)) from error

    async def parse_xml(self, xml: ET.Element, database: Database):
        """Парсим XML и сохраняем в базу"""
        func_name = "[PARSE XML] "
        self.log.debug('%sStart', func_name)
        horo_texts = [[] for i in range(len(ZODIACS))]
        try:  # Parse xml
            date = xml[0].attrib.get('weekly')
            for i, div in enumerate(xml):
                for j in range(len(ZODIACS)):
                    if div.tag in ZODIACS[j]:
                        for horo_day in div:
                            horo_texts[j].append(horo_day.text.replace('\n', ''))
            for horo_id in range(len(WEEKLY)):
                texts = {
                    'horo_date': date,
                    'horo_id': horo_id + 10,
                    'aries': horo_texts[0][horo_id],
                    'taurus': horo_texts[1][horo_id],
                    'gemini': horo_texts[2][horo_id],
                    'cancer': horo_texts[3][horo_id],
                    'leo': horo_texts[4][horo_id],
                    'virgo': horo_texts[5][horo_id],
                    'libra': horo_texts[6][horo_id],
                    'scorpio': horo_texts[7][horo_id],
                    'sagittarius': horo_texts[8][horo_id],
                    'capricorn': horo_texts[9][horo_id],
                    'aquarius': horo_texts[10][horo_id],
                    'pisces': horo_texts[11][horo_id]
                }
                await self.save_to_db(texts, database)
            # Save xml to file
            with open('xmls/weekly.xml', 'wb') as file:
                ET.ElementTree(xml).write(file, encoding='utf-8')
        except Exception as error:
            raise Exception(func_name + str(error)) from error

    async def save_to_db(self, params: dict, database: Database):
        """Сохранение в базу"""
        func_name = "[SAVE TO DB] "
        self.log.debug('%sStart', func_name)
        try:
            sql = update(WeeklyModel).\
                    where(WeeklyModel.horo_id == params['horo_id']).values(params)
            database.execute(sql)
            database.commit()
        except Exception as error:
            raise Exception(func_name + str(error)) from error
        finally:
            self.log.debug('%sEnd', func_name)

    async def update_cache(self):
        """Проверяем на актуальность и обновляем локальный кэш"""
        func_name = "[UPDATE CACHE] "
        self.log.debug('%sStart', func_name)
        try:
            database = Database()
            if not self.check_for_relevance(database, True):
                self.log.info('%sData is not actual, writе to cache...', func_name)
                self.write_to_cache(database)
            else:
                self.log.debug('%sData is actual', func_name)
        except Exception as error:
            await self.report_error(func_name, error)
        finally:
            self.log.debug('%sEnd', func_name)

    async def write_to_cache(self, database: Database):
        """Считываем гороскопы с базы и пишем в кэш"""
        func_name = "[WRITE TO CACHE] "
        self.log.debug('%sStart', func_name)
        json_data = {}
        try:
            for row in database.query(WeeklyModel).all():
                json_data[row.horo_id - 10] = {
                    'horo_id': str(row.horo_id),
                    'date': row.horo_date,
                    'aries': row.aries,
                    'taurus': row.taurus,
                    'gemini': row.gemini,
                    'cancer':  row.cancer,
                    'leo':  row.leo,
                    'virgo':  row.virgo,
                    'libra':  row.libra,
                    'scorpio':  row.scorpio,
                    'sagittarius':  row.sagittarius,
                    'capricorn':  row.capricorn,
                    'aquarius':  row.aquarius,
                    'pisces':  row.pisces
                }
            with open('cache/weekly.json', 'w', encoding='utf-8') as file:
                json.dump(
                    json_data,
                    file,
                    ensure_ascii=False
                )
        except Exception as error:
            raise Exception(func_name + str(error)) from error
        else:
            self.log.info('%sFile cache writed', func_name)
        finally:
            self.log.debug('%sEnd', func_name)

    async def insert_default_rows(self, database: Database):
        """Вставляем пустые строки в базу"""
        func_name = "[INSERT DEFAULT ROWS] "
        self.log.debug('%sStart', func_name)
        try:
            for horo_id, horo in enumerate(WEEKLY):
                sql = TypesModel(horo_id + 10, horo[1].title(), horo[0])
                database.add(sql)
                sql = WeeklyModel(horo_id + 10)
                database.add(sql)
            database.commit()
        except Exception as error:
            raise Exception(func_name + str(error)) from error
        else:
            self.log.info('%sDefault rows inserted to db', func_name)
        finally:
            self.log.debug('%sEnd', func_name)

    async def report_error(self, function: str, error: Exception):
        """Отправляем в телегу ошибку"""
        print(str(error))
        text = '-> %s' % sub(SQLALCHEMY_ERROR_SUB, '', str(error))
        self.log.error(text, exc_info=True)
        await send_error_msg(LOG_NAME, function, text)
