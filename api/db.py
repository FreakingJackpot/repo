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

    def Add(self):
        date = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
        date = date - datetime.timedelta(days=1)
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
