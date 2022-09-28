# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_utils.ipynb.

# %% auto 0
__all__ = ['df', 'mtd', 'qtd', 'ytd', 'pandas_date', 'pandas_current_month', 'multi_shift', 'to_returns', 'to_prices',
           'log_returns', 'to_log_returns', 'exponential_stdev', 'rebase', 'group_returns', 'aggregate_returns',
           'to_excess_returns', 'prepare_prices', 'prepare_returns', 'download_returns', 'prepare_benchmark',
           'round_to_closest', 'file_stream', 'make_index', 'make_portfolio']

# %% ../nbs/00_utils.ipynb 3
def mtd(df):
    """Restrict a dataframe to only month to date"""
    return df[df.index >= _dt.datetime.now(
    ).strftime('%Y-%m-01')]

# %% ../nbs/00_utils.ipynb 4
def qtd(df):
    """Restrict a dataframe to only quarter to date (quarters starting in Jan, Apr, Jun, Oct) """
    return df[df.index >= _dt.datetime.now(
    ).strftime('%Y-%m-01')]

# %% ../nbs/00_utils.ipynb 5
def ytd(df):
    """Restrict a dataframe to only year to date"""
    return df[df.index >= _dt.datetime.now(
    ).strftime('%Y-01-01')]

# %% ../nbs/00_utils.ipynb 7
def pandas_date(df, dates):
    """Filters a dataframe (with date as the index), to its values on specific days"""
    if not isinstance(dates, list):
        dates = [dates]
    return df[df.index.isin(dates)]

# %% ../nbs/00_utils.ipynb 9
def pandas_current_month(df):
    """an alternative method to mtd. remove?"""
    n = _dt.datetime.now()
    daterange = _pd.date_range(_dt.date(n.year, n.month, 1), n)
    return df[df.index.isin(daterange)]

# %% ../nbs/00_utils.ipynb 10
def multi_shift(df, shift=3):
    """Get last N rows relative to another row in dataframe of values, with a sorted index"""
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)

    dfs = [df.shift(i) for i in np.arange(shift)]
    for ix, dfi in enumerate(dfs[1:]):
        dfs[ix + 1].columns = [str(col) for col in dfi.columns + str(ix + 1)]
    return pd.concat(dfs, axis = 1, sort=True)

# %% ../nbs/00_utils.ipynb 11
df = pd.DataFrame({
    'value': [10,15,13,7,12,6],
    'Date': ['1999-10-15','1999-10-16','1999-10-17','1999-10-18','1999-10-19','1999-10-20']
})
df = df.set_index('Date')
multi_shift(df,3)

# %% ../nbs/00_utils.ipynb 12
def to_returns(prices, rf=0.):
    """Calculates the simple arithmetic returns of a price series"""
    return _prepare_returns(prices, rf)

# %% ../nbs/00_utils.ipynb 13
def to_prices(returns, base=1e5):
    """Converts returns series to price data"""
    returns = returns.copy().fillna(0).replace(
        [np.inf, -np.inf], float('NaN'))

    return base + base * stats.compsum(returns)

# %% ../nbs/00_utils.ipynb 16
def log_returns(returns, rf=0., nperiods=None):
    """Shorthand for to_log_returns"""
    return to_log_returns(returns, rf, nperiods)

# %% ../nbs/00_utils.ipynb 17
def to_log_returns(returns, rf=0., nperiods=None):
    """Converts returns series to log returns"""
    returns = prepare_returns(returns, rf, nperiods)
    try:
        return np.log(returns+1).replace([np.inf, -np.inf], float('NaN'))
    except Exception:
        return 0.

# %% ../nbs/00_utils.ipynb 18
def exponential_stdev(returns, window=30, is_halflife=False):
    """Returns series representing exponential volatility of returns"""
    returns = _prepare_returns(returns)
    halflife = window if is_halflife else None
    return returns.ewm(com=None, span=window,
                       halflife=halflife, min_periods=window).std()

# %% ../nbs/00_utils.ipynb 19
def rebase(prices, base=100.):
    """
    Rebase all series to a given intial base.
    This makes comparing/plotting different series together easier.
    Args:
        * prices: Expects a price series/dataframe
        * base (number): starting value for all series.
    """
    return prices.dropna() / prices.dropna().iloc[0] * base

# %% ../nbs/00_utils.ipynb 20
def group_returns(returns, groupby, compounded=True):
    """Summarize returns
    group_returns(df, df.index.year)
    group_returns(df, [df.index.year, df.index.month])
    """
    if compounded:
        return returns.groupby(groupby).apply(_stats.comp)
    return returns.groupby(groupby).sum()

# %% ../nbs/00_utils.ipynb 21
def aggregate_returns(returns, period=None, compounded=True):
    """Aggregates returns based on date periods"""
    if period is None or 'day' in period:
        return returns
    index = returns.index

    if 'month' in period:
        return group_returns(returns, index.month, compounded=compounded)

    if 'quarter' in period:
        return group_returns(returns, index.quarter, compounded=compounded)

    if period == "A" or any(x in period for x in ['year', 'eoy', 'yoy']):
        return group_returns(returns, index.year, compounded=compounded)

    if 'week' in period:
        return group_returns(returns, index.week, compounded=compounded)

    if 'eow' in period or period == "W":
        return group_returns(returns, [index.year, index.week],
                             compounded=compounded)

    if 'eom' in period or period == "M":
        return group_returns(returns, [index.year, index.month],
                             compounded=compounded)

    if 'eoq' in period or period == "Q":
        return group_returns(returns, [index.year, index.quarter],
                             compounded=compounded)

    if not isinstance(period, str):
        return group_returns(returns, period, compounded)

    return returns

# %% ../nbs/00_utils.ipynb 22
def to_excess_returns(returns:(pd.Series, pd.DataFrame), # Returns
 rf:(float, 'pd.Series', 'pd.DataFrame') , # Risk-Free rate(s)
 nperiods:int=None # Will convert rf to different frequency using deannualize
 )->('pd.Series', 'pd.DataFrame'): #Returns - risk free rate
    """
    Calculates excess returns by subtracting
    risk-free returns from total returns
    """
    if isinstance(rf, int):
        rf = float(rf)

    if not isinstance(rf, float):
        rf = rf[rf.index.isin(returns.index)]

    if nperiods is not None:
        # deannualize
        rf = _np.power(1 + rf, 1. / nperiods) - 1.

    return returns - rf

# %% ../nbs/00_utils.ipynb 23
def prepare_prices(data, base=1.):
    """Converts return data into prices + cleanup"""
    data = data.copy()
    if isinstance(data, _pd.DataFrame):
        for col in data.columns:
            if data[col].dropna().min() <= 0 or data[col].dropna().max() < 1:
                data[col] = to_prices(data[col], base)

    # is it returns?
    # elif data.min() < 0 and data.max() < 1:
    elif data.min() < 0 or data.max() < 1:
        data = to_prices(data, base)

    if isinstance(data, (_pd.DataFrame, _pd.Series)):
        data = data.fillna(0).replace(
            [_np.inf, -_np.inf], float('NaN'))

    return data

# %% ../nbs/00_utils.ipynb 24
def prepare_returns(data, rf=0., nperiods=None):
    """Converts price data into returns + cleanup"""
    data = data.copy()
    function = inspect.stack()[1][3]
    if isinstance(data, _pd.DataFrame):
        for col in data.columns:
            if data[col].dropna().min() >= 0 and data[col].dropna().max() > 1:
                data[col] = data[col].pct_change()
    elif data.min() >= 0 and data.max() > 1:
        data = data.pct_change()

    # cleanup data
    data = data.replace([_np.inf, -_np.inf], float('NaN'))

    if isinstance(data, (_pd.DataFrame, _pd.Series)):
        data = data.fillna(0).replace(
            [_np.inf, -_np.inf], float('NaN'))
    unnecessary_function_calls = ['_prepare_benchmark',
                                  'cagr',
                                  'gain_to_pain_ratio',
                                  'rolling_volatility',]


    if function not in unnecessary_function_calls:
        if rf > 0:
            return to_excess_returns(data, rf, nperiods)
    return data

# %% ../nbs/00_utils.ipynb 25
def download_returns(ticker, period="max"):
    """download returns from yahoo"""
    if isinstance(period, _pd.DatetimeIndex):
        p = {"start": period[0]}
    else:
        p = {"period": period}
    return _yf.Ticker(ticker).history(**p)['Close'].pct_change() # may need to change Adj Close

# %% ../nbs/00_utils.ipynb 26
def prepare_benchmark(benchmark=None, period="max", rf=0.,
                       prepare_returns=True):
    """
    Fetch benchmark if ticker is provided, and pass through
    _prepare_returns()
    period can be options or (expected) _pd.DatetimeIndex range
    """
    if benchmark is None:
        return None

    if isinstance(benchmark, str):
        benchmark = download_returns(benchmark)

    elif isinstance(benchmark, _pd.DataFrame):
        benchmark = benchmark[benchmark.columns[0]].copy()

    if isinstance(period, _pd.DatetimeIndex) \
        and set(period) != set(benchmark.index):

        # Adjust Benchmark to Strategy frequency
        benchmark_prices = to_prices(benchmark, base=1)
        new_index = _pd.date_range(start=period[0], end=period[-1], freq='D')
        benchmark = benchmark_prices.reindex(new_index, method='bfill') \
            .reindex(period).pct_change().fillna(0)
        benchmark = benchmark[benchmark.index.isin(period)]

    if prepare_returns:
        return _prepare_returns(benchmark.dropna(), rf=rf)
    return benchmark.dropna()

# %% ../nbs/00_utils.ipynb 27
def round_to_closest(val, res, decimals=None):
    """Round to closest resolution"""
    if decimals is None and "." in str(res):
        decimals = len(str(res).split('.')[1])
    return round(round(val / res) * res, decimals)

# %% ../nbs/00_utils.ipynb 28
def file_stream():
    """Returns a file stream"""
    return io.BytesIO()

# %% ../nbs/00_utils.ipynb 29
def _in_notebook(matplotlib_inline=False):
    """Identify enviroment (notebook, terminal, etc)"""
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            # Jupyter notebook or qtconsole
            if matplotlib_inline:
                get_ipython().magic("matplotlib inline")
            return True
        if shell == 'TerminalInteractiveShell':
            # Terminal running IPython
            return False
        # Other type (?)
        return False
    except NameError:
        # Probably standard Python interpreter
        return False

# %% ../nbs/00_utils.ipynb 30
def _count_consecutive(data):
    """Counts consecutive data (like cumsum() with reset on zeroes)"""
    def _count(data):
        return data * (data.groupby(
            (data != data.shift(1)).cumsum()).cumcount() + 1)

    if isinstance(data, _pd.DataFrame):
        for col in data.columns:
            data[col] = _count(data[col])
        return data
    return _count(data)

# %% ../nbs/00_utils.ipynb 31
def _score_str(val):
    """Returns + sign for positive values and - for negative values (used in plots)"""
    return ("" if "-" in val else "+") + str(val)

# %% ../nbs/00_utils.ipynb 32
def make_index(ticker_weights:(dict), #  A python dict with tickers as keys and weights as values
rebalance="1M", # Pandas resample interval or None for never
period:(str)="max", # time period of the returns to be downloaded
returns:('pd.Series', 'pd.DataFrame')=None, #Returns: If provided, check if returns for the ticker are in this dataframe, before trying to download from yahoo
match_dates:(bool)=False # whether to match dates?
)->('pd.Series', 'pd.DataFrame'):#Returns for the index
    """
    Makes an index out of the given tickers and weights.
    Optionally you can pass a dataframe with the returns.
    If returns is not given it try to download them with yfinance
    """
    # Declare a returns variable
    index = None
    portfolio = {}

    # Iterate over weights
    for ticker in ticker_weights.keys():
        if (returns is None) or (ticker not in returns.columns):
            # Download the returns for this ticker, e.g. GOOG
            ticker_returns = download_returns(ticker, period)
        else:
            ticker_returns = returns[ticker]

        portfolio[ticker] = ticker_returns

    # index members time-series
    index = _pd.DataFrame(portfolio).dropna()

    if match_dates:
        index=index[max(index.ne(0).idxmax()):]

    # no rebalance?
    if rebalance is None:
        for ticker, weight in ticker_weights.items():
            index[ticker] = weight * index[ticker]
        return index.sum(axis=1)

    last_day = index.index[-1]

    # rebalance marker
    rbdf = index.resample(rebalance).first()
    rbdf['break'] = rbdf.index.strftime('%s')

    # index returns with rebalance markers
    index = _pd.concat([index, rbdf['break']], axis=1)

    # mark first day day
    index['first_day'] = _pd.isna(index['break']) & ~_pd.isna(index['break'].shift(1))
    index.loc[index.index[0], 'first_day'] = True

    # multiply first day of each rebalance period by the weight
    for ticker, weight in ticker_weights.items():
        index[ticker] = _np.where(
            index['first_day'], weight * index[ticker], index[ticker])

    # drop first marker
    index.drop(columns=['first_day'], inplace=True)

    # drop when all are NaN
    index.dropna(how="all", inplace=True)
    return index[index.index <= last_day].sum(axis=1)


# %% ../nbs/00_utils.ipynb 33
def make_portfolio(returns, start_balance=1e5,
                   mode="comp", round_to=None):
    """Calculates compounded value of portfolio"""
    returns = _prepare_returns(returns)

    if mode.lower() in ["cumsum", "sum"]:
        p1 = start_balance + start_balance * returns.cumsum()
    elif mode.lower() in ["compsum", "comp"]:
        p1 = to_prices(returns, start_balance)
    else:
        # fixed amount every day
        comp_rev = (start_balance + start_balance *
                    returns.shift(1)).fillna(start_balance) * returns
        p1 = start_balance + comp_rev.cumsum()

    # add day before with starting balance
    p0 = _pd.Series(data=start_balance,
                    index=p1.index + _pd.Timedelta(days=-1))[:1]

    portfolio = _pd.concat([p0, p1])

    if isinstance(returns, _pd.DataFrame):
        portfolio.loc[:1, :] = start_balance
        portfolio.drop(columns=[0], inplace=True)

    if round_to:
        portfolio = _np.round(portfolio, round_to)

    return portfolio

# %% ../nbs/00_utils.ipynb 34
def _flatten_dataframe(df, set_index=None):
    """Dirty method for flattening multi-index dataframe"""
    s_buf = _io.StringIO()
    df.to_csv(s_buf)
    s_buf.seek(0)

    df = pd.read_csv(s_buf)
    if set_index is not None:
        df.set_index(set_index, inplace=True)

    return 

# %% ../nbs/00_utils.ipynb 35
#| export 

