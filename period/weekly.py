from re import sub
from os.path import exists
from xml.etree import ElementTree as ET

import json
import logging
import aiohttp

from sqlalchemy import update

from defines import WEEKLY, ZODIACS, FORMATTER, SQLALCHEMY_ERROR_SUB

from telegram.telegram import send_error_msg
from db.database import Database
from db.models import WeeklyModel, TypesModel


LOG_NAME = "WEEKLY.PY"


class Weekly:
    """
    Функции еженедельного гороскопа:
    Скачивание, парсинг, запись в базу/кэш, обновление
    """
    file_handler = None

    log = logging.getLogger(LOG_NAME)
    log.setLevel(logging.DEBUG)

    database = None

    def __init__(self):
        self.read_config()

    def read_config(self):
        """Читаем конфиг"""
        self.file_handler = logging.FileHandler('logs/weekly.log')
        self.file_handler.setFormatter(FORMATTER)

        self.log.addHandler(self.file_handler)

    async def start(self):
        """Я сказал стартуем"""
        func_name = "START"
        self.log.info(' Start')
        try:
            self.database = Database()
            sql = self.database.query(TypesModel).filter_by(file=WEEKLY[0][0]).one_or_none()
            if sql is None:  # if first run
                await self.insert_default_rows()  # Fill sql with default data
                xml = await self.download_xml()  # Fill sql with actual data
                await self.parse_xml(xml)
            else:
                await self.check_for_relevance()
            await self.write_to_cache()
        except Exception as error:
            await self.report_error(func_name, error)

    async def check_for_relevance(self, force=False):
        """Проверка локальных гороскопов на актуальность"""
        func_name = "[CHECK FOR REVELANCE] "
        self.log.info('%sStart', func_name)
        is_actual = False
        try:
            if not exists('xmls/weekly.xml') or force:
                self.log.info('%sFile not exist, downloading...', func_name)
                xml = await self.download_xml()
                await self.parse_xml(xml)
            else:  # Parse local xml
                body = ET.parse('xmls/weekly.xml').getroot()
                last_date = body[0].attrib.get('weekly')
                sql: WeeklyModel = self.database.query(WeeklyModel).first()
                if last_date != sql.horo_date:  # Check date in local file
                    xml = await self.download_xml()
                    if last_date == xml[0].attrib.get('weekly'):  # If same date
                        is_actual = True
                    else:
                        await self.parse_xml(xml)
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
                    if response.status == 200:
                        self.log.info('%sWeekly file cur.xml downloaded', func_name)
                        self.log.debug('%sEnd', func_name)
                        return ET.fromstring(await response.read())
                    else:
                        response.raise_for_status()
        except Exception as error:
            raise Exception(func_name + str(error)) from error

    async def parse_xml(self, xml: ET.Element):
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
                await self.save_to_db(texts)
            # Save xml to file
            with open('xmls/weekly.xml', 'wb') as file:
                ET.ElementTree(xml).write(file, encoding='utf-8')
        except Exception as error:
            raise Exception(func_name + str(error)) from error

    async def save_to_db(self, params: dict):
        """Сохранение в базу"""
        func_name = "[SAVE TO DB] "
        self.log.debug('%sStart', func_name)
        try:
            sql = update(WeeklyModel).\
                    where(WeeklyModel.horo_id == params['horo_id']).values(params)
            self.database.execute(sql)
            self.database.commit()
        except Exception as error:
            raise Exception(func_name + str(error)) from error
        finally:
            self.log.debug('%sEnd', func_name)

    async def update_cache(self):
        """Проверяем на актуальность и обновляем локальный кэш"""
        func_name = "[UPDATE CACHE] "
        self.log.debug('%sStart', func_name)
        try:
            if not self.check_for_relevance(True):
                self.log.info('%sData is not actual, writе to cache...', func_name)
                self.write_to_cache()
            else:
                self.log.debug('%sData is actual', func_name)
        except Exception as error:
            await self.report_error(func_name, error)
        finally:
            self.log.debug('%sEnd', func_name)

    async def write_to_cache(self):
        """Считываем гороскопы с базы и пишем в кэш"""
        func_name = "[WRITE TO CACHE] "
        self.log.debug('%sStart', func_name)
        json_data = {}
        weekly = [[] for i in range(len(WEEKLY))]
        try:
            for row in self.database.query(WeeklyModel).all():
                weekly[row.horo_id - 10] = {
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

    async def insert_default_rows(self):
        """Вставляем пустые строки в базу"""
        func_name = "[INSERT DEFAULT ROWS] "
        self.log.debug('%sStart', func_name)
        try:
            for horo_id, horo in enumerate(WEEKLY):
                sql = TypesModel(horo_id + 10, horo[1].title(), horo[0])
                self.database.add(sql)
                sql = WeeklyModel(horo_id + 10)
                self.database.add(sql)
            self.database.commit()
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
