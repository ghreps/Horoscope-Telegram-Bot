from os.path import exists
from os import mkdir

import configparser

from logging.config import fileConfig

class Config:

    file = configparser.ConfigParser()

    def __init__(self):
        create_dirs()
        if not exists('config.ini'):
            self.create_config()
        self.file.read('config.ini')

    def get(self, section, param):
        return self.file.get(section, param)

    def get_int(self, section, param):
        return self.file.getint(section, param)

    def create_config(self):
        self.file = configparser.ConfigParser()
        self.file.add_section('APP')
        self.file.set(
            'APP',
            'formatter',
            '[(asctime)s][(levelname)s][(name)s](message)s'
        )
        self.file.add_section('SQL')
        self.file.set('SQL', 'host', '127.0.0.1')
        self.file.set('SQL', 'port', '3306')
        self.file.set('SQL', 'user', 'root')
        self.file.set('SQL', 'pswd', 'admin')
        self.file.set('SQL', 'db', 'horoscope')
        self.file.add_section('TELEGRAM')
        self.file.set('TELEGRAM', 'channel_id', '0')
        self.file.set('TELEGRAM', 'admin_id', '0')
        self.file.set('TELEGRAM', 'token', '')
        self.file.set('TELEGRAM', 'log_level', '20')
        self.file.add_section('DAILY')
        self.file.set('DAILY', 'log_level', '20')
        self.file.add_section('WEEKLY')
        self.file.set('WEEKLY', 'log_level', '20')

        with open('config.ini', 'w') as config_file:
            self.file.write(config_file)
        
        input('Первый запуск, настройте конфиг и перезапустите приложение')


def create_dirs():
    if not exists('logs'):
        mkdir('logs')
    if not exists('cache'):
        mkdir('cache')
    if not exists('xmls'):
        mkdir('xmls')
