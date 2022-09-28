# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_stats.ipynb.

# %% auto 0
__all__ = ['compsum', 'comp', 'expected_return', 'geometric_mean', 'ghpr', 'outliers', 'remove_outliers', 'best', 'worst',
           'consecutive_wins', 'consecutive_losses', 'exposure', 'win_rate', 'avg_return', 'avg_win', 'avg_loss',
           'volatility', 'rolling_volatility', 'implied_volatility', 'autocorr_penalty', 'sharpe', 'smart_sharpe',
           'rolling_sharpe', 'sortino', 'smart_sortino', 'rolling_sortino', 'probabilistic_ratio',
           'probabilistic_sharpe_ratio', 'probabilistic_sortino_ratio', 'probabilistic_adjusted_sortino_ratio',
           'treynor_ratio', 'omega', 'gain_to_pain_ratio', 'cagr', 'rar', 'skew', 'kurtosis', 'calmar', 'ulcer_index',
           'ulcer_performance_index', 'upi', 'serenity_index', 'risk_of_ruin', 'ror', 'value_at_risk', 'var',
           'conditional_value_at_risk', 'cvar', 'expected_shortfall', 'tail_ratio', 'payoff_ratio', 'win_loss_ratio',
           'profit_ratio', 'profit_factor', 'cpc_index', 'common_sense_ratio', 'outlier_win_ratio',
           'outlier_loss_ratio', 'recovery_factor', 'risk_return_ratio', 'max_drawdown', 'to_drawdown_series',
           'drawdown_details', 'kelly_criterion', 'r_squared', 'r2', 'information_ratio', 'greeks', 'rolling_greeks',
           'compare', 'monthly_returns']

# %% ../nbs/01_stats.ipynb 2
#| echo: false
from nbdev.showdoc import *
from warnings import warn
import pandas as pd
import numpy as np
from math import ceil, sqrt
from scipy.stats import (
    norm as norm, linregress as linregress
)

import hypersheets.utils as utils

# %% ../nbs/01_stats.ipynb 3
def compsum(returns):
    """Calculates cumulative compounded returns up to each day, for series of daily returns"""
    return returns.add(1).cumprod() -1

# %% ../nbs/01_stats.ipynb 5
def comp(returns):
    """Calculates total compounded return, for series of daily returns"""
    return returns.add(1).prod() -1

# %% ../nbs/01_stats.ipynb 8
def expected_return(returns, aggregate=None, compounded=True,
                    prepare_returns=True):
    """
    Returns the expected geometric return for a given period
    by calculating the geometric holding period return
    """
    # if prepare_returns:
    #     returns = utils.prepare_returns(returns)
    # returns = utils.aggregate_returns(returns, aggregate, compounded)
    return np.product(1 + returns) ** (1 / len(returns)) - 1

# %% ../nbs/01_stats.ipynb 11
def geometric_mean(retruns, aggregate=None, compounded=True):
    """Shorthand for expected_return()"""
    return expected_return(retruns, aggregate, compounded)


def ghpr(retruns, aggregate=None, compounded=True):
    """Shorthand for expected_return()"""
    return expected_return(retruns, aggregate, compounded)

# %% ../nbs/01_stats.ipynb 12
def outliers(returns, quantile=.95):
    """Returns series of outliers: all values greater than the quantile"""
    return returns[returns > returns.quantile(quantile)].dropna(how='all')

# %% ../nbs/01_stats.ipynb 14
def remove_outliers(returns, quantile=.95):
    """Returns series of returns without the outliers on the top end"""
    return returns[returns < returns.quantile(quantile)]

# %% ../nbs/01_stats.ipynb 16
def best(returns, aggregate=None, compounded=True, prepare_returns=True):
    """Returns the best day/month/week/quarter/year's return"""
    if prepare_returns:
        returns = utils._prepare_returns(returns)
    return utils.aggregate_returns(returns, aggregate, compounded).max()

# %% ../nbs/01_stats.ipynb 17
def worst(returns, aggregate=None, compounded=True, prepare_returns=True):
    """Returns the worst day/month/week/quarter/year's return"""
    if prepare_returns:
        returns = utils._prepare_returns(returns)
    return utils.aggregate_returns(returns, aggregate, compounded).min()

# %% ../nbs/01_stats.ipynb 18
def consecutive_wins(returns, aggregate=None, compounded=True,
                     prepare_returns=True):
    """Returns the maximum consecutive wins by day/month/week/quarter/year"""
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    returns = _utils.aggregate_returns(returns, aggregate, compounded) > 0
    return _utils._count_consecutive(returns).max()

# %% ../nbs/01_stats.ipynb 19
def consecutive_losses(returns, aggregate=None, compounded=True,
                       prepare_returns=True):
    """
    Returns the maximum consecutive losses by
    day/month/week/quarter/year
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    returns = _utils.aggregate_returns(returns, aggregate, compounded) < 0
    return _utils._count_consecutive(returns).max()

# %% ../nbs/01_stats.ipynb 20
def exposure(returns, prepare_returns=True):
    """Returns the market exposure time (returns != 0)"""
    if prepare_returns:
        returns = _utils._prepare_returns(returns)

    def _exposure(ret):
        ex = len(ret[(~_np.isnan(ret)) & (ret != 0)]) / len(ret)
        return _ceil(ex * 100) / 100

    if isinstance(returns, _pd.DataFrame):
        _df = {}
        for col in returns.columns:
            _df[col] = _exposure(returns[col])
        return _pd.Series(_df)
    return _exposure(returns)

# %% ../nbs/01_stats.ipynb 21
def win_rate(returns, aggregate=None, compounded=True, prepare_returns=True):
    """Calculates the win ratio for a period"""
    def _win_rate(series):
        try:
            return len(series[series > 0]) / len(series[series != 0])
        except Exception:
            return 0.

    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    if aggregate:
        returns = _utils.aggregate_returns(returns, aggregate, compounded)

    if isinstance(returns, _pd.DataFrame):
        _df = {}
        for col in returns.columns:
            _df[col] = _win_rate(returns[col])

        return _pd.Series(_df)

    return _win_rate(returns)

# %% ../nbs/01_stats.ipynb 22
def avg_return(returns, aggregate=None, compounded=True, prepare_returns=True):
    """Calculates the average return/trade return for a period"""
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    if aggregate:
        returns = _utils.aggregate_returns(returns, aggregate, compounded)
    return returns[returns != 0].dropna().mean()


# %% ../nbs/01_stats.ipynb 23
def avg_win(returns, aggregate=None, compounded=True, prepare_returns=True):
    """
    Calculates the average winning
    return/trade return for a period
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    if aggregate:
        returns = _utils.aggregate_returns(returns, aggregate, compounded)
    return returns[returns > 0].dropna().mean()

# %% ../nbs/01_stats.ipynb 24
def avg_loss(returns, aggregate=None, compounded=True, prepare_returns=True):
    """
    Calculates the average low if
    return/trade return for a period
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    if aggregate:
        returns = _utils.aggregate_returns(returns, aggregate, compounded)
    return returns[returns < 0].dropna().mean()

# %% ../nbs/01_stats.ipynb 25
def volatility(returns, periods=252, annualize=True, prepare_returns=True):
    """Calculates the volatility of returns for a period"""
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    std = returns.std()
    if annualize:
        return std * _np.sqrt(periods)

    return std

# %% ../nbs/01_stats.ipynb 26
def rolling_volatility(returns, rolling_period=126, periods_per_year=252,
                       prepare_returns=True):
    if prepare_returns:
        returns = _utils._prepare_returns(returns, rolling_period)

    return returns.rolling(rolling_period).std() * _np.sqrt(periods_per_year)

# %% ../nbs/01_stats.ipynb 27
def implied_volatility(returns, periods=252, annualize=True):
    """Calculates the implied volatility of returns for a period"""
    logret = _utils.log_returns(returns)
    if annualize:
        return logret.rolling(periods).std() * _np.sqrt(periods)
    return logret.std()


# %% ../nbs/01_stats.ipynb 28
def autocorr_penalty(returns, prepare_returns=False):
    """Metric to account for auto correlation"""
    if prepare_returns:
        returns = _utils._prepare_returns(returns)

    if isinstance(returns, _pd.DataFrame):
        returns = returns[returns.columns[0]]

    # returns.to_csv('/Users/ran/Desktop/test.csv')
    num = len(returns)
    coef = _np.abs(_np.corrcoef(returns[:-1], returns[1:])[0, 1])
    corr = [((num - x)/num) * coef ** x for x in range(1, num)]
    return _np.sqrt(1 + 2 * _np.sum(corr))

# %% ../nbs/01_stats.ipynb 29
def sharpe(returns, rf=0., periods=252, annualize=True, smart=False):
    """
    Calculates the sharpe ratio of access returns
    If rf is non-zero, you must specify periods.
    In this case, rf is assumed to be expressed in yearly (annualized) terms
    Args:
        * returns (Series, DataFrame): Input return series
        * rf (float): Risk-free rate expressed as a yearly (annualized) return
        * periods (int): Freq. of returns (252/365 for daily, 12 for monthly)
        * annualize: return annualize sharpe?
        * smart: return smart sharpe ratio
    """
    if rf != 0 and periods is None:
        raise Exception('Must provide periods if rf != 0')

    returns = _utils._prepare_returns(returns, rf, periods)
    divisor = returns.std(ddof=1)
    if smart:
        # penalize sharpe with auto correlation
        divisor = divisor * autocorr_penalty(returns)
    res = returns.mean() / divisor

    if annualize:
        return res * _np.sqrt(
            1 if periods is None else periods)

    return res

# %% ../nbs/01_stats.ipynb 30
def smart_sharpe(returns, rf=0., periods=252, annualize=True):
    """Sharpe ratio, penalised with autocorrelation penalty"""
    return sharpe(returns, rf, periods, annualize, True)

# %% ../nbs/01_stats.ipynb 31
def rolling_sharpe(returns, rf=0., rolling_period=126,
                   annualize=True, periods_per_year=252,
                   prepare_returns=True):

    if rf != 0 and rolling_period is None:
        raise Exception('Must provide periods if rf != 0')

    if prepare_returns:
        returns = _utils._prepare_returns(returns, rf, rolling_period)

    res = returns.rolling(rolling_period).mean() / \
        returns.rolling(rolling_period).std()

    if annualize:
        res = res * _np.sqrt(
            1 if periods_per_year is None else periods_per_year)

    return res

# %% ../nbs/01_stats.ipynb 32
def sortino(returns, rf=0, periods=252, annualize=True, smart=False):
    """
    Calculates the sortino ratio of access returns
    If rf is non-zero, you must specify periods.
    In this case, rf is assumed to be expressed in yearly (annualized) terms
    Calculation is based on this paper by Red Rock Capital
    http://www.redrockcapital.com/Sortino__A__Sharper__Ratio_Red_Rock_Capital.pdf
    """
    if rf != 0 and periods is None:
        raise Exception('Must provide periods if rf != 0')

    returns = _utils._prepare_returns(returns, rf, periods)

    downside = _np.sqrt((returns[returns < 0] ** 2).sum() / len(returns))

    if smart:
        # penalize sortino with auto correlation
        downside = downside * autocorr_penalty(returns)

    res = returns.mean() / downside

    if annualize:
        return res * _np.sqrt(
            1 if periods is None else periods)

    return res

# %% ../nbs/01_stats.ipynb 33
def smart_sortino(returns, rf=0, periods=252, annualize=True):
    return sortino(returns, rf, periods, annualize, True)

# %% ../nbs/01_stats.ipynb 34
def rolling_sortino(returns, rf=0, rolling_period=126, annualize=True,
                    periods_per_year=252, **kwargs):
    if rf != 0 and rolling_period is None:
        raise Exception('Must provide periods if rf != 0')

    if kwargs.get("prepare_returns", True):
        returns = _utils._prepare_returns(returns, rf, rolling_period)

    downside = returns.rolling(rolling_period).apply(
        lambda x: (x.values[x.values < 0]**2).sum()) / rolling_period

    res = returns.rolling(rolling_period).mean() / _np.sqrt(downside)
    if annualize:
        res = res * _np.sqrt(
            1 if periods_per_year is None else periods_per_year)
    return res

# %% ../nbs/01_stats.ipynb 35
# check logic for this
def probabilistic_ratio(series, rf=0., base="sharpe", periods=252, annualize=False, smart=False):

    if base.lower() == "sharpe":
        base = sharpe(series, periods=periods, annualize=False, smart=smart)
    elif base.lower() == "sortino":
        base = sortino(series, periods=periods, annualize=False, smart=smart)
    elif base.lower() == "adjusted_sortino":
        base = adjusted_sortino(series, periods=periods,
                                annualize=False, smart=smart)
    else:
        raise Exception(
            '`metric` must be either `sharpe`, `sortino`, or `adjusted_sortino`')
    skew_no = skew(series, prepare_returns=False)
    kurtosis_no = kurtosis(series, prepare_returns=False)

    n = len(series)

    sigma_sr = _np.sqrt((1 + (0.5 * base ** 2) - (skew_no * base) +
                       (((kurtosis_no - 3) / 4) * base ** 2)) / (n - 1))

    ratio = (base - rf) / sigma_sr
    psr = _norm.cdf(ratio)

    if annualize:
        return psr * (252 ** 0.5)
    return psr


# %% ../nbs/01_stats.ipynb 36
def probabilistic_sharpe_ratio(series, rf=0., periods=252, annualize=False, smart=False):
    return probabilistic_ratio(series, rf, base="sharpe", periods=periods,
                               annualize=annualize, smart=smart)

# %% ../nbs/01_stats.ipynb 37
def probabilistic_sortino_ratio(series, rf=0., periods=252, annualize=False, smart=False):
    return probabilistic_ratio(series, rf, base="sortino", periods=periods,
                               annualize=annualize, smart=smart)

# %% ../nbs/01_stats.ipynb 38
def probabilistic_adjusted_sortino_ratio(series, rf=0., periods=252, annualize=False, smart=False):
    return probabilistic_ratio(series, rf, base="adjusted_sortino", periods=periods,
                               annualize=annualize, smart=smart)

# %% ../nbs/01_stats.ipynb 39
def treynor_ratio(returns, benchmark, periods=252., rf=0.):
    """
    Calculates the Treynor ratio
    Args:
        * returns (Series, DataFrame): Input return series
        * benchmatk (String, Series, DataFrame): Benchmark to compare beta to
        * periods (int): Freq. of returns (252/365 for daily, 12 for monthly)
    """
    if isinstance(returns, _pd.DataFrame):
        returns = returns[returns.columns[0]]

    beta = greeks(returns, benchmark, periods=periods).to_dict().get('beta', 0)
    if beta == 0:
        return 0
    return (comp(returns) - rf) / beta

# %% ../nbs/01_stats.ipynb 40
def omega(returns, rf=0.0, required_return=0.0, periods=252):
    """
    Determines the Omega ratio of a strategy.
    See https://en.wikipedia.org/wiki/Omega_ratio for more details.
    """
    if len(returns) < 2:
        return _np.nan

    if required_return <= -1:
        return _np.nan

    returns = _utils._prepare_returns(returns, rf, periods)

    if periods == 1:
        return_threshold = required_return
    else:
        return_threshold = (1 + required_return) ** (1. / periods) - 1

    returns_less_thresh = returns - return_threshold
    numer = returns_less_thresh[returns_less_thresh > 0.0].sum().values[0]
    denom = -1.0 * \
        returns_less_thresh[returns_less_thresh < 0.0].sum().values[0]

    if denom > 0.0:
        return numer / denom

    return _np.nan


# %% ../nbs/01_stats.ipynb 41
def gain_to_pain_ratio(returns, rf=0, resolution="D"):
    """
    Jack Schwager's GPR. See here for more info:
    https://archive.is/wip/2rwFW
    """
    returns = _utils._prepare_returns(returns, rf).resample(resolution).sum()
    downside = abs(returns[returns < 0].sum())
    return returns.sum() / downside


# %% ../nbs/01_stats.ipynb 42
def cagr(returns, rf=0., compounded=True):
    """
    Calculates the communicative annualized growth return
    (CAGR%) of access returns
    If rf is non-zero, you must specify periods.
    In this case, rf is assumed to be expressed in yearly (annualized) terms
    """
    total = _utils._prepare_returns(returns, rf)
    if compounded:
        total = comp(total)
    else:
        total = _np.sum(total)

    years = (returns.index[-1] - returns.index[0]).days / 365.

    res = abs(total + 1.0) ** (1.0 / years) - 1

    if isinstance(returns, _pd.DataFrame):
        res = _pd.Series(res)
        res.index = returns.columns

    return res

# %% ../nbs/01_stats.ipynb 43
def rar(returns, rf=0.):
    """
    Calculates the risk-adjusted return of access returns
    (CAGR / exposure. takes time into account.)
    If rf is non-zero, you must specify periods.
    In this case, rf is assumed to be expressed in yearly (annualized) terms
    """
    returns = _utils._prepare_returns(returns, rf)
    return cagr(returns) / exposure(returns)

# %% ../nbs/01_stats.ipynb 44
def skew(returns, prepare_returns=True):
    """
    Calculates returns' skewness
    (the degree of asymmetry of a distribution around its mean)
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    return returns.skew()

# %% ../nbs/01_stats.ipynb 45
def kurtosis(returns, prepare_returns=True):
    """
    Calculates returns' kurtosis
    (the degree to which a distribution peak compared to a normal distribution)
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    return returns.kurtosis()

# %% ../nbs/01_stats.ipynb 46
def calmar(returns, prepare_returns=True):
    """Calculates the calmar ratio (CAGR% / MaxDD%)"""
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    cagr_ratio = cagr(returns)
    max_dd = max_drawdown(returns)
    return cagr_ratio / abs(max_dd)

# %% ../nbs/01_stats.ipynb 47
def ulcer_index(returns):
    """Calculates the ulcer index score (downside risk measurment)"""
    dd = to_drawdown_series(returns)
    return _np.sqrt(_np.divide((dd**2).sum(), returns.shape[0] - 1))

# %% ../nbs/01_stats.ipynb 48
def ulcer_performance_index(returns, rf=0):
    """
    Calculates the ulcer index score
    (downside risk measurment)
    """
    return (comp(returns)-rf) / ulcer_index(returns)

# %% ../nbs/01_stats.ipynb 49
def upi(returns, rf=0):
    """Shorthand for ulcer_performance_index()"""
    return ulcer_performance_index(returns, rf)

# %% ../nbs/01_stats.ipynb 50
def serenity_index(returns, rf=0):
    """
    Calculates the serenity index score
    (https://www.keyquant.com/Download/GetFile?Filename=%5CPublications%5CKeyQuant_WhitePaper_APT_Part1.pdf)
    """
    dd = to_drawdown_series(returns)
    pitfall = - cvar(dd) / returns.std()
    return (comp(returns)-rf) / (ulcer_index(returns) * pitfall)

# %% ../nbs/01_stats.ipynb 51
def risk_of_ruin(returns, prepare_returns=True):
    """
    Calculates the risk of ruin
    (the likelihood of losing all one's investment capital)
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    wins = win_rate(returns)
    return ((1 - wins) / (1 + wins)) ** len(returns)

# %% ../nbs/01_stats.ipynb 52
def ror(returns):
    """Shorthand for risk_of_ruin()"""
    return risk_of_ruin(returns)

# %% ../nbs/01_stats.ipynb 53
def value_at_risk(returns, sigma=1, confidence=0.95, prepare_returns=True):
    """
    Calculats the daily value-at-risk
    (variance-covariance calculation with confidence n)
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    mu = returns.mean()
    sigma *= returns.std()

    if confidence > 1:
        confidence = confidence/100

    return _norm.ppf(1-confidence, mu, sigma)

# %% ../nbs/01_stats.ipynb 54
def var(returns, sigma=1, confidence=0.95, prepare_returns=True):
    """Shorthand for value_at_risk()"""
    return value_at_risk(returns, sigma, confidence, prepare_returns)

# %% ../nbs/01_stats.ipynb 55
def conditional_value_at_risk(returns, sigma=1, confidence=0.95,
                              prepare_returns=True):
    """
    Calculats the conditional daily value-at-risk (aka expected shortfall)
    quantifies the amount of tail risk an investment
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    var = value_at_risk(returns, sigma, confidence)
    c_var = returns[returns < var].values.mean()
    return c_var if ~_np.isnan(c_var) else var

# %% ../nbs/01_stats.ipynb 56
def cvar(returns, sigma=1, confidence=0.95, prepare_returns=True):
    """Shorthand for conditional_value_at_risk()"""
    return conditional_value_at_risk(
        returns, sigma, confidence, prepare_returns)

# %% ../nbs/01_stats.ipynb 57
def expected_shortfall(returns, sigma=1, confidence=0.95):
    """Shorthand for conditional_value_at_risk()"""
    return conditional_value_at_risk(returns, sigma, confidence)

# %% ../nbs/01_stats.ipynb 58
def tail_ratio(returns, cutoff=0.95, prepare_returns=True):
    """
    Measures the ratio between the right
    (95%) and left tail (5%).
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    return abs(returns.quantile(cutoff) / returns.quantile(1-cutoff))

# %% ../nbs/01_stats.ipynb 59
def payoff_ratio(returns, prepare_returns=True):
    """Measures the payoff ratio (average win/average loss)"""
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    return avg_win(returns) / abs(avg_loss(returns))


# %% ../nbs/01_stats.ipynb 60
def win_loss_ratio(returns, prepare_returns=True):
    """Shorthand for payoff_ratio()"""
    return payoff_ratio(returns, prepare_returns)

# %% ../nbs/01_stats.ipynb 61
def profit_ratio(returns, prepare_returns=True):
    """Measures the profit ratio (win ratio / loss ratio)"""
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    wins = returns[returns >= 0]
    loss = returns[returns < 0]

    win_ratio = abs(wins.mean() / wins.count())
    loss_ratio = abs(loss.mean() / loss.count())
    try:
        return win_ratio / loss_ratio
    except Exception:
        return 0.

# %% ../nbs/01_stats.ipynb 62
def profit_factor(returns, prepare_returns=True):
    """Measures the profit ratio (wins/loss)"""
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    return abs(returns[returns >= 0].sum() / returns[returns < 0].sum())

# %% ../nbs/01_stats.ipynb 63
def cpc_index(returns, prepare_returns=True):
    """
    Measures the cpc ratio
    (profit factor * win % * win loss ratio)
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    return profit_factor(returns) * win_rate(returns) * \
        win_loss_ratio(returns)

# %% ../nbs/01_stats.ipynb 64
def common_sense_ratio(returns, prepare_returns=True):
    """Measures the common sense ratio (profit factor * tail ratio)"""
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    return profit_factor(returns) * tail_ratio(returns)

# %% ../nbs/01_stats.ipynb 65
def outlier_win_ratio(returns, quantile=.99, prepare_returns=True):
    """
    Calculates the outlier winners ratio
    99th percentile of returns / mean positive return
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    return returns.quantile(quantile).mean() / returns[returns >= 0].mean()

# %% ../nbs/01_stats.ipynb 66
def outlier_loss_ratio(returns, quantile=.01, prepare_returns=True):
    """
    Calculates the outlier losers ratio
    1st percentile of returns / mean negative return
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    return returns.quantile(quantile).mean() / returns[returns < 0].mean()

# %% ../nbs/01_stats.ipynb 67
def recovery_factor(returns, prepare_returns=True):
    """Measures how fast the strategy recovers from drawdowns"""
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    total_returns = comp(returns)
    max_dd = max_drawdown(returns)
    return total_returns / abs(max_dd)

# %% ../nbs/01_stats.ipynb 68
def risk_return_ratio(returns, prepare_returns=True):
    """
    Calculates the return / risk ratio
    (sharpe ratio without factoring in the risk-free rate)
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    return returns.mean() / returns.std()

# %% ../nbs/01_stats.ipynb 69
def max_drawdown(prices):
    """Calculates the maximum drawdown"""
    prices = _utils._prepare_prices(prices)
    return (prices / prices.expanding(min_periods=0).max()).min() - 1

# %% ../nbs/01_stats.ipynb 70
def to_drawdown_series(returns):
    """Convert returns series to drawdown series"""
    prices = _utils._prepare_prices(returns)
    dd = prices / _np.maximum.accumulate(prices) - 1.
    return dd.replace([_np.inf, -_np.inf, -0], 0)

# %% ../nbs/01_stats.ipynb 71
def drawdown_details(drawdown):
    """
    Calculates drawdown details, including start/end/valley dates,
    duration, max drawdown and max dd for 99% of the dd period
    for every drawdown period
    """
    def _drawdown_details(drawdown):
        # mark no drawdown
        no_dd = drawdown == 0

        # extract dd start dates
        starts = ~no_dd & no_dd.shift(1)
        starts = list(starts[starts].index)

        # extract end dates
        ends = no_dd & (~no_dd).shift(1)
        ends = list(ends[ends].index)

        # no drawdown :)
        if not starts:
            return _pd.DataFrame(
                index=[], columns=('start', 'valley', 'end', 'days',
                                   'max drawdown', '99% max drawdown'))

        # drawdown series begins in a drawdown
        if ends and starts[0] > ends[0]:
            starts.insert(0, drawdown.index[0])

        # series ends in a drawdown fill with last date
        if not ends or starts[-1] > ends[-1]:
            ends.append(drawdown.index[-1])

        # build dataframe from results
        data = []
        for i, _ in enumerate(starts):
            dd = drawdown[starts[i]:ends[i]]
            clean_dd = -remove_outliers(-dd, .99)
            data.append((starts[i], dd.idxmin(), ends[i],
                         (ends[i] - starts[i]).days,
                         dd.min() * 100, clean_dd.min() * 100))

        df = _pd.DataFrame(data=data,
                           columns=('start', 'valley', 'end', 'days',
                                    'max drawdown',
                                    '99% max drawdown'))
        df['days'] = df['days'].astype(int)
        df['max drawdown'] = df['max drawdown'].astype(float)
        df['99% max drawdown'] = df['99% max drawdown'].astype(float)

        df['start'] = df['start'].dt.strftime('%Y-%m-%d')
        df['end'] = df['end'].dt.strftime('%Y-%m-%d')
        df['valley'] = df['valley'].dt.strftime('%Y-%m-%d')

        return df

    if isinstance(drawdown, _pd.DataFrame):
        _dfs = {}
        for col in drawdown.columns:
            _dfs[col] = _drawdown_details(drawdown[col])
        return _pd.concat(_dfs, axis=1)

    return _drawdown_details(drawdown)

# %% ../nbs/01_stats.ipynb 72
def kelly_criterion(returns, prepare_returns=True):
    """
    Calculates the recommended maximum amount of capital that
    should be allocated to the given strategy, based on the
    Kelly Criterion (http://en.wikipedia.org/wiki/Kelly_criterion)
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    win_loss_ratio = payoff_ratio(returns)
    win_prob = win_rate(returns)
    lose_prob = 1 - win_prob

    return ((win_loss_ratio * win_prob) - lose_prob) / win_loss_ratio

# %% ../nbs/01_stats.ipynb 74
def r_squared(returns, benchmark, prepare_returns=True):
    """Measures the straight line fit of the equity curve"""
    # slope, intercept, r_val, p_val, std_err = _linregress(
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    _, _, r_val, _, _ = _linregress(
        returns, _utils._prepare_benchmark(benchmark, returns.index))
    return r_val**2

# %% ../nbs/01_stats.ipynb 75
def r2(returns, benchmark):
    """Shorthand for r_squared()"""
    return r_squared(returns, benchmark)

# %% ../nbs/01_stats.ipynb 76
def information_ratio(returns, benchmark, prepare_returns=True):
    """
    Calculates the information ratio
    (basically the risk return ratio of the net profits)
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    diff_rets = returns - _utils._prepare_benchmark(benchmark, returns.index)

    return diff_rets.mean() / diff_rets.std()

# %% ../nbs/01_stats.ipynb 77
def greeks(returns, benchmark, periods=252., prepare_returns=True):
    """Calculates alpha and beta of the portfolio"""
    # ----------------------------
    # data cleanup
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    benchmark = _utils._prepare_benchmark(benchmark, returns.index)
    # ----------------------------

    # find covariance
    matrix = _np.cov(returns, benchmark)
    beta = matrix[0, 1] / matrix[1, 1]

    # calculates measures now
    alpha = returns.mean() - beta * benchmark.mean()
    alpha = alpha * periods

    return _pd.Series({
        "beta":  beta,
        "alpha": alpha,
        # "vol": _np.sqrt(matrix[0, 0]) * _np.sqrt(periods)
    }).fillna(0)

# %% ../nbs/01_stats.ipynb 78
def rolling_greeks(returns, benchmark, periods=252, prepare_returns=True):
    """Calculates rolling alpha and beta of the portfolio"""
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    df = _pd.DataFrame(data={
        "returns": returns,
        "benchmark": _utils._prepare_benchmark(benchmark, returns.index)
    })
    df = df.fillna(0)
    corr = df.rolling(int(periods)).corr().unstack()['returns']['benchmark']
    std = df.rolling(int(periods)).std()
    beta = corr * std['returns'] / std['benchmark']

    alpha = df['returns'].mean() - beta * df['benchmark'].mean()

    # alpha = alpha * periods
    return _pd.DataFrame(index=returns.index, data={
        "beta": beta,
        "alpha": alpha
    })

# %% ../nbs/01_stats.ipynb 79
def compare(returns, benchmark, aggregate=None, compounded=True,
            round_vals=None, prepare_returns=True):
    """
    Compare returns to benchmark on a
    day/week/month/quarter/year basis
    """
    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    benchmark = _utils._prepare_benchmark(benchmark, returns.index)

    data = _pd.DataFrame(data={
        'Benchmark': _utils.aggregate_returns(
            benchmark, aggregate, compounded) * 100,
        'Returns': _utils.aggregate_returns(
            returns, aggregate, compounded) * 100
    })

    data['Multiplier'] = data['Returns'] / data['Benchmark']
    data['Won'] = _np.where(data['Returns'] >= data['Benchmark'], '+', '-')

    if round_vals is not None:
        return _np.round(data, round_vals)

    return data

# %% ../nbs/01_stats.ipynb 80
def monthly_returns(returns, eoy=True, compounded=True, prepare_returns=True):
    """Calculates monthly returns"""
    if isinstance(returns, _pd.DataFrame):
        warn("Pandas DataFrame was passed (Series expeted). "
             "Only first column will be used.")
        returns = returns.copy()
        returns.columns = map(str.lower, returns.columns)
        if len(returns.columns) > 1 and 'close' in returns.columns:
            returns = returns['close']
        else:
            returns = returns[returns.columns[0]]

    if prepare_returns:
        returns = _utils._prepare_returns(returns)
    original_returns = returns.copy()

    returns = _pd.DataFrame(
        _utils.group_returns(returns,
                             returns.index.strftime('%Y-%m-01'),
                             compounded))

    returns.columns = ['Returns']
    returns.index = _pd.to_datetime(returns.index)

    # get returnsframe
    returns['Year'] = returns.index.strftime('%Y')
    returns['Month'] = returns.index.strftime('%b')

    # make pivot table
    returns = returns.pivot('Year', 'Month', 'Returns').fillna(0)

    # handle missing months
    for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
        if month not in returns.columns:
            returns.loc[:, month] = 0

    # order columns by month
    returns = returns[['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']]

    if eoy:
        returns['eoy'] = _utils.group_returns(
            original_returns, 
            original_returns.index.year, 
            compounded=compounded).values

    returns.columns = map(lambda x: str(x).upper(), returns.columns)
    returns.index.name = None

    return returns
