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
    if session.query(exists().where(Currency.name == name)).scalar():
        newCur = session.query(Currency).filter(Currency.name == name).first()
        newCur.value = value

    else:
        session.add(Currency(name, value))
    session.commit()


def reset_currency():
    date = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    request = requests.get(url)
    request = request.json()
    tmp = '-'.join([str(date.year), str(date.month), str(date.day)])
    if request["Date"].find(tmp) > -1:
        key = 'Value'
    elif request["PreviousDate"].find(tmp) > -1:
        key = 'Previous'
    rates = request["Valute"]
    for i in rates.keys():
        print(rates[i][key])
        create_curr(i, rates[i][key])


def get_currency(name):
    return session.query(Currency).filter(Currency.name == name).first().value


class db:
    def __init__(self):
        self.conn = sqlite3.connect("db.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Currencies (name text UNIQUE ,value FLOAT ) """)
        self.Add()

    def Add(self):
        date = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        request = requests.get(url)
        request = request.json()
        tmp = '-'.join([str(date.year), str(date.month), str(date.day)])
        if request["Date"].find(tmp) > -1:
            key = 'Value'
        elif request["PreviousDate"].find(tmp) > -1:
            key = 'Previous'
        rates = request["Valute"]
        for i in rates.keys():
            try:
                self.cursor.execute("INSERT INTO Currencies VALUES (?,?)", (i, rates[i][key]))
            except:
                self.cursor.execute("UPDATE Currencies SET value = ? WHERE name=?", (rates[i][key], i))
        self.conn.commit()

    def Update(self):
        self.Add()

    def Get(self, currency):
        self.cursor.execute("SELECT value FROM Currencies WHERE name=?", (currency,))
        return self.cursor.fetchone()[0]
