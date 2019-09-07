import os
from unittest import TestCase
from scraper import CurrentEventsScraper
from _test import test_data


def mock_scraper_fail(url):
    raise ValueError

def mock_parser_fail(html):
    raise ValueError

def mock_scraper(url):
    return test_data.RAW_HTML

def mock_parser(html):
    return test_data.PARSED_HTML


class TestScraper(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.save_path = '_test/test_save_scraper.pkl'

        cls.failed_scrape = CurrentEventsScraper(
            1999, 'March', scraper=mock_scraper_fail, parser=mock_parser
        )
        cls.failed_parse = CurrentEventsScraper(
            1999, 'March', scraper=mock_scraper, parser=mock_parser_fail
        )
        cls.successful = CurrentEventsScraper(
            1999, 'March', scraper=mock_scraper, parser=mock_parser
        )

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.save_path)

    def test_scrape_failure(self):
        self.failed_scrape.run()
        self.assertNotEqual(self.failed_scrape.errors['scraper'], [])
        self.assertEqual(self.failed_scrape.errors['parser'], [])

    def test_parse_failure(self):
        self.failed_parse.run()
        self.assertEqual(self.failed_parse.errors['scraper'], [])
        self.assertNotEqual(self.failed_parse.errors['parser'], [])

    def test_successful_run(self):
        self.successful.run()
        self.assertEqual(self.successful.errors['scraper'], [])
        self.assertEqual(self.successful.errors['parser'], [])

    def test_save(self):
        self.successful.save(self.save_path)
