import pandas as pd
import numpy as np
from pathlib import Path
import pickle


def generate_arbitrage_summary(df1: pd.DataFrame,
                               df2: pd.DataFrame,
                               pair: str,
                               mkt1: str,
                               mkt2: str,
                               threshold: float = 0.8) -> dict:
    '''
    :param df1: dataframe of market A data from nomics candles api data for timeframe X, for given pair
    :param df2: dataframe of market B data from nomics candles api data from timeframe X, for given pair
    :param pair: string identifier for pair that data represents
    :param mkt1: string identifier for pair market 1
    :param mkt2: string identifier for pair market 2
    :param threshold: threshold for considering trades profitable
    :return: arbitrage_results (dict): in the form:
                { 'info' : [pairstring, market_1, market_2],
                  'dataframe' : <pd.DataFrame>,
                  'profitable_trades_min' : int
                  'profitable_trades_close' : int
                }
    '''

    # Merge data with shared timestamps
    merged_data = pd.merge(df1, df2, how='outer', on='Datetime')

    # Convert data to numeric data
    cols = ['low_x', 'low_y', 'open_x', 'open_y', 'close_x', 'close_y', 'high_x', 'high_y']
    merged_data[cols] = merged_data[cols].apply(pd.to_numeric, errors='coerce')

    # arbitrage
    merged_data['arbitrage'] = (merged_data['close_x'] - merged_data['close_y']).abs()

    # Compute arbitrage from close values
    merged_data = merged_data.assign(arbitrage_close=
                                     lambda x: np.where(x['close_x'] > x['close_y'],
                                                        (x['close_x'] - x['close_y'])/x['close_x'],
                                                        (x['close_y'] - x['close_x'])/x['close_y']))
    merged_data['arbitrage_close'] *= 100

    # Compute min arbitrage (worst case)
    merged_data = merged_data.assign(arbitrage_min=
                                     lambda x: np.where(x['open_x'] > x['open_y'],
                                                        (x['low_x'] - x['high_y'])/x['open_y'],
                                                        (x['low_y'] - x['high_x'])/x['open_x']))
    merged_data['arbitrage_min'] *= 100

    # Find trades that exceed the profit threshold
    merged_data = merged_data.assign(profitable_trades_close=
                                     lambda x: x['arbitrage_close'] > threshold)
    merged_data = merged_data.assign(profitable_trades_min=
                                     lambda x: x['arbitrage_min'] > threshold)

    # Get time in int64
    merged_data['datetime64'] = merged_data['Datetime'].astype('datetime64[ns]')

    arbitrage_results = dict()
    arbitrage_results['info'] = (pair, mkt1, mkt2)
    arbitrage_results['dataframe'] = merged_data
    arbitrage_results['profitable_trades_min'] = np.sum(merged_data['profitable_trades_min'].to_numpy().astype(int))
    arbitrage_results['profitable_trades_close'] = np.sum(merged_data['profitable_trades_close'].to_numpy().astype(int))
    return arbitrage_results


def save_analysis(arbitrage: dict) -> None:
    pckl_dir = '../saved/'
    pcklfilename = f"{arbitrage['info'][0]}-{arbitrage['info'][1]}-{arbitrage['info'][2]}.pkl"
    pcklfilepath = Path(pckl_dir + pcklfilename)
    with open(pcklfilepath, 'wb') as handle:
        pickle.dump(arbitrage, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return


def debug_arbitrage_results(arbitrage_results: dict) -> None:
    profitable_trades_min = arbitrage_results['profitable_trades_min']
    profitable_trades_close = arbitrage_results['profitable_trades_close']
    (pair, mkt1, mkt2) = arbitrage_results['info']
    arbitrage_results = arbitrage_results['dataframe']
    mkt1_columns = ['Datetime', 'low_x', 'open_x', 'close_x', 'high_x']
    mkt2_columns = ['Datetime', 'low_y', 'open_y', 'close_y', 'high_y']
    print(f"DEBUG ANALYSIS INFO\n")
    print(f"pair: {pair}")
    print(f"\tmarket_1: {mkt1}")
    print(f"\tmarket_2: {mkt2}")
    print(f"Exchange 1 Dataframe:")
    print(arbitrage_results[mkt1_columns].head(3))
    print("---------------------------------")
    print(f"Exchange 2 Dataframe:")
    print(arbitrage_results[mkt2_columns].head(3))
    print("---------------------------------")
    print(f"Arbitrage trades preview:\n{arbitrage_results[['Datetime','arbitrage']].head()}")
    print("---------------------------------")
    print(f"Arbitrage summary:\n{arbitrage_results['arbitrage'].describe()}")
    print("---------------------------------")
    print(f"Arbitrage Spread returns (worst) preview:\n{arbitrage_results['arbitrage_min'].head()}")
    print("---------------------------------")
    print(f"Arbitrage Spread returns (close) preview:\n{arbitrage_results['arbitrage_close'].head()}")
    print("---------------------------------")
    print(f"Returns Summary Worst:\n{arbitrage_results['arbitrage_min'].describe()}")
    print("---------------------------------")
    print(f"Returns Summary Close:\n{arbitrage_results['arbitrage_close'].describe()}")
    print("---------------------------------")
    print(f"Num Profitable trades worst:\n{profitable_trades_min}")
    print("---------------------------------")
    print(f"Num Profitable trades close:\n{profitable_trades_close}")
