import holoviews as hv
import panel as pn


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
    # for now, just use whatever is first element in the list of results and draw that
    # dict keys are: dict_keys(['info', 'dataframe', 'profitable_trades_min', 'profitable_trades_close'])
    arb_info_dict = arb_results_list[0]

    # unpack info tuple example: ('BNBBUSD', 'apeswap', 'pancakeswapv2')
    (pairstr, mkt1, mkt2) = arb_info_dict['info']

    # Interactive view
    arbitrage = pn.template.MaterialTemplate(title='Arbitrage')

    # create list of options for widgets
    variables = ['close', 'worst case']

    # create space and widgets
    variable = pn.widgets.Select(options=variables)
    tol = pn.widgets.FloatSlider(name="Tolerance", start=0.5, end=1, value=0.5)

    # create variables for the plots
    estimated_tolerance = 0.3 + 0.3 + 0.1 + 0.1
    df = arb_info_dict['dataframe']

    # Create the underlayer plots
    p1 = hv.Curve((df['datetime64'], df['arbitrage_close']), 'Time Since Start', '% Arbitrage').opts(color='blue')
    p2 = hv.Curve((df['datetime64'], df['arbitrage_min']), 'Time Since Start', '% Arbitrage').opts(color='blue')
    p3 = hv.HLine(estimated_tolerance, label='Estimated Threshold').opts(color='red')
    arb_close = df['arbitrage_close']
    arb_min = df['arbitrage_min']
    arb_time = df['datetime64']

    @pn.depends(tol=tol, variable=variable)
    def plot_(tol, variable):
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
        return plot.opts(width=800,
                         height=500,
                         bgcolor='lightgray',
                         title="Arbitrage {0} for {1} vs {2}".format(pairstr, mkt1, mkt2))

    # append the widgets to the sidebar
    arbitrage.sidebar.append(tol)
    arbitrage.sidebar.append(variable)

    # append the main section
    arbitrage.main.append(
        pn.Row(
            pn.Card(hv.DynamicMap(plot_), title='Arbitrage Opportunities'),

        )
    )
    arbitrage.show()
