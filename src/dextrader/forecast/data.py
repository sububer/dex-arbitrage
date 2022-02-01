import pandas as pd
from pytorch_forecasting import TimeSeriesDataSet


def get_dataset(csv_path: str) -> TimeSeriesDataSet:
        df = pd.read_csv(csv_path, infer_datetime_format=True, parse_dates=True)
        df['timeindex'] = pd.to_datetime(df['Datetime'], unit='ns').apply(lambda x: x.value)
        df['timeindex'] -= df['timeindex'][0]
        df['timeindex'] /= 10**9
        df['timeindex'] /= 60
        df['timeindex'] = df['timeindex'].astype(int)

        print(df.head())
        columns = ["low", "open", "close", "high", "volume", "num_trades"]
        dataset = TimeSeriesDataSet(
            df,
            group_ids=columns,
            target=columns,
            time_idx="timeindex",
            min_encoder_length=0,
            max_encoder_length=100,
            min_prediction_length=1,
            max_prediction_length=5,
            allow_missing_timesteps=True,
            time_varying_unknown_reals=columns,
        )
        return dataset

"""
test = '../datasets/january-AVAXUSDT-pangolin.csv'
test_dataset = get_dataset(test)
dataloader = test_dataset.to_dataloader(batch_size=4)
x, y = next(iter(dataloader))
print("x =", x)
print("\ny =", y)
print("\nsizes of x =")
for key, value in x.items():
    print(f"\t{key} = {value[0].size()}")
"""