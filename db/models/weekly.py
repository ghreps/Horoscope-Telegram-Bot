from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import Integer, SmallInteger, Text, VARCHAR

from ..database import DeclarativeBase


class WeeklyModel(DeclarativeBase):

    __tablename__ = 'weekly'
    id = Column(Integer, primary_key=True, autoincrement=True)
    horo_id = Column(SmallInteger)
    horo_date = Column(VARCHAR(50), default='')
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

    def __init__(self, id):
        self.horo_id = id
