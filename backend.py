#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from database import Database
import json
from flask_cors import CORS, cross_origin

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


@app.route("/block/month/total/<month>/user/<user>")
def block_month_total(month, user):
    value = database.block_playtime_month(user, month)[0][0]
    if value is not None:
        data = [{'value': int(value)}]
    else:
        data = [{'value': 0}]
    return json.dumps(data)


#
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


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)