import urllib.request
import json
import os
import pandas as pd


def get_recent_trades(exchange: str, market: str, limit: int = 100) -> dict:
    api_key = os.getenv('API_KEY')
    url = "https://api.nomics.com/v1/trades?key={0}" \
          "&exchange={1}" \
          "&market={2}" \
          "&limit={3}" \
          "order=asc&from=<last>".format(api_key, exchange, market, limit)
    return json.loads(urllib.request.urlopen(url).read())


def get_candles(exchange: str, market: str, start: str, end: str) -> dict:
    api_key = os.getenv('API_KEY')
    url = "https://api.nomics.com/v1/exchange_candles?key={0}" \
          "&interval=1m" \
          "&exchange={1}" \
          "&market={2}" \
          "&start={3}T00%3A00%3A00Z&end={4}T00%3A00%3A00Z".format(api_key, exchange, market, start, end)
    return json.loads(urllib.request.urlopen(url).read())


def format_query_as_dataframe(query: dict) -> pd.DataFrame:
    df = pd.DataFrame(data=query)
    df['Datetime'] = pd.to_datetime(df['timestamp'])
    df = df.drop(['timestamp'], axis=1)
    df = df.set_index(['Datetime'])
    return df

