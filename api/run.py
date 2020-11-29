import os
import schedule
import db
import time
from multiprocessing import Process
from sanic import Sanic
from sanic.response import json, text


def Updatedb():
    schedule.every().day.at("21:00").do(db.Update)
    while True:
        schedule.run_pending()
        time.sleep(1)


db = db.db()
app = Sanic()
Update_bd = Process(target=Updatedb)
Update_bd.start()


@app.get("/course/<currency>")
async def test(request, currency):
    course = await get_course(currency)
    return json({
        "currency": currency,
        "rub_course": course
    })


@app.get("/convert/<before>/<after>/<value>")
async def convert(request, before, after, value):
    value = float(value)
    if before != 'RUB' and after != 'RUB':
        course1 = await get_course(before)
        course2 = await get_course(after)
        result = value * (course1 / course2)
    elif before == 'RUB':
        course = await get_course(after)
        result = value / course
    elif after == 'RUB':
        course = await get_course(before)
        result = value * course
    return json({
        "currency_before": before,
        "currency_after": after,
        "result": round(result, 2)
    })


@app.post('/convert')
async def post_handler(request):
    course = await get_course(request.args['from_currency'][0],
                              request.args['to_currency'][0])
    print(course)

    return json({"currency": request.args['to_currency'][0],
                 "rub_course": float(request.args['amount'][0]) * course
                 })


async def get_course(convert_from):
    value = db.Get(convert_from)
    return float(value)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False
    )
