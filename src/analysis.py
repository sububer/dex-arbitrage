import pandas as pd
from nomics_tests import test_candles_pancake,test_candles_ape
from APIKEYS import API_KEY
import os


## Preparing dataframe 'df' to analyse 'close' column from candles data

# Dropping null values if any
def drop_null(df_list):
    for df in df_list:
        df= df.dropna()
    return df_list


# Checking datatype of 'close'column and changing it to float if required
def data_types_close(df_list):
    for df in df_list:
        data_type= df['close'].dtypes
        if data_type != 'float64':
            df.loc[:,'close']= df.loc[:,'close'].astype("float")
    return df_list

# Selecting only 'close' column with index'datetime' for analysis
def fetch_close_from_df(df_list):
    df_list_new = []
    for df in df_list:
        df = df.loc[:,'close']
        df = pd.DataFrame(df)
        df_list_new.append(df)
    return df_list_new

# calculating arbitrage opportunities (taking absolute value of difference in close prices between the exchanges)

def arbitrage_spread(df1,df2):
    arbitrage = (df1-df2)
    return arbitrage.abs()


# calculating Potential spread return

def combine_df(df1,df2):
    #df1 = pd.DataFrame(df1)
    #df2 = pd.DataFrame(df2)
    df1 = df1.rename(columns={"close": "df1_close"})
    df2 = df2.rename(columns={"close": "df2_close"})
    combined_df = pd.concat([df1,df2], axis='columns', join='inner')
    return combined_df


def get_spread_return(df):
    spread_return={}
    for index, row in df.iterrows():
        df1_close = row['df1_close']
        df2_close = row['df2_close']
        if df1_close > df2_close:
            spread_return[index] = (((df1_close - df2_close)/df2_close)*100)
        elif df1_close < df2_close:
            spread_return[index] =(((df2_close - df1_close)/df1_close)*100)
    return pd.DataFrame.from_dict(spread_return, orient='index')
            
    
# Profitable trades after estimated_tolerance of 0.8(0.3 + 0.3 + 0.1 + 0.1)

def get_profitable_trades(df):
    df.columns= ['returns']
    profitable_trades_df=[]
    net_profit= df['returns']- 0.8
    for index, row in df.iterrows():
        if row['returns'] > 0.8:
             profitable_trades_df.append(row['returns']) 
    return pd.DataFrame(profitable_trades_df, columns= ['returns'])


def generate_arbitrage_data_between_markets(df1: pd.DataFrame, df2: pd.DataFrame, pair: str, mkt1: str, mkt2: str) -> dict:
    '''
    inputs:
    df1 : dataframe of market A data from nomics candles api data for timeframe X, for given pair
    df2 : dataframe of market B data from nomics candles api data from timeframe X, for given pair
    pair : string identifier for pair that data represents

    outputs:
    arbitrage_results (dict): in the form:
    { 'info' : [pairstring, market_1, market_2],
      'arbitrage' : <pd.DataFrame>,
      'combined_df : <pd.DataFrame>, 
      'spread_return_df' : <pd.DataFrame>,
      'profitable_trades_df': <pd.DataFrame>
    }
    '''
    arbitrage_results = dict()
    
    df_list= [df1,df2]
    
    df_list=drop_null(df_list)
    
    df_list = data_types_close(df_list)
    
    df_list = fetch_close_from_df(df_list)

    arbitrage_results['info'] = (pair, mkt1, mkt2)
    
    df_1 = df_list[0]
    df_2 = df_list[1]
    
    arbitrage = arbitrage_spread(df_1,df_2)
    arbitrage_results['arbitrage'] = arbitrage

    combined_df = combine_df(df_1,df_2)
    arbitrage_results['combined_df'] = combined_df
    
    spread_return_df = get_spread_return(combined_df)
    arbitrage_results['spread_return_df'] = spread_return_df
    
    profitable_trades_df = get_profitable_trades(spread_return_df)
    arbitrage_results['profitable_trades_df']= profitable_trades_df

    #### DEBUG INFO
    print(f"DEBUG ANALYSIS INFO\n")
    print(f"pair: {pair}")
    print(f"\tmarket_1: {mkt1}")
    print(f"\tmarket_2: {mkt2}")
    print(f"Exchange 1 Dataframe:")
    print(df_1.head(3))
    print("---------------------------------")
    print(f"Exchange 2 Dataframe:")
    print(df_2.head(3))
    print("---------------------------------")
    print(f"Arbitrage trades preview:\n{arbitrage.head()}")
    print("---------------------------------")
    print(f"Arbitrage summary:\n{arbitrage.describe()}")
    print("---------------------------------")
    print(f"Combined dataframe preview:\n{combined_df.head()}")
    print("---------------------------------")
    print(f"Arbitrage Spread returns preview:\n{spread_return_df.head()}")
    print("---------------------------------")
    print(f"Returns Summary:\n{spread_return_df.describe()}")
    print("---------------------------------")
    print(f"Profitable trades summary:\n{profitable_trades_df.describe()}")


    

    return arbitrage_results


if __name__ == '__main__':
    os.environ["API_KEY"] = API_KEY
    print('analysis module')
