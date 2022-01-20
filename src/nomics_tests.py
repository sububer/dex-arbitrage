from dextrader.nomics.utils import get_candles, format_query_as_dataframe, get_recent_trades
from dextrader.nomics.pairs import nomics
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


def test_pairs():
    for chain_id in nomics["chain"].keys():
        for exchange in nomics["chain"][chain_id]["exchanges"]:
            for market in nomics["chain"][chain_id]["exchanges"][exchange]["markets"].keys():
                hash = nomics["chain"][chain_id]["exchanges"][exchange]["markets"][market]
                print(chain_id, exchange, market, hash)
    start = "2022-01-18"
    end = "2022-01-19"
    query = get_candles(exchange, hash, start, end)
    df = format_query_as_dataframe(query)
    print(df.head(3))
    print("PASSED")


if __name__ == '__main__':
    os.environ["API_KEY"] = API_KEY
    test_recent_trades()
    test_candles()
    test_pairs()
