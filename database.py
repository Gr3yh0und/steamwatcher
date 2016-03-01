#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as Sql
import logging
from threading import Lock
import datetime

__author__ = 'Michael Morscher'
__description__ = 'Database access management'
__copyright__ = "Copyright 2015, Steam query tests"
__version__ = "0.1"
__maintainer__ = "Michael Morscher"
__email__ = "morscher@hm.edu"
__status__ = "in development"


class Database(object):

    # server -> string: name of server
    # user -> string: name of user
    # password -> string: password of user
    # database -> string: name of database
    def __init__(self, server, user, password, database):
        self.server = server
        self.database = database
        self.user = user
        self.password = password
        self.db = Lock()
        self.logger = logging.getLogger("steam.database")

    def send_command(self, command):
        result = None
        if command.startswith("SELECT"):
            done = False
            while not done:
                if not self.db.locked():
                    result = self.execute_command(command)
                    done = True
        else:
            with self.db:
                result = self.execute_command(command)
        return result

    def execute_command(self, command):
        result = None
        connection = Sql.connect(self.server, self.user, self.password, self.database)
        with connection:
            cursor = connection.cursor()
            cursor.execute(command)
            if command.startswith("SELECT"):
                result = cursor.fetchall()
        return result

    # data -> list: return from sql query
    @staticmethod
    def get_element(data):
        for e in data:
            if isinstance(e, tuple):
                return e[0]
            else:
                return e

# users
# ToDo: Remove user_id from DB and here and use steam ID as primary key
    def user_exists(self, user_id):
        return self.get_element(self.send_command("SELECT id FROM users WHERE id = '{0}'".format(user_id)))

    def user_add(self, username, steam_id):
        self.send_command("INSERT INTO users (id,name,id_steam,created) VALUES (0, '{0}', '{1}', NOW())"
                          .format(username, steam_id))

    def user_delete(self, user_id):
        if self.user_exists(user_id):
            self.send_command("UPDATE users SET deleted = TRUE WHERE id = '{0}'".format(user_id))
        else:
            self.logger.error("User with ID {0} does not exist!".format(user_id))

    # ToDo: remove *
    def user_get_all(self):
        return self.send_command("SELECT * FROM users")

    def user_get_list_all(self):
        return self.send_command("SELECT id, name FROM users")

    # ToDo: remove *
    def user_get_active(self):
        return self.send_command("SELECT * FROM users WHERE active = '1'")

    def user_get_list_active(self):
        return self.send_command("SELECT id, name FROM users WHERE active = '1'")

    def user_get_single_data(self, user_id):
        return self.send_command("SELECT * FROM users WHERE id = '{0}'".format(user_id))

# apps
    def app_exists(self, app_id):
        return self.get_element(self.send_command("SELECT id FROM apps WHERE id = '{0}'".format(app_id)))

    def app_add(self, app_id, app_name, icon_url, logo_url):
        # escape characters
        app_name = app_name.replace("'", "\\'")
        self.send_command("INSERT INTO apps (id,name,icon_url,logo_url) VALUES ('{0}', '{1}', '{2}', '{3}')"
                          .format(app_id, app_name.encode('utf8'), icon_url, logo_url))

    def app_delete(self, app_id):
        if self.app_exists(app_id):
            self.send_command("UPDATE apps SET deleted = TRUE WHERE id = '{0}'".format(app_id))
        else:
            self.logger.error("App with ID {0} does not exist!".format(app_id))

    def playtime_add(self, user_id, app_id, playtime_week, playtime_total):
        self.send_command("INSERT INTO playtime (id,id_user,id_app,playtime_week,playtime_total,date) "
                          "VALUES (0, '{0}', '{1}', '{2}', '{3}', NOW())"
                          .format(user_id, app_id, playtime_week, playtime_total))


# playground
############

    def playtime_get_1day(self, user_id, app_id, date):
        return self.send_command("SELECT date, playtime_week, playtime_total FROM playtime WHERE id_user = '{0}' AND id_app = '{1}' AND date LIKE '{2}%'".format(user_id, app_id, date))





if __name__ == "__main__":

    database_host = "127.0.0.1"
    database_user = "steamuser"
    database_password = "steamuser!!345"
    database_name = "steam"
    database = Database(database_host, database_user, database_password, database_name)

    for time in database.playtime_get_1day(4, 218620, datetime.datetime.now().strftime("%Y-%m-%d")):
        print time
