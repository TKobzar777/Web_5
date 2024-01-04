import asyncio
import logging
import sys

import aiohttp

from datetime import datetime, timedelta
from typing import AsyncIterator


CURRENCIES_AVAILABLE = ('USD', 'EUR', 'CHF', 'GBP', 'PLZ', 'SEK', 'XAU', 'CAD')


async def request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    return r
                logging.error(f"Error status {response.status} for {url}")
        except aiohttp.ClientConnectorError as e:
            logging.error(f"Connection error {url}: {e}")
        return None


async def get_requests(params_request: dict) -> AsyncIterator:
    url = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='
    current_datetime = datetime.now()
    days = params_request['days']
    cur = params_request['cur']
    for i in range(days):
        date_request = current_datetime.strftime('%d.%m.%Y')
        url_date = ''.join([url, date_request])
        current_datetime -= timedelta(days=1)
        yield get_exchange(url_date, cur)


async def get_exchange(url: str, list_required_currencies: list):
    dict_result = {}
    dict_currency = {}
    dict_of_costs = {}

    resp = await request(url)
    data_resp = resp['date']
    list_currencies_resp = resp['exchangeRate']

    for el in list_currencies_resp:
        if el['currency'] in list_required_currencies:
            dict_of_costs['sale'] = el['saleRateNB']
            dict_of_costs['purchase'] = el['purchaseRateNB']
            dict_currency[el['currency']] = dict_of_costs
    dict_result[data_resp] = dict_currency
    return dict_result


async def main(requests: AsyncIterator):
    result = []

    async for req in requests:
        result.append(req)
    return await asyncio.gather(*result)


def get_params():
    params = {'days': 0,'cur': ['USD', 'EUR'] }
    l = len(sys.argv)
    if l < 2:
        return params
    i = 1
    while i < l:
        if sys.argv[1].isdigit():
            ds = int(sys.argv[1])
            if ds < 10:
                params['days'] = ds
        else:
            if sys.argv[1].upper() in CURRENCIES_AVAILABLE and not sys.argv[1].upper() in params['cur']:
                params['cur'].append(sys.argv[1].upper())
        i += 1
    return params


if __name__ == "__main__":
    params = get_params()
    print(params)
    users = asyncio.run(main(get_requests(params)))
    print(users)
