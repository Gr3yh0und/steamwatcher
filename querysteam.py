#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Michael Morscher'
__description__ = ''
__copyright__ = "Copyright 2015, Steam query tests"
__version__ = "0.1"
__maintainer__ = "Michael Morscher"
__email__ = "morscher@hm.edu"
__status__ = "in development"

import requests
import urllib
import logging
import time
import json
from database import Database

# Steam API
steam_api_key = "A104C12F64A12F31CF6408D54496022C"
steam_base_url = "http://api.steampowered.com/"
steam_logo_url = "http://media.steampowered.com/steamcommunity/public/images/apps/"

# user agent for queries
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'

# database configuration
database_host = "bitch"
database_user = "steamuser"
database_password = "steamuser!!345"
database_name = "steam"

# folder
folder_logos = "logos"

# create logging
logger = logging.getLogger("steam")
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)

# create database connection
database = Database(database_host, database_user, database_password, database_name)


def steam_api_url(url_part, key, additional_parameters):
    return steam_base_url + url_part + "?key=" + key + additional_parameters


def steam_api_logo_url(app_id, app_logo_url):
    return steam_logo_url + "/" + str(app_id) + "/" + app_logo_url + ".jpg"


def steam_api_recent_games(player_id, data_format='json'):
    return steam_api_url("IPlayerService/GetRecentlyPlayedGames/v0001/",
                         steam_api_key, '&steamid=' + str(player_id) + "&format=" + data_format)


def steam_api_query(url):
    logger = logging.getLogger("steam.download_site")
    logger.debug("Querying URL =  {0}".format(url))

    # make request to download website
    headers = {'User-Agent': user_agent}
    page = requests.get(url, headers=headers, timeout=15)

    # check HTTP response code
    if page.status_code != 200:
        logger.error("Error! Website returned HTTP status code {0}!".format(page.status_code))
        return False

    # return content
    return page.json()


def download_picture(url, filename):
    """Downloads a picture from an URL
    @param url: URL to picture
    @param filename: filename to be saved locally"""
    logger = logging.getLogger("steam.download_picture")

    logger.debug("Downloading picture ({0}) ...".format(filename))
    try:
        urllib.urlretrieve(url, filename)
    except:
        logger.error("Could not download picture {0} from {1}!".format(filename, url))
        return False
    return True


def app_add(app_id, app_name, app_icon_url, app_logo_url):
    """ Adds a new app to the database and downloads the logo from steam backend
    :param app_id: ID of application
    :param app_name: name of application
    :param app_icon_url: hash of URL where to find the icon
    :param app_logo_url: hash of URL where to find the logo
    :return:
    """

    logger.debug("App {0} ({1}) will be added to database ...".format(app_name.encode('utf8'), app_id))

    try:
        # insert app to database
        database.app_add(app_id, app_name, app_icon_url, app_logo_url)

        # download pictures
        download_picture(steam_api_logo_url(app_id, app_logo_url), folder_logos + "/" + str(app_id) + ".jpg")

        return True
    except:
        return False


if __name__ == "__main__":
    logger.info("Execution started")

    # get all activated users
    for user in database.user_get_active():
        user_id = user[0]
        user_name = user[1]
        user_steam_id = user[2]

        # query stats for every user
        logger.debug("Getting stats for user: {0}".format(user_name))
        stats = steam_api_query(steam_api_recent_games(user_steam_id))

        # check if the user has played any games
        if stats['response']['total_count'] > 0:

            # check all recently played games
            for app in stats['response']['games']:

                # check if app/game already exists in database
                if database.app_exists(app['appid']):
                    # add game play time
                    database.playtime_add(user_id, app['appid'], app['playtime_2weeks'], app['playtime_forever'])
                else:
                    # add new app/game
                    app_add(app['appid'], app['name'], app['img_icon_url'], app['img_logo_url'])
