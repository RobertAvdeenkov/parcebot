from sqlalchemy import Column,Integer,String,DateTime,func,Boolean,Float,ForeignKey
from sqlalchemy.orm import DeclarativeBase,relationship

class Base(DeclarativeBase):pass

class User(Base):
    __tablename__='users'
    id=Column(Integer,primary_key=True)
    name=Column(String)
    password=Column(String)

    sites=relationship('Site', back_populates='user')
    checks=relationship('Check', back_populates='user')

class Site(Base):
    __tablename__='sites'
    id=Column(Integer,primary_key=True)
    url=Column(String)
    name=Column(String)
    interval=Column(Integer)
    active=Column(Boolean, default=True)
    created_at=Column(DateTime, default=func.now())

    user_id=Column(Integer, ForeignKey('users.id'))
    user=relationship('User', back_populates='sites')

    checks=relationship('Check', back_populates='site')

class Check(Base):
    __tablename__='checks'
    id=Column(Integer,primary_key=True)
    code=Column(Integer)
    response=Column(Float)
    status=Column(Boolean, default=True)
    created_at=Column(DateTime,default=func.now())

    user_id=Column(Integer,ForeignKey('users.id'))
    user=relationship('User',back_populates='checks')

    site_id=Column(Integer,ForeignKey('sites.id'))
    site=relationship('Site', back_populates='checks')
