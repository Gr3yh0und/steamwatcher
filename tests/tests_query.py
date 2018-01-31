import unittest
import configuration
import query


class TestQuery(unittest.TestCase):

    def test_steam_api_url_backend(self):
        configuration.steam_base_url = "http://steam.com"
        url_part = "some_url_part"
        key = "SOMEKEY"
        additional_parameters = "123"
        self.assertEqual(query.steam_api_url_backend(url_part, key, additional_parameters), configuration.steam_base_url + url_part + "?key=" + key + additional_parameters)

