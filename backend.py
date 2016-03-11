#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import datetime
import dateutils
from flask import Flask, jsonify
from flask_cors import cross_origin
from flask_api import status

from database import Database
import configuration

__author__ = 'Michael Morscher'
__description__ = 'Python Flask REST backend service'
__copyright__ = "Copyright 2016"
__version__ = "0.2"
__maintainer__ = "Michael Morscher"
__email__ = "morscher@hm.edu"
__status__ = "in development"

# Make Database connection
database = Database(configuration.database_host, configuration.database_user,
                    configuration.database_password, configuration.database_name)

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['CORS_HEADERS'] = 'Content-Type'


# returns an error message
def error_message(error_code, error_message_user, error_message_internal):
    return {"errors": [{"userMessage": error_message_user,
                        "internalMessage": error_message_internal,
                        "code": error_code}]}


# Default index page
@app.route("/")
def index():
    return "Steam Watcher Backend REST API v{0}".format(__version__)


# Return information about a single user
@app.route("/user/information/user/<user>/")
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def user_information(user):
    data = []
    result = database.user_get_single_data(user)
    if result is not ():
        data.append({'id': user})
        data.append({'name': result[0][0]})
        data.append({'steamid': result[0][1]})
        data.append({'created': "{0}".format(result[0][2])})
        data.append({'recorded_playtime': int(database.user_get_recorded_playtime(user)[0][0])})
        return json.dumps(data)
    else:
        return jsonify(error_message(404, "User not found!", "User not found!")), status.HTTP_404_NOT_FOUND


# Return a list of all currently activated users
# ToDO: to be removed because of security reasons? Hiding data?
@app.route("/user/list/")
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def user_list():
    data = []
    result = database.user_get_list_active()
    for user in result:
        data.append({'id': user[0], 'name': user[1]})
    return json.dumps(data)


# Return the total playtime of a user of all apps on a given date (1 day)
@app.route("/block/day/<day>/user/<user>/")
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def block_day(day, user):

    # ToDo: Manage database connection right
    # check database connection first
    if database.alive_status():

        # check if queried user exists
        if not database.user_exists(user):
            return jsonify(error_message(404, "User not found!", "User not found!")), status.HTTP_404_NOT_FOUND

        # check if queried day has correct format
        try:
            datetime.datetime.strptime(day, '%Y-%m-%d')
        except ValueError:
            return jsonify(error_message(400, "Incorrect or not possible data format for given day (YYYY-MM-DD)!",
                                         "Incorrect or not possible data format for given day (YYYY-MM-DD)!")),\
                   status.HTTP_400_BAD_REQUEST

        # check if queried day is not in the future
        if datetime.datetime.strptime(day, "%Y-%m-%d") > datetime.datetime.now():
            return jsonify(error_message(400, "Given date is in the future!", "Given date is in the future!")),\
                   status.HTTP_400_BAD_REQUEST

        # query database
        result = database.block_playtime_day_total(user, day)[0][0]
    else:
        return jsonify(error_message(503, "Database server not available!",
                                     "No available connection to the database server!")), \
               status.HTTP_503_SERVICE_UNAVAILABLE

    # check if database result makes sense
    if result is not None:
        value = int(result)
    else:
        value = 0

    return jsonify(day=day, user=user, value=value)


# Return total playtime for all apps for a given month
@app.route("/block/month/total/<month>/user/<user>/")
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def block_month_total(month, user):

    # check if queried user exists
    if not database.user_exists(user):
        return jsonify(error_message(404, "Error: User not found!", "User not found!")), status.HTTP_404_NOT_FOUND

    # check if queried day has correct format
    try:
        datetime.datetime.strptime(month, '%Y-%m')
    except ValueError:
        return jsonify(error_message(400, "Error: Incorrect or not possible data format for given month (YYYY-MM)!",
                                     "Incorrect or not possible data format for given month (YYYY-MM)!")),\
               status.HTTP_400_BAD_REQUEST

    # check if queried day is not in the future
    if datetime.datetime.strptime(month, "%Y-%m") > datetime.datetime.now():
        return jsonify(error_message(400, "Error: Given month is in the future!", "Given month is in the future!")),\
               status.HTTP_400_BAD_REQUEST

    # query database
    result = database.block_playtime_month(user, month)[0][0]

    # check if database result makes sense
    if result is not None:
        value = int(result)
    else:
        value = 0

    return jsonify(month=month, user=user, value=value)


# Return total playtime for each app for each day for the last X days (given)
@app.route("/block/last/days/<days>/user/<user>/")
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def block_last_days(days, user):
    value = []
    total = 0

    # check if queried user exists
    if not database.user_exists(user):
        return jsonify(error_message(404, "Error: User not found!", "User not found!")), status.HTTP_404_NOT_FOUND

    # check if parameter is a number and convert it to integer
    try:
        days = int(days)
    except:
        return jsonify(error_message(400, "Error: Days is no number!",
                                     "Days is no number: Int transformation not possible!")), status.HTTP_404_NOT_FOUND

    # check if days are higher than a year: Not allowed due to runtime duration of db query
    if days > 365:
        return jsonify(error_message(400, "Error: Days is not allowed to be higher than 365!",
                                     "Days is not allowed to be higher than 365!")), status.HTTP_404_NOT_FOUND

    # get today's date
    today = datetime.date.today()

    # get all used apps for the last given days
    applications = database.blocks_get_ids_lastdays(user, days)

    # check data for every day
    for x in range(1, days + 1):

        # calculate date difference
        day = today - datetime.timedelta(days=x)
        date = "{0}".format(day)
        entry = [{"v": date}]

        # query db for playtime
        result = database.block_playtime_day_total_detailed(user, date)

        # for each app used in the whole period
        for application in applications:
            found = False

            # for every app used on that day
            for application_time in result:

                # if app was used that day
                if application[0] == application_time[0]:
                    found = True
                    entry.append({"v": int(application_time[1])})
                    total += application_time[1]

            # else return 0 minutes as value
            if found is False:
                entry.append({"v": 0})

        # add to list
        value.append({"c": entry})

    # create columns dictionary and add X-Axis
    cols_dict = [{"label": 'Day', "type": 'string'}]

    # add every app to columns
    for application in applications:
        cols_dict.append({"label": database.app_get_name(application[0]), "type": 'number'})

    if total > 0:
        return jsonify(total=int(total), cols=cols_dict, rows=value)
    else:
        return jsonify(error_message(400, "Sorry, there is no information available for the given time window!",
                                     "Total playtime is null")), status.HTTP_404_NOT_FOUND


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
            result = database.block_playtime_day_by_game(user, application[0], date)[0][0]

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
        result = database.block_playtime_day_by_game(user, application[0], month)[0][0]
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
        value.append({"c": [{"v": "Date({0}, {1}, {2})".format(day.year, int(day.month) - 1, day.day)},
                            {"v": int(result)}]})

        # do the calculation for the next iteration
        day = day - dateutils.relativedelta(days=+1)

    # create columns dictionary and add X-Axis
    cols_dict = [
        {"label": 'Day', "type": 'date'},
        {"label": 'Playtime', "type": 'number'}
    ]
    return jsonify(cols=cols_dict, rows=value)


if __name__ == "__main__":
    app.run(host=configuration.server_listen_ip, debug=configuration.server_debug_level)
