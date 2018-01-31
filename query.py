#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Michael Morscher'
__description__ = 'Module that contains base functions for querying the steam backend'
__copyright__ = "Copyright 2018, query module"
__version__ = "0.1.1"
__maintainer__ = "Michael Morscher"
__email__ = "ich@morschi.com"
__status__ = "in development"

import requests
import urllib
import logging

from database import Database
import configuration

# create logging
log = logging.getLogger("steam")
log.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
log.addHandler(sh)


def steam_api_url_backend(url_part, key, additional_parameters):
    """
    Adds given parameters to steam base backend URL and returns it
    :param url_part: Additional url parameter
    :param key: Steam backend authentication key
    :param additional_parameters: Additional parameters that should be added to the URL
    :return: steam backend URL string
    :rtype: str"""
    return configuration.steam_base_url + url_part + "?key=" + key + additional_parameters


def steam_api_url_logo(app_id, app_logo_url):
    """
    Adds given parameters to steam base logo URL and returns it
    :param integer app_id: ID of the steam app
    :param str app_logo_url: part URL of the app logo
    :return: steam logo URL string
    :rtype: str"""
    return configuration.steam_logo_url + "/" + str(app_id) + "/" + app_logo_url + ".jpg"


def steam_api_recent_games(player_id, data_format='json'):
    """
    Combines given input parameters and return the full steam backend request URL
    :param integer player_id: Steam ID of the requested player
    :param str data_format: Format of requested data, defaults to json
    :return: steam backend recent played games URL string
    :rtype: str"""
    return steam_api_url_backend("IPlayerService/GetRecentlyPlayedGames/v0001/", configuration.steam_api_key,
                                 '&steamid=' + str(player_id) + "&format=" + data_format)


def steam_api_query(url):
    """
    Queries the steam API using the given URL parameter and returns a json object
    :param str url: steam query URL
    :return: response object containing json query result
    :rtype: response object"""
    logger = logging.getLogger("steam.query.steam_api_query")
    logger.debug("Querying URL =  {0}".format(url))

    # make request to download website
    headers = {'User-Agent': configuration.misc.user_agent}
    page = requests.get(url, headers=headers, timeout=15)

    # check HTTP response code
    if page.status_code != 200:
        logger.error("Error! Website returned HTTP status code {0}!".format(page.status_code))
        return False

    # return content
    return page.json()


def download_picture(url, filename):
    """
    Downloads a picture from an URL
    :param str url: URL to picture
    :param str filename: filename to be saved locally
    :return: True on success, False on error
    :rtype: bool"""
    logger = logging.getLogger("steam.query.download_picture")
    logger.debug("Downloading picture ({0}) ...".format(filename))

    try:
        urllib.urlretrieve(url, filename)
        return True
    except:
        logger.error("Could not download picture {0} from {1}!".format(filename, url))
        return False


def app_add(app_id, app_name, app_icon_url, app_logo_url, database):
    """
    Adds a new app to the database and downloads the logo from steam backend
    :param integer app_id: ID of the application
    :param str app_name: name of the application
    :param str app_icon_url: hash of URL where to find the icon
    :param str app_logo_url: hash of URL where to find the logo
    :param object database: database object
    :return: True on success, False on error
    :rtype: bool
    """
    logger = logging.getLogger("steam.query.app_add")
    logger.debug("App {0} ({1}) will be added to the database ...".format(app_name.encode('utf8'), app_id))

    try:
        # insert app to database
        database.app_add(app_id, app_name, app_icon_url, app_logo_url)

        # download pictures
        download_picture(steam_api_url_logo(app_id, app_logo_url),
                         configuration.misc.folder_logos + "/" + str(app_id) + ".jpg")

        log.debug("App with ID {0} ({1}) will be added to the database ...".format(app_name.encode('utf8'), app_id))
        return True
    except:
        return False


if __name__ == "__main__":
    log.info("Execution started")

    # create database connection
    log.info("Connecting to database {0} on {1}".format(configuration.database_name.encode('utf8'),
                                                        configuration.database_host.encode('utf8')))
    try:
        database = Database(configuration.database_host, configuration.database_user, configuration.database_password,
                            configuration.database_name)
    except Exception, e:
        log.warning("Database connection not successful!")
        log.error("{0}".format(e))
        log.error("Aborting run...")
        exit(255)

    # get all activated users
    log.info("Starting to query user information")
    for user in database.user_get_active():
        user_id = user[0]
        user_name = user[1]
        user_steam_id = user[2]

        # query stats for every user
        log.debug("Getting stats for user: {0} ({1})".format(user_name, user_id))
        stats = steam_api_query(steam_api_recent_games(user_steam_id))

        # check if the user has played any games
        if stats['response']['total_count'] > 0:

            # check all recently played games
            for app in stats['response']['games']:

                # check if app/game already exists in database
                if database.app_exists(app.get("appid")):
                    # add game play time
                    database.playtime_add(user_id, app.get("appid"), app.get("playtime_2weeks"),
                                          app.get("playtime_forever"))
                else:
                    # add new app/game
                    if app.get("name"):
                        app_add(app.get("appid"), app.get("name"), app.get("img_icon_url"), app.get("img_logo_url"),
                                database)

    log.info("Execution stopped")
