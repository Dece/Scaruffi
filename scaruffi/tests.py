import logging
import unittest

from scaruffi.api import ScaruffiApi


class TestScaruffi(unittest.TestCase):

    def setUp(self):
        self.api = ScaruffiApi()

    def tearDown(self):
        self.api = None

    def test_get_musicians(self):
        musicians = self.api.get_musicians()
        self.assertEqual(len(musicians), 20)

    def test_get_ratings(self):
        self.assertIsNotNone(self.api.get_ratings(1960))
        self.assertIsNotNone(self.api.get_ratings(1970))
        self.assertIsNotNone(self.api.get_ratings(1980))
        self.assertIsNotNone(self.api.get_ratings(1990))
        self.assertIsNotNone(self.api.get_ratings(2000))
        self.assertIsNotNone(self.api.get_ratings(2010))
