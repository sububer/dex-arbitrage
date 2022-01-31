import pandas as pd
from dextrader.nomics.utils import get_candles, format_query_as_dataframe, get_recent_trades
from dextrader.nomics.pairs import get_chains, get_exchanges, get_market_pairs, get_market_query_data_for_pair
import os
import fire
import questionary
import datetime
import itertools
import re
from dextrader.analysis.arbitrage import generate_arbitrage_summary, debug_arbitrage_results
from pathlib import Path
from dextrader.vis.arbitrage_holoview import show_arbitrage_viz
# NOMICS-API uncomment if running via API
#from APIKEYS import API_KEY

# cli helpers
def display_exchanges(exch_list):
    print('Exchanges:')
    for exch in exch_list:
        print(f"\t{exch}")


def display_pairs(pair_list):
    print('Pairs:')
    for pair in pair_list:
        print(f"\t{pair}")


def display_data_avail(pair: str) -> dict:
    DATA_DIR = Path('../datasets/')
    matching_data_files = [f for f in os.listdir(DATA_DIR) if f.startswith(pair)]

    if len(matching_data_files) > 0:
        print("Existing pulled data...")
        dates_avail = dict()
        for datafile in sorted(matching_data_files):
            date_avail = "".join(datafile.split('-')[1:4])
            if date_avail in dates_avail:
                dates_avail[date_avail].append(datafile)
            else:
                dates_avail[date_avail] = [datafile]
            print(f"\t{datafile}")
        return dates_avail
    else:
        print(f"\nNo existing data available for pair: {pair}")
        return dict()


def get_recent_csv_file_paths_for_pair(pair: str) -> list:
    DATA_DIR = Path('../datasets/')
    date_str = datetime.datetime.today().strftime('%Y-%m-%d')
    recent_data_files = [f for f in os.listdir(DATA_DIR) if f.startswith(f"{pair}-{date_str}")]

    return sorted(recent_data_files)


def update_and_persist_trade_data(chain: str, pair: str) -> list:
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
    generated_csv_file_list = list()

    for pair_key, market_info in market_data.items():
        for exch, market_hash in market_info:
            csv_dir = '../datasets/'
            csvfilename = f"{pair}-{end_date}-{exch}.csv"
            csvfilepath = Path(csv_dir + csvfilename)

            # get market data
            print(f"Pulling {pair_key} data for exchange {exch} ...")
            query = get_candles(exchange=exch, market=market_hash, start=start_date, end=end_date)
            updated_data_df = format_query_as_dataframe(query)
            updated_data_df.to_csv(csvfilepath)
            generated_csv_file_list.append(csvfilename)
    
    return sorted(generated_csv_file_list)


def get_market_name(csvfilename: str) -> str:
    match = re.search('.*-.*-(.*).csv$', csvfilename)
    return match.group(1)


def do_arbitrage_analysis_for_pair(pair: str, csvfiles: list):
    print(f"Running analysis for pair: {pair}")
    data_files_list = csvfiles[:]

    if len(data_files_list) == 0:
        data_files_list = get_recent_csv_file_paths_for_pair(pair)

    # list of arbitrage results for each analyzed market pair
    arbitrage_results = []

    # analyze 2 market data sets at a time
    for market_pair in itertools.combinations(data_files_list, 2):
        # call generate_arbitrage_data_between_markets()
        csv_dir = '../datasets/'
        market_a_file_name = market_pair[0]
        market_b_file_name = market_pair[1]
        
        market_a_name = get_market_name(market_a_file_name)
        market_b_name = get_market_name(market_b_file_name)
        
        market_a_file_path = Path(csv_dir + market_a_file_name)
        market_b_file_path = Path(csv_dir + market_b_file_name)

        market_a_df = pd.read_csv(market_a_file_path, infer_datetime_format=True, parse_dates=True)
        market_b_df = pd.read_csv(market_b_file_path, infer_datetime_format=True, parse_dates=True)

        arbitrage_data_for_markets = generate_arbitrage_summary(market_a_df, market_b_df, pair, market_a_name, market_b_name)
        debug_arbitrage_results(arbitrage_data_for_markets)
        arbitrage_results.append(arbitrage_data_for_markets)

    return arbitrage_results


## call Jaime's viz
def generate_viz_from_arbitrage_results(arb_results: list) -> None:
    print("Generating viz...")
    show_arbitrage_viz(arb_results)


# main cli flow
def run():
    # NOMICS-API uncomment if running via API
    # os.environ["API_KEY"] = API_KEY
    
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


    dates_avail = display_data_avail(pair_selected)

    # get new data?
    updated_csv_filenames = []
    data_update_q = "Generate new csv data for pair? -- Requires NOMICS API setup!!"
    update_pair_data = questionary.confirm(data_update_q).ask()
    if update_pair_data:
        updated_csv_filenames = update_and_persist_trade_data(chain_selected, pair_selected)
    elif len(dates_avail):
        file_q = "Select a file to analyze"
        selected_date = questionary.select(message=file_q, choices=list(dates_avail.keys())).ask()
        updated_csv_filenames = dates_avail[selected_date]
    else:
        raise ValueError("You don't have any cached files. Select (yes) to pull new data with nomics API.")

    # analyze?
    arbitrage_result_list = []
    run_analysis_q = f"Run analysis for pair {pair_selected} (y/n)"
    run_analysis = questionary.confirm(message=run_analysis_q).ask()
    if run_analysis:
        arbitrage_result_list = do_arbitrage_analysis_for_pair(pair_selected, updated_csv_filenames)

    # viz?
    run_viz_q = f"Generate viz for pair {pair_selected} (y/n)"
    run_viz = questionary.confirm(message=run_viz_q).ask()
    if run_viz:
        generate_viz_from_arbitrage_results(arbitrage_result_list)




if __name__ == '__main__':
    # a user can view available chains, avail pairs on selected chain
    # select a pair to update data, run analysis, run viz

    # app loop
    fire.Fire(run)