import os
import requests
from sanic import Sanic
from sanic.response import json, text

app = Sanic()


@app.get("/course/<currency>")
async def test(request, currency):
    course = await get_course(currency, "RUB")
    return json({
        "currency": currency,
        "rub_course": course
    })


@app.post('/convert')
async def post_handler(request):
    course = await get_course(request.args['from_currency'][0],
                              request.args['to_currency'][0])
    print(course)

    return json({"currency": request.args['to_currency'][0],
                 "rub_course": float(request.args['amount'][0]) * course
                 })


async def get_course(convert_from, convert_to):
    url = 'https://currate.ru/api/'
    token = 'c70e0b7553d7cf53db5964520b420d8d'
    rez = requests.get(url, params={'get': 'rates',
                                          'pairs': convert_from + convert_to,
                                          'key': token})
    print(rez.json())
    return float(rez.json()['data'][convert_from + convert_to])


if __name__ == "__main__":

    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False
    )
