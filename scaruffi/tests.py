import unittest

from scaruffi import api


class TestScaruffi(unittest.TestCase):

    def setUpClass():
        api.setup_logging("test")

    def test_get_musicians(self):
        musicians = api.get_musicians()
        self.assertEqual(len(musicians), 20)

    def test_get_ratings(self):
        self.assertIsNotNone(api.get_ratings(1960))
        self.assertIsNotNone(api.get_ratings(1970))
        self.assertIsNotNone(api.get_ratings(1980))
        self.assertIsNotNone(api.get_ratings(1990))
        self.assertIsNotNone(api.get_ratings(2000))
        self.assertIsNotNone(api.get_ratings(2010))
