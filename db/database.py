from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

from config import Config

DeclarativeBase = declarative_base()


class Database():

    config = Config()

    def __init__(self):
        self.engine = self.create_db_engine()
        self._sessionmaker = sessionmaker(bind=self.engine)
        self.session: Session = self._sessionmaker()

    def query(self, *entities, **kwargs) -> Query:
        try:
            return self.session.query(*entities, **kwargs)
        except exc.SQLAlchemyError as error:
            raise error

    def execute(self, *entities, **kwargs):
        try:
            return self.session.execute(*entities, **kwargs)
        except exc.SQLAlchemyError as error:
            raise error

    def add(self, *entities, **kwargs):
        try:
            return self.session.add(*entities, **kwargs)
        except exc.SQLAlchemyError as error:
            raise error

    def commit(self):
        try:
            self.session.commit()
        except exc.SQLAlchemyError as error:
            self.session.rollback()
            raise error

    def close(self):
        try:
            self.session.close()
        except exc.SQLAlchemyError as error:
            self.session.rollback()
            raise error

    def create_db_engine(self):
        url = URL(
            'mysql+pymysql',
            self.config.get('SQL', 'user'),
            self.config.get('SQL', 'pswd'),
            self.config.get('SQL', 'host'),
            self.config.get_int('SQL', 'port'),
            self.config.get('SQL', 'db'),
            query={'charset': 'utf8mb4'}
        )
        engine_params = {
            'poolclass': QueuePool,
            'pool_size': 20,
            'pool_pre_ping': True,
            'echo': False
        }
        try:
            engine = create_engine(url, **engine_params)
            engine.connect()
        except exc.SQLAlchemyError as error:
            raise error
        else:
            DeclarativeBase.metadata.create_all(engine)
            return engine
