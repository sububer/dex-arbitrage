import holoviews as hv
import panel as pn
import numpy as np
import hvplot.pandas

hv.extension('bokeh', 'matplotlib')
pn.extension()


# pancakeswapv2_BNBBUSD: pd.DataFrame, apeswap_BNBBUSD: pd.DataFrame
def show_arbitrage_viz(arb_results_list: list) -> None:
    ''' Displays arbitrage visuals for a two markets for a liquidity pair

    input: list of arbitrage result dicts, where each dict is of form:

    { 'info' : (pairstring, market_1, market_2),
      'df' : <pd.DataFrame>,
      'profitable_trades_min : int,
      'profitable_trades_close' : int
    }
    '''
    # Get time delta
    t_delta = np.timedelta64(60000000000, 'ns')

    # Get mkts-compared
    exch_dict = {}
    for i, result in enumerate(arb_results_list):
        exch_dict[f"{result['info'][1]}-{result['info'][2]}"] = i

    # Interactive view
    pn.extension(sizing_mode='stretch_width')
    arbitrage = pn.template.MaterialTemplate(title='Arbitrage Opportunity Analysis', theme=pn.template.theme.DarkTheme)
    arbitrage.template.theme = 'DarkTheme'
    # create list of options for widgets
    variables = ['close', 'worst case']

    # create space and widgets
    variable = pn.widgets.RadioButtonGroup(options=variables)
    exchs = pn.widgets.Select(options=list(exch_dict.keys()))
    tol = pn.widgets.FloatSlider(name="Tolerance", start=0.5, end=1, value=0.5)

    # create variables for the plots
    estimated_tolerance = 0.3 + 0.3 + 0.1 + 0.1

    @pn.depends(exchs=exchs)
    def candles_(exchs):
        arb_info_dict = arb_results_list[exch_dict[exchs]]
        pairstr,mkt1,_ =arb_info_dict['info']
        df = arb_info_dict['dataframe']
        df['time_start'] = df.datetime64 - t_delta  # rectangles start
        df['time_end'] = df.datetime64 + t_delta  # rectangles end
        df['positive'] = ((df.close_x - df.open_x) > 0).astype(int)
        _delta = np.median(np.diff(df.datetime64))
        candlestick = hv.Segments(df, kdims=['datetime64', 'low_x', 'datetime64', 'high_x']) * \
                      hv.Rectangles(df, kdims=['time_start', 'open_x', 'time_end', 'close_x'],
                                    vdims=['positive'])
        candlestick = candlestick.redim.label(Low='Values')
        return candlestick.opts(hv.opts.Rectangles(color='positive', cmap=['red', 'green'], responsive=True),
                                hv.opts.Segments(color='black', height=400, responsive=True),
                                hv.opts(bgcolor='lightgray', xlabel='Date/Hour', ylabel='Price', title=pairstr))

    @pn.depends(exchs=exchs)
    def volume_(exchs):
        arb_info_dict = arb_results_list[exch_dict[exchs]]
        pairstr,mkt1,_ =arb_info_dict['info']
        plot = arb_info_dict['dataframe'].hvplot(x="datetime64", y="volume_x", xlabel= 'Date/Hour', ylabel='Num Trades', kind="line", responsive=True)
        return plot.opts(bgcolor='lightgray',
                         title="{0} - {1}".format(pairstr, mkt1),
                         height=400,
                         responsive=True)

    @pn.depends(tol=tol, variable=variable, exchs=exchs)
    def plot_(tol, variable, exchs):
        arb_info_dict = arb_results_list[exch_dict[exchs]]
        (pairstr, mkt1, mkt2) = arb_info_dict['info']
        df = arb_info_dict['dataframe']
        # Create the underlayer plots
        p1 = hv.Curve((df['datetime64'], df['arbitrage_close']), 'Time Since Start', '% Arbitrage').opts(color='blue')
        p2 = hv.Curve((df['datetime64'], df['arbitrage_min']), 'Time Since Start', '% Arbitrage').opts(color='blue')
        p3 = hv.HLine(estimated_tolerance, label='Estimated Threshold').opts(color='red')
        arb_close = df['arbitrage_close']
        arb_min = df['arbitrage_min']
        arb_time = df['datetime64']
        if variable == 'close':
            plot = p3 * p1 * (hv.Scatter((arb_time[arb_close > tol], arb_close[arb_close > tol]),
                                         'time',
                                         '% diff',
                                         group='Group',
                                         label='Opportunity').opts(color='g', marker='+', size=10))
        else:
            plot = p3 * p2 * (hv.Scatter((arb_time[arb_min > tol], arb_min[arb_min > tol]),
                                         'time',
                                         '% diff',
                                         group='Group',
                                         label='Opportunity').opts(color='g', marker='+', size=10))
        return plot.opts(bgcolor='lightgray',
                         title="{0} -- {1} vs {2}".format(pairstr, mkt1, mkt2),
                         height=500,
                         responsive=True,
                         xlabel='Date/Hour',
                         ylabel='Spread')

    # append the widgets to the sidebar
    arbitrage.sidebar.append(tol)
    arbitrage.sidebar.append(exchs)
    arbitrage.sidebar.append(variable)

    # append the main section
    arbitrage.main.append(
        pn.Column(
            pn.Card(hv.DynamicMap(plot_), title='Arbitrage Spread W/Opportunities'),
            pn.Card(hv.DynamicMap(candles_), title='1 Minute Candle'),
            pn.Card(hv.DynamicMap(volume_), title='Pair/Exchange Volume'),
        )
    )
    arbitrage.show()
"""
def _transform_data(raw_data: pd.DataFrame):
    data = raw_data[["Date", "Open", "High", "Low", "Close", "Volume"]].copy(deep=True).rename(columns={
        "Date": "time",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })
    t_delta = timedelta(hours=1)
    data['time_start'] = data.time - 9*t_delta # rectangles start
    data['time_end'] = data.time + 9*t_delta    # rectangles end
    data['positive'] = ((data.close - data.open)>0).astype(int)
    return data

def make_candle_stick(data):
    _delta = np.median(np.diff(data.time))
    candlestick = hv.Segments(data, kdims=['time', 'low', 'time', 'high']), vdims=['positive'])
    candlestick = candlestick.redim.label(Low='Values')
    return candlestick.opts(hv.opts.Rectangles(color='positive', cmap=['red', 'green'], responsive=True),
                            hv.opts.Segments(color='black', height=400, responsive=True))

"""