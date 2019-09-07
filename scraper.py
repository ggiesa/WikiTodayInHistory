
from datetime import datetime
from copy import copy
import traceback

from progress.bar import FillingSquaresBar
import config
import helpers


class CurrentEventsScraper:
    def __init__(self,
        years=None,
        months=None,
        base_url=None,
        scraper=helpers.get_html,
        parser=helpers.parser):

        self.years = years or config.YEARS
        self.months = months or config.MONTHS
        self.base_url = base_url or config.BASE_URL

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


    def _log_error(self, key, year, month, trace):
        self.errors[key].append({
            'error':trace,
            'year':year,
            'month':month
        })


    def _get_raw(self):
        """Scrape raw html strings for current events in given years.
            Return:
                dict: {year:{January:<html>, February:<html>...}}
        """
        with FillingSquaresBar('Scraping Raw', max=len(self.years)*len(self.months)) as bar:
            for year in self.years:
                for month in self.months:
                    try:
                        self.raw[year][month] = self.scraper(self.base_url + f'{month}_{year}')
                    except:
                        self._log_error('scraper', year, month, traceback.format_exc())
                    bar.next()


    def _parse_raw(self):
        """Iterate through raw monthly data, parsing daily events into dict"""
        with FillingSquaresBar('Parsing', max=len(self.years)*len(self.months)) as bar:
            for year in self.raw:
                for month in self.raw[year]:
                    try:
                        self.parsed[year][month] = self.parser(self.raw[year][month])
                    except:
                        self._log_error('parser', year, month, traceback.format_exc())
                    bar.next()


    def run(self):
        """Scrape wikipedia for current events for given years and months, parse results into dict"""
        self._get_raw()
        self._parse_raw()


    def save(self, path=None):
        path = path or f"./scrape_results/scraper_{datetime.utcnow().strftime('%Y-%m-%d_%s')}.pkl"
        helpers.save_object(path, self)


if __name__ == '__main__':
    c = CurrentEventsScraper()
    c.run()
    c.save()
