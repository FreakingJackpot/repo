import requests
import sqlite3
import datetime
import pytz
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists

engine = create_engine('sqlite:///currency.db', echo=True)
Base = declarative_base()

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


class Currency(Base):
    __tablename__ = 'currency'

    def __init__(self, name, value):
        self.name = name
        self.value = value

    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(Float)


def create_curr(name, value):
    if curr_exist(name):
        newCur = session.query(Currency).filter(Currency.name == name).first()
        newCur.value = value

    else:
        session.add(Currency(name, value))
    session.commit()


def reset_currency():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    request = requests.get(url)
    request = request.json()
    date = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    if date.weekday() == 0:
        key = __Data_check(date,request,days=2)
    elif date.weekday() == 6:
        key = __Data_check(date, request,days=1)
    else:
        key = __Data_check(date, request)
    rates = request["Valute"]
    for i in rates.keys():
        print(rates[i][key])
        create_curr(i, rates[i][key])


def get_currency(name):
    return session.query(Currency).filter(Currency.name == name).first().value


def curr_exist(name):
    return session.query(exists().where(Currency.name == name)).scalar()

#Проверяет поля запроса на совпадение с датой
def __Data_check(date,request,days=0):
    date = date - datetime.timedelta(days=days)
    tmp = '-'.join([str(date.year), str(date.month), str(date.day)])
    if request["Date"].find(tmp) > -1:
        key = 'Value'
    elif request["PreviousDate"].find(tmp) > -1:
        key = 'Previous'
    return key