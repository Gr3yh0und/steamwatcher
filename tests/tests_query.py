#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Michael Morscher'
__description__ = 'Tests for the query module'
__copyright__ = "Copyright 2018, query tests"
__version__ = "0.1"
__maintainer__ = "Michael Morscher"
__email__ = "ich@morschi.com"
__status__ = "in development"

import unittest
import responses
import requests
from requests.exceptions import ConnectionError

import configuration
import query


class TestQuery(unittest.TestCase):

    url = "http://steam.com/data.json"
    data_json = {"response": {
                        "total_count": 1,
                        "games": [
                            {
                                "appid": 578080,
                                "name": "PLAYERUNKNOWN'S BATTLEGROUNDS",
                                "playtime_2weeks": 91,
                                "playtime_forever": 3313,
                                "img_icon_url": "93d896e7d7a42ae35c1d77239430e1d90bc82cae",
                                "img_logo_url": "2d2732a33511b58c69aff6b098a22687a3bb8533"
                            }
                        ]
                    }}

    def test_steam_api_url_backend(self):
        url_part = "some_url_part"
        key = "SOMEKEY"
        additional_parameters = "123"
        self.assertEqual(query.steam_api_url_backend(url_part, key, additional_parameters), configuration.steam_base_url + url_part + "?key=" + key + additional_parameters)

    def test_steam_api_url_logo(self):
        app_id = 123456
        app_logo_url = "logo_url"
        self.assertEqual(query.steam_api_url_logo(app_id, app_logo_url), configuration.steam_logo_url + "/" + str(app_id) + "/" + app_logo_url + ".jpg")

    def test_steam_api_recent_games(self):
        player_id = 123
        data_format = "json"
        self.assertEqual(query.steam_api_recent_games(player_id, data_format), configuration.steam_base_url + "IPlayerService/GetRecentlyPlayedGames/v0001/" + "?key=" + configuration.steam_api_key + "&steamid=" + str(player_id) + "&format=" + data_format)

    @responses.activate
    def test_steam_api_query_success(self):
        responses.add(responses.GET, self.url, json=self.data_json, status=200)
        response = requests.get(self.url, timeout=0.3)
        self.assertEqual(query.steam_api_query(self.url), response.json())

    @responses.activate
    def test_steam_api_query_failure(self):
        with self.assertRaises(ConnectionError):
            requests.get(self.url, timeout=0.1)
