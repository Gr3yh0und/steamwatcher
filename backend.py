#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask
from database import Database
import json
import datetime

__author__ = 'Michael Morscher'
__description__ = 'REST backend service'
__copyright__ = "Copyright 2016"
__version__ = "0.1"
__maintainer__ = "Michael Morscher"
__email__ = "morscher@hm.edu"
__status__ = "in development"

# database configuration
database_host = "127.0.0.1"
database_user = "steamuser"
database_password = "steamuser!!345"
database_name = "steam"
database = Database(database_host, database_user, database_password, database_name)

app = Flask(__name__)


@app.route("/")
def index():
    return "Steam Watcher Backend"


@app.route("/block")
def block():
    return "Get Block Information"


@app.route("/block/day/<day>/user/<user>")
def block_day(day, user):
    value = database.block_playtime_day(user, day)[0][0]
    if value is not None:
        data = [{'value': int(value)}]
    else:
        data = [{'value': 0}]
    return json.dumps(data)


@app.route("/block/month/total/<month>/user/<user>")
def block_month_total(month, user):
    value = database.block_playtime_month(user, month)[0][0]
    if value is not None:
        data = [{'value': int(value)}]
    else:
        data = [{'value': 0}]
    return json.dumps(data)


@app.route("/block/month/details/<month>/user/<user>/")
def block_month_details(month, user):
    value = []

    # check for every day
    for day in range(01, 32):

        # get data
        date = "{0}-{1:0=2d}".format(month, day)
        result = database.block_playtime_day(user, date)[0][0]

        # convert None to 0
        if result is None:
            result = 0

        # add to list
        value.append({'date': date, 'value': int(result)})
    return json.dumps(value)


if __name__ == "__main__":
    app.run(debug=True)