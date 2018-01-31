#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as Sql
import logging
import datetime
from threading import Lock

__author__ = 'Michael Morscher'
__description__ = 'Database access management / API'
__copyright__ = "Copyright 2016"
__version__ = "0.1"
__maintainer__ = "Michael Morscher"
__email__ = "morscher@hm.edu"
__status__ = "in development"

TABLE_PLAYTIME = 'playtime'
TABLE_APPS = 'apps'
TABLE_BLOCKS = 'blocks'
TABLE_USERS = 'users'


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
        self.__connection = Sql.connect(self.server, self.user, self.password, self.database)

    def alive_status(self):
        if self.__connection.open:
            return True
        else:
            return False

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
        with self.__connection:
            cursor = self.__connection.cursor()
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
        return self.get_element(self.send_command("SELECT id FROM {0} WHERE id = '{1}'".format(TABLE_USERS, user_id)))

    def user_add(self, username, steam_id):
        self.send_command("INSERT INTO {0} (id,name,id_steam,created) VALUES (0, '{1}', '{2}', NOW())"
                          .format(TABLE_USERS, username, steam_id))

    def user_delete(self, user_id):
        if self.user_exists(user_id):
            self.send_command("UPDATE {0} SET deleted = TRUE WHERE id = '{1}'".format(TABLE_USERS, user_id))
        else:
            self.logger.error("User with ID {0} does not exist!".format(user_id))

    # ToDo: remove *
    def user_get_all(self):
        return self.send_command("SELECT * FROM {0}".format(TABLE_USERS))

    def user_get_list_all(self):
        return self.send_command("SELECT id, name FROM {0}".format(TABLE_USERS))

    # ToDo: remove *
    def user_get_active(self):
        return self.send_command("SELECT * FROM {0} WHERE active = '1'".format(TABLE_USERS))

    def user_get_list_active(self):
        return self.send_command("SELECT id, name FROM {0} WHERE active = '1'".format(TABLE_USERS))

    def user_get_single_data(self, user_id):
        return self.send_command("SELECT name, steamid, created FROM {0} WHERE id = '{1}'".format(TABLE_USERS, user_id))

    def user_get_recorded_playtime(self, user_id):
        return self.send_command("SELECT SUM(duration) FROM {0} WHERE id_user = '{1}' ".format(TABLE_BLOCKS, user_id))

# apps
    def app_exists(self, app_id):
        return self.get_element(self.send_command("SELECT id FROM {0} WHERE id = '{1}'".format(TABLE_APPS, app_id)))

    def app_add(self, app_id, app_name, icon_url, logo_url):
        # escape characters
        app_name = app_name.replace("'", "\\'")
        self.send_command("INSERT INTO {4} (id,name,icon_url,logo_url) VALUES ('{0}', '{1}', '{2}', '{3}')"
                          .format(app_id, app_name.encode('utf8'), icon_url, logo_url, TABLE_APPS))

    def app_delete(self, app_id):
        if self.app_exists(app_id):
            self.send_command("UPDATE {0} SET deleted = TRUE WHERE id = '{1}'".format(TABLE_APPS, app_id))
        else:
            self.logger.error("App with ID {0} does not exist!".format(app_id))

    def app_get_name(self, app_id):
        return self.get_element(self.send_command("SELECT name FROM {0} WHERE id = '{1}'".format(TABLE_APPS, app_id)))

# playtime

    def playtime_add(self, user_id, app_id, playtime_week, playtime_total):
        self.send_command("INSERT INTO {4} (id,id_user,id_app,playtime_week,playtime_total,date) "
                          "VALUES (0, '{0}', '{1}', '{2}', '{3}', NOW())"
                          .format(user_id, app_id, playtime_week, playtime_total, TABLE_PLAYTIME))

    def playtime_get_1day_game(self, user_id, app_id, date):
        return self.send_command("SELECT date, playtime_week, playtime_total FROM {3} WHERE id_user = '{0}' AND id_app = '{1}' AND date LIKE '{2}%'".format(user_id, app_id, date, TABLE_PLAYTIME))

    def playtime_get_1day(self, user_id, date):
        return self.send_command("SELECT date, id_app, playtime_week, playtime_total FROM {2} WHERE id_user = '{0}' AND date LIKE '{1}%'".format(user_id, date, TABLE_PLAYTIME))

    def playtime_get_1day_game_ids(self, user_id, date):
        return self.send_command("SELECT DISTINCT(id_app) FROM {2} WHERE id_user = '{0}' AND date LIKE '{1}%'".format(user_id, date, TABLE_PLAYTIME))

    def playtime_delete_1day(self, user_id, date):
        return self.send_command("DELETE FROM {0} WHERE id_user = '{1}' AND date LIKE '{2}%'".format(TABLE_PLAYTIME, user_id, date))


# blocks

    def block_add(self, user_id, app_id, start, duration):
        return self.send_command("INSERT INTO {5} (id,id_user,id_app,start,end,duration)"
                                 "VALUES (0, '{0}', '{1}', '{2}', '{3}', '{4}')"
                                 .format(user_id, app_id, start.replace(second=0, microsecond=0), start.replace(second=0, microsecond=0) + datetime.timedelta(minutes=duration), duration, TABLE_BLOCKS))

    def block_playtime_day_total(self, user_id, date):
        return self.send_command("SELECT SUM(duration) FROM {2} WHERE id_user = '{0}' AND start LIKE '{1}%' ".format(user_id, date, TABLE_BLOCKS))

    def block_playtime_day_total_detailed(self, user_id, date):
        return self.send_command("SELECT id_app, SUM(duration) FROM {2} WHERE id_user = '{0}' AND start LIKE '{1}%' GROUP BY id_app".format(user_id, date, TABLE_BLOCKS))

    def block_playtime_day_by_game(self, user_id, app_id, date):
        return self.send_command("SELECT SUM(duration) FROM {3} WHERE id_user = '{0}' AND id_app = '{1}' AND start LIKE '{2}%' ".format(user_id, app_id, date, TABLE_BLOCKS))

    def block_playtime_month(self, user_id, month):
        start = "{0}-01".format(month)
        end = "{0}-31".format(month)
        return self.send_command("SELECT SUM(duration) FROM {3} WHERE id_user = '{0}' AND start BETWEEN '{1}' AND '{2}'".format(user_id, start, end, TABLE_BLOCKS))

    def blocks_app_ids_day(self, user_id, day):
        return self.send_command("SELECT DISTINCT(id_app) FROM {2} WHERE id_user = '{0}' AND start LIKE '{1}%'".format(user_id, day, TABLE_BLOCKS))

    def blocks_app_ids_days_last(self, user_id, days):
        return self.send_command("SELECT id_app FROM {2} WHERE id_user = '{0}' AND DATE_SUB(CURDATE(),INTERVAL {1} DAY) <= start GROUP BY id_app ORDER BY MAX(start) DESC".format(user_id, days, TABLE_BLOCKS))

    def blocks_get_month_app_ids(self, user_id, month):
        start = "{0}-01".format(month)
        end = "{0}-31".format(month)
        return self.send_command("SELECT DISTINCT(id_app) FROM {3} WHERE id_user = '{0}' AND start BETWEEN '{1}' AND '{2}'".format(user_id, start, end, TABLE_BLOCKS))
