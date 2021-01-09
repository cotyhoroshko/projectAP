import enum

from sqlalchemy import Integer, Column, String, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ModifierEnum(enum.Enum):
    public = 1
    local = 0


class RoleEnum(enum.Enum):
    average = 1
    master = 0


class Advertisement(Base):
    __tablename__ = 'advertisements'
    id = Column(Integer, primary_key=True)
    summary = Column(String(50))
    description = Column(String(512))
    topic = Column(String(15))
    modifier = Column(Enum(ModifierEnum))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='advertisements')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    email = Column(String(30))
    role = Column(Enum(RoleEnum))
    password_hash = Column(String(512))
    advertisements = relationship('Advertisement', back_populates='user')
