
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


    def _log_error(self, collection, year, month, trace):
        collection.append({
            'error':trace,
            'year':year,
            'month':month
        })

    def _interval_generator(self, task_name):
        with FillingSquaresBar(task_name, max=len(self.years)*len(self.months)) as bar:
            for year in self.years:
                for month in self.months:
                    yield (year, month)
                    bar.next()


    def _get_raw(self):
        """Scrape raw html strings for current events in given years."""
        for year, month in self._interval_generator("Scraping Raw"):
            try:
                self.raw[year][month] = self.scraper(self.base_url + f'{month}_{year}')
            except:
                self._log_error(self.errors['scraper'], year, month, traceback.format_exc())


    def _parse_raw(self):
        """Iterate through raw monthly data, parsing daily events into dict"""
        for year, month in self._interval_generator("Parsing"):
            try:
                self.parsed[year][month] = self.parser(self.raw[year][month])
            except:
                self._log_error(self.errors['parser'], year, month, traceback.format_exc())


    def run(self):
        """Scrape wikipedia for current events for given years and months, parse results into dict"""
        self._get_raw()
        self._parse_raw()


    def save(self, path=None):
        path = path or f"./scrape_results/scraper_{datetime.utcnow().strftime('%Y-%m-%d_%s')}.pkl"
        helpers.save_object(path, self)


if __name__ == '__main__':
    c = CurrentEventsScraper(1999)
    c.run()
    c.save()
