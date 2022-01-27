import pandas as pd
import holoviews as hv
from holoviews import dim, opts
hv.extension('bokeh', 'matplotlib')
import numpy as np
import panel as pn
pn.extension()


# pancakeswapv2_BNBBUSD: pd.DataFrame, apeswap_BNBBUSD: pd.DataFrame
def show_arbitrage_viz(arb_results_list: list) -> None:
    ''' Displays arbitrage visuals for a two markets for a liquidity pair

    input: list of arbitrage result dicts, where each dict is of form:

    { 'info' : (pairstring, market_1, market_2),
      'arbitrage' : <pd.DataFrame>,
      'combined_df : <pd.DataFrame>, 
      'spread_return_df' : <pd.DataFrame>,
      'profitable_trades_df': <pd.DataFrame>
    }
    '''
    # for now, just use whatever is first element in the list of results and draw that
    # dict keys are: dict_keys(['info', 'arbitrage', 'combined_df', 'spread_return_df', 'profitable_trades'])
    arb_info_dict = arb_results_list[0]

    # unpack info tuple ('BNBBUSD', 'apeswap', 'pancakeswapv2')
    (pairstr, mkt1, mkt2) = arb_info_dict['info']

    '''
    # dataframes
    arbitrage_df = arb_info_dict['arbitrage'].dropna()
    print('arbitrage_df')
    print(arbitrage_df.head(3))

    combined_df = arb_info_dict['combined_df']
    combined_df['date_time'] = combined_df.index
    print('combined_df')
    print(combined_df.head(3))

    spread_return_df = arb_info_dict['spread_return_df']
    print('spread_return_df')
    print(spread_return_df.head(3))

    # list
    profitable_trades_df = arb_info_dict['profitable_trades_df']
    print(profitable_trades_df)
    '''
    # Interactive view
    # load the template 
    arbitrage = pn.template.MaterialTemplate(title='Arbitrage')



    # calculate which decentralize exchange has the higher value and drop the NA 
    # apeswap_BNBBUSD['APE2PS'] = (pancakeswapv2_BNBBUSD['low'] - apeswap_BNBBUSD['high'])/apeswap_BNBBUSD['high']

    # pancakeswapv2_BNBBUSD['PS2APE'] = (apeswap_BNBBUSD['low'] - pancakeswapv2_BNBBUSD['high'])/pancakeswapv2_BNBBUSD['high']

    # pancakeswapv2_BNBBUSD.loc[pancakeswapv2_BNBBUSD['PS2APE'] < 0, 'PS2APE'] = 0

    # apeswap_BNBBUSD.loc[apeswap_BNBBUSD['APE2PS'] < 0, 'APE2PS'] = 0

    # apeswap_BNBBUSD = apeswap_BNBBUSD.dropna()
    # pancakeswapv2_BNBBUSD = pancakeswapv2_BNBBUSD.dropna()

    # create max arbitrage and timestamps list and add values to them

    max_arbitrage = []

    timestamps = []

    for i,j,k in zip(combined_df['df1_close'], combined_df['df2_close'], combined_df['date_time']):
        if i > j:
            max_arbitrage.append(i * 100.)
            timestamps.append(np.datetime64(pd.to_datetime(k).value,'ns'))
        else:
            max_arbitrage.append(j * 100.)
            timestamps.append(np.datetime64(pd.to_datetime(k).value,'ns'))


    # create list of options for widgets 
    variables = ['low', 'open', 'high', 'close', 'volume']
    pairs = []
    pairs.append(pairstr)

    # create space and widgets
    xs = np.linspace(0, 100)
    tol = pn.widgets.FloatSlider(name="Tolerance", start=0, end=10, value=2)
    time = pn.widgets.FloatSlider(name="Time", start=0, end=np.pi)
    pair = pn.widgets.RadioButtonGroup(options=pairs)
    variable = pn.widgets.Select(options=variables)
    diff1 = pn.widgets.FloatSlider(name="% Arbitrage", start=0.5, end=1, value=0.5)

    # create variables for the plots
    estimated_tolerance = 0.3 + 0.3 + 0.1 + 0.1
    diff = pd.Series(max_arbitrage)
    time = pd.Series(timestamps)


    # Create the underlayer plots
    p1 = hv.Curve((time, diff), 'Time Since Start', '% Arbitrage')
    p2 = hv.HLine(estimated_tolerance, label='Estimated Threshold')

    @pn.depends(diff1=diff1)
    def plot_(diff1):
        return p1.opts(color='b')*p2.opts(color='r')*hv.Scatter((time[diff>diff1], diff[diff >diff1]),'time','% diff', group='Group', label='Arbitrage').opts(opts.Scatter(marker='x',color='g',size=40)) 

    # append the widgets to the sidebar
    #arbitrage.sidebar.append(tol)
    #arbitrage.sidebar.append(time)
    arbitrage.sidebar.append(pair)
    arbitrage.sidebar.append(variable)
    arbitrage.sidebar.append(diff1)


    #append the main section
    arbitrage.main.append(
        pn.Row(
            pn.Card(hv.DynamicMap(plot_), title='Arbitrage Opportunities'),
            
        )
    )
    
    arb_spread = pn.widgets.FloatSlider(name='arbitrage spread', start=0.5, end=1, value=0.5)
    
    @pn.depends(arb_spread=arb_spread)
    def arbitrage_spread(arb_spread):
        return hv.Curve(arbitrage_df['close'], 'Arbitrage spread')
    arbitrage.main.append(
        pn.Row(
            pn.Card(hv.DynamicMap(arbitrage_spread), title='Arbitrage spread'),
        )
    )

    # call the UI 
    arbitrage.show()



if __name__ == '__main__':
    print('viz module testing...')
    # pancakeswapv2_BNBBUSD = pd.read_csv(Path('../datasets/BNBBUSD-2022-01-25-pancakeswapv2.csv'),
    # parse_dates=True,
    # infer_datetime_format=True)
    
    # apeswap_BNBBUSD = pd.read_csv(Path('../datasets/BNBBUSD-2022-01-25-apeswap.csv'),
    # parse_dates=True,
    # infer_datetime_format=True)

    # show_arbitrage_viz(pancakeswapv2_BNBBUSD, apeswap_BNBBUSD)
