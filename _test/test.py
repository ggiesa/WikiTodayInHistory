from unittest import TestCase
import os
import helpers
from _test import test_data

class TestHelpers(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.save_path = '_test/test_save_obj.pkl'
        cls.url = 'https://en.wikipedia.org/wiki/Portal:Current_events/January_1995'

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.save_path)

    def test_save_load_obj(self):
        obj = [1,2,3]
        helpers.save_object(self.save_path, obj)

        t = helpers.load_object(self.save_path)
        self.assertEqual(obj, t)

    def test_get_html(self):
        self.assertIsNotNone(helpers.get_html(self.url))

    def test_parser(self):
        r = helpers.parser(test_data.RAW_HTML)
        self.assertEqual(r, test_data.PARSED_HTML)

        with self.assertRaises(ValueError):
            helpers.parser(test_data.MULTIPLE_YEAR_HTML)

        with self.assertRaises(ValueError):
            helpers.parser(test_data.MULTIPLE_MONTH_HTML)
