import os
import schedule
import db
import time
from multiprocessing import Process
from sanic import Sanic
from sanic.response import json, text


async def update_db():
    schedule.every().day.at("21:00").do(db.reset_currency)
    while True:
        schedule.run_pending()
        time.sleep(1)


app = Sanic()
Update_bd = Process(target=update_db)
Update_bd.start()


@app.get("/course/<currency>")
async def test(request, currency):
    course = db.get_currency(currency)
    print(currency)
    return json({
        "currency": currency,
        "rub_course": course
    })


@app.get("/convert/<before>/<after>/<value>")
async def convert(request, before, after, value):
    value = float(value)
    if before != 'RUB' and after != 'RUB':
        course1 = db.get_currency(before)
        course2 = db.get_currency(after)
        result = value * (course1 / course2)
    elif before == 'RUB':
        course = db.get_currency(after)
        result = value / course
    elif after == 'RUB':
        course = db.get_currency(before)
        result = value * course
    else:
        result = 1
    return json({
        "currency_before": before,
        "currency_after": after,
        "result": round(result, 2)
    })


@app.post('/convert')
async def post_handler(request):
    course = await db.get_currency(request.args['from_currency'][0],
                                   request.args['to_currency'][0])
    print(course)

    return json({"currency": request.args['to_currency'][0],
                 "rub_course": float(request.args['amount'][0]) * course
                 })


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False
    )
