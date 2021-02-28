from logging import Formatter, getLogger, FileHandler
from xml.etree import ElementTree as ET
from multiprocessing import Pool
from datetime import datetime
from os.path import exists
from os import listdir
from json import dump
from re import sub

from requests import get as http_get
from sqlalchemy import update

from config import Config
from db.database import Database
from db.models import DailyModel, TypesModel

from telegram.telegram import send_error_msg

from defines import DAILY, ZODIACS, SQLALCHEMY_ERROR_SUB, OFFSET

LOG_NAME = "DAILY.PY"


class Daily:
    """
    Функции ежедневного гороскопа:
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
        file_handler = FileHandler('logs/daily.log')
        file_handler.setFormatter(Formatter(formatter))

        self.log.addHandler(file_handler)
        self.log.setLevel(self.config.get_int('DAILY', 'log_level'))

    async def start(self):
        """Я сказал стартуем"""
        func_name = "[START] "
        self.log.info('%sStart', func_name)
        try:
            database = Database()
            sql = database.session.query(TypesModel).\
                filter_by(file=DAILY[0][0]).one_or_none()
            if sql is None:  # if first run
                self.log.info(' First run detected - db is empty')
                await self.insert_default_rows(database)  # Fill sql with default data
                #
                with Pool(len(DAILY)) as pool:
                    result = pool.map_async(download_and_parse, range(len(DAILY)))
                    print(result)
                    print(result.get())
                    for horo_id, fail in enumerate(result.get()):
                        if fail:
                            await self.report_error(func_name, fail)
                        else:
                            self.log.info(
                                '%sFile %s downloaded and parsed',
                                func_name,
                                DAILY[horo_id][0]
                            )
            else:
                await self.check_for_relevance()
            await self.write_to_cache(database)
        except Exception as error:
            await self.report_error(func_name, error)
        else:
            database.close()
            self.log.debug('%sEnd', func_name)

    async def check_for_relevance(self, force=False):
        """Проверка ежедневных гороскопов на актуальность"""
        func_name = "[CHECK FOR REVELANCE] "
        self.log.info('%sStart', func_name)
        is_actual = False
        try:
            now = datetime.now(OFFSET).strftime("%d.%m.%Y")
            if len(listdir('xmls')) == 0:  # If no files - download all
                with Pool(len(DAILY)) as pool:
                    result = pool.map_async(download_and_parse, range(len(DAILY)))
                    for horo_id, fail in enumerate(result.get()):
                        if fail:
                            await self.report_error(func_name, fail)
                        else:
                            self.log.info(
                                '%sFile %s downloaded and parsed',
                                func_name,
                                DAILY[horo_id][0]
                            )
            else:  # if at least one file exists
                for horo_id in range(len(DAILY)):
                    file = 'xmls/%s.xml' % DAILY[horo_id][0]
                    need_download = False
                    if not exists(file) or force:
                        need_download = True
                    else:
                        body = ET.parse(file).getroot()  # Parse local xml
                        if body[0].attrib.get('today') != now:
                            need_download = True
                    if need_download:
                        self.log.info('%sDownloading %s...', func_name, file)
                        with Pool(1) as pool:
                            fail = pool.apply_async(download_and_parse, [horo_id])
                            if fail.get():
                                await self.report_error(func_name, fail.get())
                            else:
                                self.log.info(
                                    '%sFile %s downloaded and parsed',
                                    func_name,
                                    file
                                )
                    else:
                        is_actual = True
                        self.log.info('%sData is actual in file %s', func_name, file)
        except Exception as error:
            raise Exception(func_name + str(error)) from error
        else:
            self.log.debug('%sEnd', func_name)
            return is_actual

    async def update_cache(self):
        """Проверяем на актуальность и обновляем локальный кэш"""
        func_name = "[UPDATE CACHE] "
        self.log.debug('%sStart', func_name)
        try:
            database = Database()
            if not await self.check_for_relevance(True):
                self.log.info('%sData is not actual...', func_name)
                await self.write_to_cache(database)
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
            for row in database.query(DailyModel).all():
                json_data[row.id] = {
                    'horo_id': str(row.horo_id),
                    'day': str(row.horo_day),
                    'date': row.horo_date.strftime('%d.%m.%Y'),
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
            with open('cache/daily.json', 'w', encoding='utf-8') as file:
                dump(
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
            for horo_id, horo in enumerate(DAILY):
                sql = TypesModel(horo_id + 1, horo[2].title(), horo[0])
                database.add(sql)
                for horo_day in range(4):
                    sql = DailyModel(horo_id + 1, horo_day)
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
        print(function, str(error))
        text = '{0} -> {1}'.format(
            function,
            sub(SQLALCHEMY_ERROR_SUB, '', str(error))
        )
        self.log.error(text, exc_info=True)
        await send_error_msg(LOG_NAME, function, text)


def download_and_parse(horo_id):
    """Скачивание и парсинг XML"""
    try:
        xml = download(horo_id)
        return parse(horo_id, xml)
    except Exception as error:
        print('---')
        print(error)
        return str(error)


def download(horo_id):
    """Скачиваем xml с сайта"""
    func_name = "[DOWNLOAD] "
    url = 'https://ignio.com/r/export/utf/xml/daily/%s' % DAILY[horo_id][1]
    try:
        with http_get(url) as request:
            request.raise_for_status()
            return ET.fromstring(request.content)
    except Exception as error:
        raise Exception(func_name + str(error)) from error


def parse(horo_id, xml: ET.Element):
    """Парсим XML и сохраняем в базу"""
    func_name = "[PARSE] "
    dates = []
    horo_texts = [[] for i in range(len(ZODIACS))]
    try:
        database = Database()
        # Parse xml
        for i, div in enumerate(xml):
            if div.tag == 'date':
                for date in div.attrib.values():
                    dates.append(datetime.strptime(date, '%d.%m.%Y').date())
            for j in range(len(ZODIACS)):
                if div.tag in ZODIACS[j]:
                    for horo_day in div:
                        horo_texts[j].append(horo_day.text.replace('\n', ''))
        # horo_day
        # 0 - yesterday
        # 1 - today
        # 2 - tomorrow
        # 3 - tomorrow2
        daily = {}
        for horo_day in range(4):
            tmp = [horo_texts[i][horo_day] for i in range(len(ZODIACS))]
            texts = {
                'horo_date': dates[horo_day],
                'aries': tmp[0],
                'taurus': tmp[1],
                'gemini': tmp[2],
                'cancer': tmp[3],
                'leo': tmp[4],
                'virgo': tmp[5],
                'libra': tmp[6],
                'scorpio': tmp[7],
                'sagittarius': tmp[8],
                'capricorn': tmp[9],
                'aquarius': tmp[10],
                'pisces': tmp[11]
            }
            daily[horo_day] = {
                'horo_id': horo_id + 1,
                'texts': texts
            }
        save_to_db(daily, database)
        # Save xml to file
        with open('xmls/%s.xml' % DAILY[horo_id][0], 'wb') as file:
            ET.ElementTree(xml).write(file, encoding='utf-8')
    except Exception as error:
        raise Exception(func_name + str(error)) from error
    else:
        database.close()
        return False  # Is fail?


def save_to_db(params: dict, database: Database):
    """Сохранение в базу"""
    func_name = "[SAVE TO DB] "
    try:
        for horo_day, value in params.items():  # SQL update horoscope texts
            sql = update(DailyModel).\
                where(
                    (DailyModel.horo_id == value['horo_id']) & (DailyModel.horo_day == horo_day)
                ).values(value['texts'])
            database.execute(sql)
        database.commit()
    except Exception as error:
        raise Exception(func_name + str(error)) from error
