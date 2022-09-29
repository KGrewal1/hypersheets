# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_reports.ipynb.

# %% auto 0
__all__ = ['std_path', 'html']

# %% ../nbs/04_reports.ipynb 2
#| echo: false
import pandas as pd
import numpy as np
from math import sqrt, ceil
from datetime import (
    datetime as dt, timedelta as td
)
from base64 import b64encode
import re as regex
from tabulate import tabulate
import hypersheets
# from hypersheets import (
#     __version__, stats,
#     utils as utils, plots as plots
# )
from dateutil.relativedelta import relativedelta

try:
    from IPython.core.display import (
        display as iDisplay, HTML as iHTML
    )
except ImportError:
    pass



# %% ../nbs/04_reports.ipynb 3
#| echo: false
# path to location of default report template
std_path = hypersheets.__path__[0]+ '/report.html' 

# %% ../nbs/04_reports.ipynb 4
def _get_trading_periods(periods_per_year=252):
    half_year = ceil(periods_per_year/2)
    return periods_per_year, half_year

# %% ../nbs/04_reports.ipynb 5
def _match_dates(returns, benchmark):
    returns = returns.loc[
        max(returns.ne(0).idxmax(), benchmark.ne(0).idxmax()):]
    benchmark = benchmark.loc[
        max(returns.ne(0).idxmax(), benchmark.ne(0).idxmax()):]

    return returns, benchmark

# %% ../nbs/04_reports.ipynb 6
def html(returns, benchmark=None, rf=0., grayscale=False,
         title='Strategy Tearsheet', output=None, compounded=True,
         periods_per_year=252, download_filename='quantstats-tearsheet.html',
         figfmt='svg', template_path=None, match_dates=False, **kwargs):
    """Production of .html tearsheets"""

    if output is None and not utils._in_notebook():
        raise ValueError("`file` must be specified")

    win_year, win_half_year = _get_trading_periods(periods_per_year)

    tpl = ""
    with open(template_path or __file__[:-4] + '.html') as f:
        tpl = f.read()
        f.close()
     
    returns_title = 'Strategy'
    # get title for returns: 
    if isinstance(returns, str):
        returns_title = returns
    elif isinstance(returns, pd.Series):
        returns_title = returns.name
    elif isinstance(returns, pd.DataFrame):
        returns_title = returns[returns.columns[0]].name

    # prepare timeseries
    returns = utils._prepare_returns(returns)

    if benchmark is not None:
        benchmark_title = kwargs.get('benchmark_title', 'Benchmark')
        if kwargs.get('benchmark_title') is None:
            if isinstance(benchmark, str):
                benchmark_title = benchmark
            elif isinstance(benchmark, pd.Series):
                benchmark_title = benchmark.name
            elif isinstance(benchmark, pd.DataFrame):
                benchmark_title = benchmark[benchmark.columns[0]].name

        tpl = tpl.replace('{{benchmark_title}}', f"Benchmark is {benchmark_title.upper()} | ")
        benchmark = utils.prepare_benchmark(benchmark, returns.index, rf)
        if match_dates is True:
            returns, benchmark = _match_dates(returns, benchmark)

    date_range = returns.index.strftime('%e %b, %Y')
    tpl = tpl.replace('{{date_range}}', date_range[0] + ' - ' + date_range[-1])
    tpl = tpl.replace('{{title}}', title)
    tpl = tpl.replace('{{v}}', __version__)

    mtrx = metrics(returns=returns, benchmark=benchmark,
                   rf=rf, display=False, mode='full',
                   sep=True, internal="True",
                   compounded=compounded,
                   periods_per_year=periods_per_year,
                   prepare_returns=False, returns_title = returns_title, benchmark_title=benchmark_title)[2:]

    mtrx.index.name = 'Metric'
    tpl = tpl.replace('{{metrics}}', _html_table(mtrx))
    tpl = tpl.replace('<tr><td></td><td></td><td></td></tr>',
                      '<tr><td colspan="3"><hr></td></tr>')
    tpl = tpl.replace('<tr><td></td><td></td></tr>',
                      '<tr><td colspan="2"><hr></td></tr>')
    
    
    dd = _stats.to_drawdown_series(returns)
    dd_info = _stats.drawdown_details(dd).sort_values(
        by='max drawdown', ascending=True)[:10]

    dd_info = dd_info[['start', 'end', 'max drawdown', 'days']]
    dd_info.columns = ['Started', 'Recovered', 'Drawdown', 'Days']
    tpl = tpl.replace('{{dd_info}}', _html_table(dd_info, False))


    if benchmark is not None:
        yoy = _stats.compare(
            returns, benchmark, aggregate="A", compounded=compounded,
            prepare_returns=False)
        yoy.columns = [benchmark_title, returns_title, 'Multiplier', 'Won']
        yoy = yoy.reindex(columns = [returns_title, benchmark_title, 'Multiplier', 'Won'])
        yoy.index.name = 'Year'
        tpl = tpl.replace('{{eoy_title}}', '<h3>EOY Returns vs %s Benchmark</h3>' % benchmark_title)
        tpl = tpl.replace('{{eoy_table}}', _html_table(yoy))
    else:
        # pct multiplier
        yoy = _pd.DataFrame(
            _utils.group_returns(returns, returns.index.year) * 100)
        yoy.columns = ['Return']
        yoy['Cumulative'] = _utils.group_returns(
            returns, returns.index.year, True)
        yoy['Return'] = yoy['Return'].round(2).astype(str) + '%'
        yoy['Cumulative'] = (yoy['Cumulative'] *
                             100).round(2).astype(str) + '%'
        yoy.index.name = 'Year'
        tpl = tpl.replace('{{eoy_title}}', '<h3>EOY Returns</h3>')
        tpl = tpl.replace('{{eoy_table}}', _html_table(yoy))
        
        
    if benchmark is not None:
        mom = _stats.compare(
            returns, benchmark, aggregate="M", compounded=compounded,
            prepare_returns=False)
        mom.columns = [benchmark_title, returns_title, 'Multiplier', 'Won']
        mom = mom.reindex(columns = [returns_title, benchmark_title, 'Multiplier', 'Won'])
        mom.index.name = 'Index'
        mom['Month'] = mom.index
        mom['Month'] = mom['Month'].apply(lambda x: '-'.join(map(str, x)))
        mom = mom.reset_index(drop = True)
        mom = mom.set_index('Month')
        mom.index.name = 'Month'
        tpl = tpl.replace('{{eom_title}}', '<h3>EOM Returns vs %s Benchmark</h3>' % benchmark_title)
        tpl = tpl.replace('{{eom_table}}', _html_table(mom))
    else:
        # pct multiplier
        mom = _pd.DataFrame(
            _utils.group_returns(returns, [returns.index.year, returns.index.month]) * 100)
        mom.columns = ['Return']
        mom['Cumulative'] = _utils.group_returns(
            returns, [returns.index.year, returns.index.month], True)
        mom['Return'] = mom['Return'].round(2).astype(str) + '%'
        mom['Cumulative'] = (mom['Cumulative'] *
                             100).round(2).astype(str) + '%'
        mom.index.name = 'Index'
        mom['Month'] = mom.index
        mom['Month'] = mom['Month'].apply(lambda x: '-'.join(map(str, x)))
        mom = mom.reset_index(drop = True)
        mom = mom.set_index('Month')
        mom.index.name = 'Month'
        tpl = tpl.replace('{{eom_title}}', '<h3>EOM Returns</h3>')
        tpl = tpl.replace('{{eom_table}}', _html_table(mom))
        


    # plots
    figfile = _utils._file_stream()
    _plots.returns(returns, benchmark, grayscale=grayscale,
                   figsize=(8, 5), subtitle=False,
                   returns_label=returns_title, benchmark_label=benchmark_title,
                   savefig={'fname': figfile, 'format': figfmt},
                   show=False, ylabel=False, cumulative=compounded,
                   prepare_returns=False)
    tpl = tpl.replace('{{returns}}', _embed_figure(figfile, figfmt))

    figfile = _utils._file_stream()
    _plots.log_returns(returns, benchmark, grayscale=grayscale,
                       figsize=(8, 4), subtitle=False,
                       savefig={'fname': figfile, 'format': figfmt},
                       returns_label=returns_title, benchmark_label=benchmark_title,
                       show=False, ylabel=False, cumulative=compounded,
                       prepare_returns=False)
    tpl = tpl.replace('{{log_returns}}', _embed_figure(figfile, figfmt))

    if benchmark is not None:
        figfile = _utils._file_stream()
        _plots.returns(returns, benchmark, match_volatility=True,
                       grayscale=grayscale, figsize=(8, 4), subtitle=False,
                       savefig={'fname': figfile, 'format': figfmt},
                       returns_label=returns_title, benchmark_label=benchmark_title,
                       show=False, ylabel=False, cumulative=compounded,
                       prepare_returns=False)
        tpl = tpl.replace('{{vol_returns}}', _embed_figure(figfile, figfmt))

    figfile = _utils._file_stream()
    _plots.yearly_returns(returns, benchmark, grayscale=grayscale,
                          figsize=(8, 4), subtitle=False,
                          savefig={'fname': figfile, 'format': figfmt},
                          returns_label=returns_title, benchmark_label=benchmark_title,
                          show=False, ylabel=False, compounded=compounded,
                          prepare_returns=False)
    tpl = tpl.replace('{{eoy_returns}}', _embed_figure(figfile, figfmt))

    figfile = _utils._file_stream()
    _plots.histogram(returns, grayscale=grayscale,
                     figsize=(8, 4), subtitle=False,
                     savefig={'fname': figfile, 'format': figfmt},
                     show=False, ylabel=False, compounded=compounded,
                     prepare_returns=False)
    tpl = tpl.replace('{{monthly_dist}}', _embed_figure(figfile, figfmt))

    figfile = _utils._file_stream()
    _plots.daily_returns(returns, grayscale=grayscale,
                         figsize=(8, 3), subtitle=False,
                         savefig={'fname': figfile, 'format': figfmt},
                         show=False, ylabel=False,
                         prepare_returns=False)
    tpl = tpl.replace('{{daily_returns}}', _embed_figure(figfile, figfmt))

    if benchmark is not None:
        figfile = _utils._file_stream()
        _plots.rolling_beta(returns, benchmark, grayscale=grayscale,
                            benchmark_label=benchmark_title,
                            figsize=(8, 3), subtitle=False,
                            window1=win_half_year, window2=win_year,
                            savefig={'fname': figfile, 'format': figfmt},
                            show=False, ylabel=False,
                            prepare_returns=False)
        tpl = tpl.replace('{{rolling_beta}}', _embed_figure(figfile, figfmt))

    figfile = _utils._file_stream()
    _plots.rolling_volatility(returns, benchmark, grayscale=grayscale,
                              figsize=(8, 3), subtitle=False,
                              savefig={'fname': figfile, 'format': figfmt},
                              returns_label=returns_title, benchmark_label=benchmark_title,
                              show=False, ylabel=False, period=win_half_year,
                              periods_per_year=win_year)
    tpl = tpl.replace('{{rolling_vol}}', _embed_figure(figfile, figfmt))

    figfile = _utils._file_stream()
    _plots.rolling_sharpe(returns, grayscale=grayscale,
                          figsize=(8, 3), subtitle=False,
                          savefig={'fname': figfile, 'format': figfmt},
                          returns_label=returns_title, 
                          show=False, ylabel=False, period=win_half_year,
                          periods_per_year=win_year)
    tpl = tpl.replace('{{rolling_sharpe}}', _embed_figure(figfile, figfmt))

    figfile = _utils._file_stream()
    _plots.rolling_sortino(returns, grayscale=grayscale,
                           figsize=(8, 3), subtitle=False,
                           savefig={'fname': figfile, 'format': figfmt},
                           returns_label=returns_title,
                           show=False, ylabel=False, period=win_half_year,
                           periods_per_year=win_year)
    tpl = tpl.replace('{{rolling_sortino}}', _embed_figure(figfile, figfmt))

    figfile = _utils._file_stream()
    _plots.drawdowns_periods(returns, grayscale=grayscale,
                             figsize=(8, 4), subtitle=False,
                             savefig={'fname': figfile, 'format': figfmt},
                             show=False, ylabel=False, compounded=compounded,
                             prepare_returns=False)
    tpl = tpl.replace('{{dd_periods}}', _embed_figure(figfile, figfmt))

    figfile = _utils._file_stream()
    _plots.drawdown(returns, grayscale=grayscale,
                    figsize=(8, 3), subtitle=False,
                    savefig={'fname': figfile, 'format': figfmt},
                    show=False, ylabel=False)
    tpl = tpl.replace('{{dd_plot}}', _embed_figure(figfile, figfmt))

    figfile = _utils._file_stream()
    _plots.monthly_heatmap(returns, grayscale=grayscale,
                           figsize=(8, 4), cbar=False, eoy = True,
                           savefig={'fname': figfile, 'format': figfmt},
                           show=False, ylabel=False, compounded=compounded)
    tpl = tpl.replace('{{monthly_heatmap}}', _embed_figure(figfile, figfmt))
    
    if benchmark is not None:
        figfile = _utils._file_stream()
        _plots.outperformance_heatmap(returns, benchmark=benchmark, grayscale=grayscale,
                               figsize=(8, 4), cbar=False, eoy = True, benchmark_label=benchmark_title,
                               savefig={'fname': figfile, 'format': figfmt},
                               show=False, ylabel=False, compounded=compounded)
        tpl = tpl.replace('{{perf_heatmap}}', _embed_figure(figfile, figfmt))

    figfile = _utils._file_stream()
    _plots.distribution(returns, grayscale=grayscale,
                        figsize=(8, 4), subtitle=False,
                        savefig={'fname': figfile, 'format': figfmt},
                        show=False, ylabel=False, compounded=compounded,
                        prepare_returns=False)
    tpl = tpl.replace('{{returns_dist}}', _embed_figure(figfile, figfmt))

    tpl = _regex.sub(r'\{\{(.*?)\}\}', '', tpl)
    tpl = tpl.replace('white-space:pre;', '')

    if output is None:
        # _open_html(tpl)
        _download_html(tpl, download_filename)
        return

    with open(download_filename, 'w', encoding='utf-8') as f:
        f.write(tpl)
