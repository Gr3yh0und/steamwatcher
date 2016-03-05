#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import datetime
import dateutils
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from database import Database

__author__ = 'Michael Morscher'
__description__ = 'REST backend service'
__copyright__ = "Copyright 2016"
__version__ = "0.1"
__maintainer__ = "Michael Morscher"
__email__ = "morscher@hm.edu"
__status__ = "in development"

# database configuration
database_host = "192.168.0.8"
database_user = "steamuser"
database_password = "steamuser!!345"
database_name = "steam"
database = Database(database_host, database_user, database_password, database_name)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/set": {"origins": "*"}})


@app.route("/")
def index():
    return "Steam Watcher Backend"


@app.route("/block")
def block():
    return "Get Block Information"


@app.route("/block/day/<day>/user/<user>")
def block_day(day, user):
    value = database.block_playtime_day_total(user, day)[0][0]
    if value is not None:
        data = [{'value': int(value)}]
    else:
        data = [{'value': 0}]
    return json.dumps(data)


# diagram x - get the total amount of playtime in a month
@app.route("/block/month/total/<month>/user/<user>/")
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def block_month_total(month, user):
    value = database.block_playtime_month(user, month)[0][0]
    if value is not None:
        data = [{'value': int(value)}]
    else:
        data = [{'value': 0}]
    return json.dumps(data)


# diagram 1 - get details for a month / every day and every game
@app.route("/block/month/details/<month>/user/<user>/")
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def block_month_details(month, user):
    value = []

    # get apps played in a month
    apps = database.blocks_get_month_app_ids(user, month)

    # check for every day
    for day in range(01, 32):

        # define date and add it to row
        date = "{0}-{1:0=2d}".format(month, day)
        entry = [{"v": day}]

        # request playtime for every app
        for application in apps:
            result = database.block_playtime_day_game(user, application[0], date)[0][0]

            # replace None with 0
            if result is None:
                result = 0

            # add it to the row
            entry.append({"v": int(result)})

        # add to list
        value.append({"c": entry})

    # create columns dictionary and add X-Axis
    cols_dict = [{"label": 'Day', "type": 'string'}]

    # add a column for every app
    for application in apps:
        cols_dict.append({"label": database.app_get_name(application[0]), "type": 'number'})

    return jsonify(cols=cols_dict, rows=value)


# diagram 2 - get the total amount of playtime for each app in a month
@app.route("/block/month/playtime/<month>/user/<user>/")
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def block_month_app_playtime(month, user):
    value = []

    # check every application
    for application in database.blocks_get_month_app_ids(user, month):
        app_name = database.app_get_name(application[0])
        result = database.block_playtime_day_game(user, application[0], month)[0][0]
        value.append({"c": [{"v": app_name}, {"v": int(result)}]})

    # create columns dictionary and add X-Axis
    cols_dict = [
        {"label": 'App', "type": 'string'},
        {"label": 'Playtime', "type": 'number'}
    ]

    return jsonify(cols=cols_dict, rows=value)


# diagram 3 - get the total amount of playtime in the last 12 months
@app.route("/block/month/last12/user/<user>/")
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def block_month_last12(user):
    value = []

    # calculate the first day of the current month
    day_today = datetime.date.today()
    day_first = day_today.replace(day=1)
    month = day_first

    # get the last 12 year-month-combinations
    for i in range(0, 12):

        # current date and database query
        date = "{0}-{1:0=2d}".format(month.year, month.month)
        result = database.block_playtime_month(user, date)[0][0]

        # replace None with 0
        if result is None:
            result = 0

        # add result to the final list
        value.append({"c": [{"v": date}, {"v": int(result)}]})

        # do the calculation for the next iteration
        month = month - dateutils.relativedelta(months=+1)

    # create columns dictionary and add X-Axis
    cols_dict = [
        {"label": 'Day', "type": 'string'},
        {"label": 'Playtime', "type": 'number'}
    ]

    return jsonify(cols=cols_dict, rows=value)


# diagram 4 - calendar
@app.route("/block/month/last365/user/<user>/")
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def block_month_last365(user):
    value = []

    # calculate the first day of the current day
    day_today = datetime.date.today()
    day = day_today

    # get the last 365 days
    for i in range(1, 365):

        # current date and database query
        result = database.block_playtime_day_total(user, day)[0][0]

        # replace None with 0
        if result is None:
            result = 0

        # add result to the final list
        value.append({"c": [{"v": "Date({0}, {1}, {2})".format(day.year, int(day.month) - 1, day.day)}, {"v": int(result)}]})

        # do the calculation for the next iteration
        day = day - dateutils.relativedelta(days=+1)

    # create columns dictionary and add X-Axis
    cols_dict = [
        {"label": 'Day', "type": 'date'},
        {"label": 'Playtime', "type": 'number'}
    ]

    return jsonify(cols=cols_dict, rows=value)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)