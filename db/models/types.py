from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import SmallInteger, VARCHAR

from ..database import DeclarativeBase


class TypesModel(DeclarativeBase):

    __tablename__ = 'types'
    horo_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255))
    file = Column(VARCHAR(255), primary_key=True)

    def __init__(self, id, name, file):
        self.horo_id = id
        self.name = name
        self.file = file
