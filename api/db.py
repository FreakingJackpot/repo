import datetime
import sqlite3

import pytz
import requests


class db:
    def __init__(self):
        self.conn = sqlite3.connect("db.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Currencies (name text UNIQUE ,value FLOAT ) """)
        self.Add()

    # Добавление новых записей в БД
    def Add(self):
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        request = requests.get(url)
        request = request.json()
        date = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
        if date.weekday() == 0:
            key = self.__data_check(date, request, 2)
        elif date.weekday() == 6:
            key = self.__data_check(date, request, 1)
        else:
            key = self.__data_check(date, request)
        rates = request['Valute']
        for i in rates.keys():
            try:
                self.cursor.execute("INSERT INTO Currencies VALUES (?,?)", (i, rates[i][key]))
            except:
                self.cursor.execute("UPDATE Currencies SET value = ? WHERE name=?", (rates[i][key], i))
        self.conn.commit()

    def Update(self):
        self.Add()

    # Получение информации из БД
    def Get(self, currency):
        self.cursor.execute("SELECT value FROM Currencies WHERE name=?", (currency,))
        return self.cursor.fetchone()[0]
    def curr_exist(self,currency):
        self.cursor.execute("SELECT value FROM Currencies WHERE name=?", (currency,))
        return self.cursor.fetchone()
    # Проверяет поля запроса на совпадение с датой
    def __data_check(self, date, request, days=0):
        date = date - datetime.timedelta(days=days)
        tmp = date.strftime("%Y-%m-%d")
        if request["Date"].find(tmp) > -1:
            key = 'Value'
        elif request["PreviousDate"].find(tmp) > -1:
            key = 'Previous'
        return key
