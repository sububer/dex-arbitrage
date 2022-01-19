from dextrader.nomics.utils import get_candles, format_query_as_dataframe, get_recent_trades
from APIKEYS import API_KEY
import os


def test_recent_trades():
    exchange = "pancakeswapv2"
    market = "0x58f876857a02d6762e0101bb5c46a8c1ed44dc16"
    query = get_recent_trades(exchange, market)
    df = format_query_as_dataframe(query)
    print(df.head(3))
    if len(df) < 1:
        print("FAILED")
        return False
    else:
        print("PASSED")
        return True


def test_candles():
    exchange = "pancakeswapv2"
    market = "0x58f876857a02d6762e0101bb5c46a8c1ed44dc16"
    start = "2022-01-18"
    end = "2022-01-19"
    query = get_candles(exchange, market, start, end)
    df = format_query_as_dataframe(query)
    print(df.head(3))
    if len(df) < 1:
        print("FAILED")
        return False
    else:
        print("PASSED")
        return True


if __name__ == '__main__':
    os.environ["API_KEY"] = API_KEY
    test_recent_trades()
    test_candles()
