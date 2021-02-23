import configparser
import os


class Config:

    def __init__(self):
        if not os.path.exists('config.ini'):
            self.create_config()
        self.file = configparser.ConfigParser()
        self.file.read('config.ini')

    def get(self, section, param):
        return self.file.get(section, param)

    def get_int(self, section, param):
        return self.file.getint(section, param)

    def create_config(self):
        new = configparser.ConfigParser()
        new.add_section('SQL')
        new.set('SQL', 'host', '127.0.0.1')
        new.set('SQL', 'port', '3306')
        new.set('SQL', 'user', 'root')
        new.set('SQL', 'pswd', 'admin')
        new.set('SQL', 'db', 'db')
        new.add_section('TELEGRAM')
        new.set('TELEGRAM', 'channel_id', '0')
        new.set('TELEGRAM', 'admin_id', '0')
        new.set('TELEGRAM', 'token', '')

        with open('config.ini', 'w') as config_file:
            new.write(config_file)
