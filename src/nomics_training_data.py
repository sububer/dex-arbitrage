import os
from dextrader.nomics.utils import get_candles, format_query_as_dataframe
from dextrader.nomics.pairs import nomics
from APIKEYS import API_KEY
from tqdm import tqdm

from pathlib import Path
os.environ["API_KEY"] = API_KEY

market = "AVAXUSDT"
exchanges = ["pangolin", "sushiswap_avalanche", "traderjoe"]
hashes = [nomics["chain"]["avalanche"]["exchanges"][exchange]["markets"][market] for exchange in exchanges]
df = dict()
csv_dir = '../datasets/'
for i in tqdm(range(1, 31)):
    start_date = "2022-01-{0:02d}".format(i)
    end_date = "2022-01-{0:02d}".format(i+1)
    for exchange, hash in zip(exchanges, hashes):
        query = get_candles(exchange, hash, start_date, end_date)

        if exchange not in df:
            df[exchange] = format_query_as_dataframe(query)
        else:
            df[exchange] = df[exchange].append(format_query_as_dataframe(query))

for exchange in exchanges:
    csv_filename = f"january-{market}-{exchange}.csv"
    csv_filepath = Path(csv_dir + csv_filename)
    df[exchange].drop_duplicates().to_csv(csv_filepath)
    print(exchange, len(df[exchange]), 'samples')
