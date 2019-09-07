import pickle
import requests
from bs4 import BeautifulSoup
import config


def save_object(path, obj):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)

def load_object(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def get_html(url):
    r = requests.get(url)
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
