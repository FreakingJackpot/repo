import os
import time
from multiprocessing import Process

import db
import schedule
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


@app.post("/course/")
async def convert(request):
    before = request.args['before'][0]
    after = request.args['after'][0]
    value = request.args['value'][0]
    value = float(value)
    if (before != "RUB" and not db.curr_exist(before)) or (after != "RUB" and not db.curr_exist(after)) or value <= 0:
        return json({
            "currency_before": before,
            "currency_after": after,
            "result": 'ERROR'
        })
    if before != 'RUB' and after != 'RUB':
        course1 = await get_course(before)
        course2 = await get_course(after)
        result = value * (course1 / course2)
    elif before == 'RUB' and after != 'RUB':
        course = await get_course(after)
        result = value / course
    elif after == 'RUB' and before != 'RUB':
        course = await get_course(before)
        result = value * course
    else:
        result = value
    return json({
        "currency_before": before,
        "currency_after": after,
        "result": round(result, 4)
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
