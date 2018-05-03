from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from flask_login import UserMixin

Base = declarative_base()


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    category = Column(String(50))
    description = Column(String(250))
    image = Column(String(100))
    user_id = Column(String(50), ForeignKey('users.id'))


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), index=True)
    pass_hash = Column(String(120))
    status = Column(String(10))

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
