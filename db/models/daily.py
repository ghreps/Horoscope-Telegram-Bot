from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import Integer, SmallInteger, Date, Text

from ..database import DeclarativeBase


class DailyModel(DeclarativeBase):

    __tablename__ = 'daily'

    id = Column(Integer, primary_key=True, autoincrement=True)
    horo_id = Column(SmallInteger)
    horo_day = Column(SmallInteger)
    horo_date = Column(Date, default='2000-01-01')
    aries = Column(Text, default='')
    taurus = Column(Text, default='')
    gemini = Column(Text, default='')
    cancer = Column(Text, default='')
    leo = Column(Text, default='')
    virgo = Column(Text, default='')
    libra = Column(Text, default='')
    scorpio = Column(Text, default='')
    sagittarius = Column(Text, default='')
    capricorn = Column(Text, default='')
    aquarius = Column(Text, default='')
    pisces = Column(Text, default='')

    def __init__(self, id, day):
        self.horo_id = id
        self.horo_day = day
