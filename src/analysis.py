import pandas as pd
from nomics_tests import test_recent_trades, test_candles
from APIKEYS import API_KEY
import os


# Preparing dataframe 'df' to analyse 'close' column

# Dropping null values if any
def drop_null(df):
    df= df.dropna()
    return df


# Checking datatype of 'close'column and changing to float if required
def data_types_close(df):
    data_type= df['close'].dtypes
    if data_type != 'float64':
        df.loc[:,'close']= df.loc[:,'close'].astype("float")
    return df

def data_types_price(df):
    data_type= df['price'].dtypes
    if data_type != 'float64':
        df.loc[:,'price']= df.loc[:,'price'].astype("float")
    return df

# 

if __name__ == '__main__':
    os.environ["API_KEY"] = API_KEY
    recent_trades_df = test_recent_trades()
    candles_df = test_candles()
    
    recent_trades_df = drop_null(recent_trades_df)
    candles_df = drop_null(candles_df)
    
    recent_trades_df = data_types_price(recent_trades_df)
    candles_df = data_types_close(candles_df)
    
    print(recent_trades_df.head(3))
    print("---------------------------------")
    print(candles_df.head(3))