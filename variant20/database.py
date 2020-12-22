import enum

from sqlalchemy import create_engine, Integer, Column, String, Enum, ForeignKey
from sqlalchemy.dialects.mysql import TINYTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('mysql+pymysql://lab:password@localhost:3306/pplab?charset=utf8mb4', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class ModifierEnum(enum.Enum):
    public = 1
    local = 0


class Advertisement(Base):
    __tablename__ = 'advertisements'
    id = Column(Integer, primary_key=True)
    summary = Column(String(50))
    description = Column(TINYTEXT)
    topic = Column(String(15))
    modifier = Column(Enum(ModifierEnum))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='advertisements')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    email = Column(String(30))
    password_hash = Column(String(512))
    advertisements = relationship('Advertisement', back_populates='user')
