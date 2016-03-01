# -*- coding: UTF-8 -*
'''
    data model
    ~~~~~~~~~~~~~~~~
    sqlalchemy data model.

    :copyright: 20160204 by raptor.zh@gmail.com.
'''
from config import config

from sqlalchemy import create_engine

engine = create_engine(config["db_url"])

from sqlalchemy import Table, ForeignKey, Column, String, Unicode, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


Base = declarative_base()

class User(Base):
    __tablename__ = "gauser"

    email     = Column(Unicode(100), primary_key=True)
    secret    = Column(String(10), nullable=False)  # if none, password is not required
    expires   = Column(Float)
    key       = Column(String(33), nullable=False, unique=True)
    resetpw   = Column(String(10))
    inv_setpw = Column(Float)
    inv_login = Column(Float)
    inv_reset = Column(Float)


metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)
