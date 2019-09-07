
import pickle
from datetime import datetime
from copy import copy
import calendar
import traceback

import requests
from bs4 import BeautifulSoup
from progress.bar import FillingSquaresBar

class C:
    MONTHS = [m for m in calendar.month_name if m]
    YEARS = list(range(1995, 2019))
    BASE_URL = 'https://en.wikipedia.org/wiki/Portal:Current_events/'

def load_results(path):
    with open('scraper_2019-59-06_1567839551.pkl', 'rb') as f:
        return pickle.load(f)

def get_raw(year, month, base_url=C.BASE_URL):
    r = requests.get(base_url + f'{month}_{year}')
    return r.text


def parser(raw_month_html):
    soup = BeautifulSoup(raw_month_html, features="html.parser")

    days, months, years = set(), set(), set()
    all_dates = soup.table.find_all('div')

    # Filter out redundant css tags - yyyy_mm_d / yyyy_mm_dd
    for date in all_dates:
        year, month, day = date.attrs['id'].split('_')
        days.add(int(day))
        months.add(month)
        years.add(year)

        err_msg = 'parser: Expected raw HTML to correspond to only a single {}. Found data for {}.'
        if len(years) > 1:
            raise ValueError(err_msg.format('year', years))
        if len(months) > 1:
            raise ValueError(err_msg.format('month', months))

    tags = [f'{year}_{month}_{day}' for day in days]

    # Parse events for each day of the month
    parsed = {day:[] for day in days}
    for day, tag in zip(days, tags):
        raw_day_data = soup.find(id=tag).find_all_next('tr')[2].find_all('li')
        for element in raw_day_data:
            parsed[day].append(element.text)
    return parsed


class CurrentEventsScraper:
    def __init__(self, years=None, months=None, base_url=None, scraper=get_raw, parser=parser):

        self.years = years or C.YEARS
        self.months = months or C.MONTHS
        self.base_url = base_url or C.BASE_URL

        self.scraper = scraper
        self.parser = parser

        if not isinstance(self.years, list):
            self.years = [self.years]

        if not isinstance(self.months, list):
            self.months = [self.months]

        months = {month:{} for month in self.months}
        self.raw = {year:copy(months) for year in self.years}
        self.parsed = {year:copy(months) for year in self.years}
        self.errors = {'scraper':[], 'parser':[]}


    def _get_raw(self):
        """Scrape raw html strings for current events in given years.
            Return:
                dict: {year:{January:<html>, February:<html>...}}
        """
        with FillingSquaresBar('Scraping Raw', max=len(self.years)*len(self.months)) as bar:
            for year in self.years:
                for month in self.months:
                    try:
                        self.raw[year][month] = self.scraper(year, month, self.base_url)
                    except:
                        self.errors['scraper'].append({
                            'error':traceback.format_exc(),
                            'year':year,
                            'month':month
                        })
                    bar.next()


    def _parse_raw(self):
        """Iterate through raw monthly data, parsing daily events into dict"""
        with FillingSquaresBar('Parsing', max=len(self.years)*len(self.months)) as bar:
            for year in self.raw:
                for month in self.raw[year]:
                    try:
                        self.parsed[year][month] = self.parser(self.raw[year][month])
                    except:
                        self.errors['parser'].append({
                            'error':traceback.format_exc(),
                            'year':year,
                            'month':month
                        })
                    bar.next()


    def run(self):
        """Scrape wikipedia for current events for given years and months, parse results into dict"""
        self._get_raw()
        self._parse_raw()


    def save(self, path=None):
        path = path or f"./scraper_{datetime.utcnow().strftime('%Y-%M-%d_%s')}.pkl"
        with open(path, 'wb') as f:
            pickle.dump(self, f)


if __name__ == '__main__':
    c = CurrentEventsScraper()
    c.run()
    c.save()
