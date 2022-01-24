from email import message
from random import choices
from time import strftime
import pandas as pd
from dextrader.nomics.utils import get_candles, format_query_as_dataframe, get_recent_trades
from dextrader.nomics.pairs import get_chains, get_exchanges, get_market_pairs, get_market_query_data_for_pair
import os
import fire
import questionary
import datetime
import sys
from pathlib import Path
from APIKEYS import API_KEY


# cli helpers
def display_exchanges(exch_list):
    print('Exchanges:')
    for exch in exch_list:
        print(f"\t{exch}")

def display_pairs(pair_list):
    print('Pairs:')
    for pair in pair_list:
        print(f"\t{pair}")

def display_data_avail(pair: str) -> None:
    DATA_DIR = Path('../datasets/')
    matching_data_files = [f for f in os.listdir(DATA_DIR) if f.startswith(pair)]

    if len(matching_data_files) > 0:
        print("Existing pulled data...")
        for datafile in matching_data_files:
            print(f"\t{datafile}")
    else:
        print(f"No existing data available for pair: {pair}")


def udpate_and_persist_trade_data(chain, pair):
    ''' pulls new csv data for all exchange/markets available for a given pair

    in: pair string eg USDCBUSD
    out: .csv file writting to ../dataset/pairid-exchangeid-pulldate.csv
         # eg: USDCBUSD-pancakeswapv2-2022-01-24.csv
    '''
    print(f"Updating and saving csv data for chain: {chain} pair: {pair}")
    
    # default start/end dates
    # 1 day ago, eg '2022-01-23'
    start_date = (datetime.datetime.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
    
    # today, eg '2022-01-24'
    end_date = datetime.datetime.today().strftime('%Y-%m-%d')

    # get market query data for pair
    market_data = get_market_query_data_for_pair(chain, pair)

    # get and persist updated data
    for pair_key, market_info in market_data.items():
        for exch, market_hash in market_info:
            csv_dir = '../datasets/'
            csvfilename = f"{pair}-{exch}-{end_date}.csv"
            csvfilepath = Path(csv_dir + csvfilename)

            # get market data
            print(f"Pulling {pair_key} data for exchange {exch} ...")
            query = get_candles(exchange=exch, market=market_hash, start=start_date, end=end_date)
            updated_data_df = format_query_as_dataframe(query)
            updated_data_df.to_csv(csvfilepath)




## call Shivangi's analysis code 
def do_arbitrage_analysis_for_pair(pair):
    print(f"Running analysis for pair: {pair}")


## call Jaime's viz
def generate_arbitrage_viz_from_analysis_df():
    print("Generating viz...")

    


# main cli flow
def run():
    os.environ["API_KEY"] = API_KEY
    # udpate_and_persist_trade_data('bsc', 'USDTBUSD')

    print('Welcome to DEX Arbitrage App.\nYou can select liquidity pool pairs across multiple exchanges to discover arbitrage opportunities.\n')

    # select from avail chains
    chains_avail = get_chains()
    chain_q = "Select a chain to explore pairs on:"
    chain_selected = questionary.select(message=chain_q, choices=chains_avail).ask()

    exchanges_avail = get_exchanges(chain_selected)
    pairs_avail = get_market_pairs(chain_selected)

    display_exchanges(exchanges_avail)
    display_pairs(pairs_avail)

    pair_q = "\nWhat pair would you like to explore?"
    pair_selected = questionary.select(message=pair_q, choices=pairs_avail).ask()


    display_data_avail(pair_selected)

    # update?
    data_update_q = "Update new pair data? (y/n)"
    update_pair_data = questionary.confirm(data_update_q).ask()
    if update_pair_data:
        udpate_and_persist_trade_data(chain_selected, pair_selected)

    # analyze?
    run_analysis_q = f"Run analysis for pair {pair_selected} (y/n)"
    run_analysis = questionary.confirm(message=run_analysis_q).ask()
    if run_analysis:
        do_arbitrage_analysis_for_pair(pair_selected)

    
    # viz?
    run_viz_q = f"Generate viz for pair {pair_selected} (y/n)"
    run_viz = questionary.confirm(message=run_viz_q).ask()
    if run_viz:
        generate_arbitrage_viz_from_analysis_df()




if __name__ == '__main__':
    # a user can view available chains, avail pairs on selected chain
    # select a pair to update data, run analysis, run viz

    # app loop
    fire.Fire(run)