# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/03_plot_wrappers.ipynb.

# %% auto 0
__all__ = ['FLATUI_COLORS', 'GRAYSCALE_COLORS', 'to_plotly', 'returns', 'log_returns', 'daily_returns', 'yearly_returns',
           'distribution', 'histogram', 'drawdown', 'drawdowns_periods', 'rolling_beta', 'rolling_volatility',
           'rolling_sharpe', 'rolling_sortino', 'monthly_heatmap', 'outperformance_heatmap', 'monthly_returns']

# %% ../../nbs/03_plot_wrappers.ipynb 2
#| echo: false
import warnings
import matplotlib.pyplot as plt
from matplotlib.ticker import (
    StrMethodFormatter,
    FuncFormatter
)

import numpy as np
from pandas import DataFrame as df
import seaborn as sns

from .. import (
    stats as _stats, utils as _utils)
from hypersheets._plotting import (
    core as _core)

# %% ../../nbs/03_plot_wrappers.ipynb 4
#| echo: false
# Define global color variables

FLATUI_COLORS = ["#696969", "#348dc1", "#af4b64",#fedd78->#696969 #348dc1->#0000FF
                  "#4fa487", "#9b59b6", "#808080"]
GRAYSCALE_COLORS = ['silver', '#222222', 'gray'] * 3

# check for plotly
_HAS_PLOTLY = False
try:
    import plotly
    _HAS_PLOTLY = True
except ImportError:
    pass

# %% ../../nbs/03_plot_wrappers.ipynb 5
def to_plotly(fig):
    if not _HAS_PLOTLY:
        return fig
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig = plotly.tools.mpl_to_plotly(fig)
        return plotly.plotly.iplot(fig, filename='quantstats-plot',
                                   overwrite=True)

# %% ../../nbs/03_plot_wrappers.ipynb 10
def returns(returns, benchmark=None,
            grayscale=False, figsize=(10, 6),
            returns_label="Strategy", benchmark_label="Benchmark",
            fontname='Arial', lw=1.5,
            match_volatility=False, compound=True, cumulative=True,
            resample=None, ylabel="Cumulative Returns",
            subtitle=True, savefig=None, show=True,
            prepare_returns=False):

    title = 'Cumulative Returns' if compound else 'Returns'
    if benchmark is not None:
        if isinstance(benchmark, str):
            title += ' vs %s' % benchmark.upper()
        else:
            title += ' vs %s' % benchmark_label
        if match_volatility:
            title += ' (Volatility Matched)'

    if prepare_returns:
        returns = _utils.prepare_returns(returns)

    benchmark = _utils.prepare_benchmark(benchmark, returns.index)

    fig = _core.plot_timeseries(returns, benchmark, title,
                                ylabel=ylabel,
                                match_volatility=match_volatility,
                                log_scale=False,
                                resample=resample,
                                compound=compound,
                                cumulative=cumulative,
                                lw=lw,
                                returns_label=returns_label,
                                benchmark_label = benchmark_label,
                                figsize=figsize,
                                fontname=fontname,
                                grayscale=grayscale,
                                subtitle=subtitle,
                                savefig=savefig, show=show)
    if not show:
        return fig

# %% ../../nbs/03_plot_wrappers.ipynb 12
def log_returns(returns, benchmark=None,
                grayscale=False, figsize=(10, 5),
                returns_label="Strategy", benchmark_label="Benchmark",
                fontname='Arial', lw=1.5,
                match_volatility=False, compound=True, cumulative=True,
                resample=None, ylabel="Cumulative Returns",
                subtitle=True, savefig=None, show=True,
                prepare_returns=False):

    title = 'Cumulative Returns' if compound else 'Returns'
    if benchmark is not None:
        if isinstance(benchmark, str):
            title += ' vs %s (Log Scaled' % benchmark.upper()
        else:
            title += ' vs %s (Log Scaled'  % benchmark_label
        if match_volatility:
            title += ', Volatility Matched'
    else:
        title += ' (Log Scaled'
    title += ')'

    if prepare_returns:
        returns = _utils.prepare_returns(returns)

    benchmark = _utils.prepare_benchmark(benchmark, returns.index)

    fig = _core.plot_timeseries(returns, benchmark, title,
                                ylabel=ylabel,
                                match_volatility=match_volatility,
                                log_scale=True,
                                resample=resample,
                                compound=compound,
                                cumulative=cumulative,
                                lw=lw,
                                returns_label=returns_label,
                                benchmark_label = benchmark_label,
                                figsize=figsize,
                                fontname=fontname,
                                grayscale=grayscale,
                                subtitle=subtitle,
                                savefig=savefig, show=show)
    if not show:
        return fig


def daily_returns(returns,
                  grayscale=False, figsize=(10, 4),
                  fontname='Arial', lw=0.5,
                  log_scale=False, ylabel="Returns",
                  subtitle=True, savefig=None, show=True,
                  prepare_returns=True):

    if prepare_returns:
        returns = _utils.prepare_returns(returns)

    fig = _core.plot_timeseries(returns, None, 'Daily Returns',
                                ylabel=ylabel,
                                match_volatility=False,
                                log_scale=log_scale,
                                resample='D',
                                compound=False,
                                lw=lw,
                                figsize=figsize,
                                fontname=fontname,
                                grayscale=grayscale,
                                subtitle=subtitle,
                                savefig=savefig, show=show)
    if not show:
        return fig

# %% ../../nbs/03_plot_wrappers.ipynb 14
def yearly_returns(returns, benchmark=None,
                   returns_label="Strategy", benchmark_label="Benchmark",
                   fontname='Arial', grayscale=False,
                   hlw=1.5, hlcolor="red", hllabel="",
                   match_volatility=False,
                   log_scale=False, figsize=(10, 5), ylabel=True,
                   subtitle=True, compounded=True,
                   savefig=None, show=True,
                   prepare_returns=True):

    title = 'EOY Returns'
    if benchmark is not None:
        title += ' vs %s' % benchmark_label
        benchmark = _utils.prepare_benchmark(
            benchmark, returns.index).resample('A').apply(
                _stats.comp).resample('A').last()

    if prepare_returns:
        returns = _utils.prepare_returns(returns)

    if compounded:
        returns = returns.resample('A').apply(_stats.comp)
    else:
        returns = returns.resample('A').apply(df.sum)
    returns = returns.resample('A').last()

    fig = _core.plot_returns_bars(returns, benchmark,
                                  returns_label=returns_label, benchmark_label=benchmark_label,
                                  fontname=fontname,
                                  hline=returns.mean(),
                                  hlw=hlw,
                                  hllabel=hllabel,
                                  hlcolor=hlcolor,
                                  match_volatility=match_volatility,
                                  log_scale=log_scale,
                                  resample=None,
                                  title=title,
                                  figsize=figsize,
                                  grayscale=grayscale,
                                  ylabel=ylabel,
                                  subtitle=subtitle,
                                  savefig=savefig, show=show)
    if not show:
        return fig

# %% ../../nbs/03_plot_wrappers.ipynb 16
def distribution(returns, fontname='Arial', grayscale=False, ylabel=True,
                 figsize=(10, 6), subtitle=True, compounded=True,
                 savefig=None, show=True,
                 prepare_returns=True):
    if prepare_returns:
        returns = _utils.prepare_returns(returns)

    fig = _core.plot_distribution(returns,
                                  fontname=fontname,
                                  grayscale=grayscale,
                                  figsize=figsize,
                                  ylabel=ylabel,
                                  subtitle=subtitle,
                                  compounded=compounded,
                                  savefig=savefig, show=show)
    if not show:
        return fig

# %% ../../nbs/03_plot_wrappers.ipynb 18
def histogram(returns, resample='M', fontname='Arial',
              grayscale=False, figsize=(10, 5), ylabel=True,
              subtitle=True, compounded=True, savefig=None, show=True,
              prepare_returns=True):

    if prepare_returns:
        returns = _utils.prepare_returns(returns)

    if resample == 'W':
        title = "Weekly "
    elif resample == 'M':
        title = "Monthly "
    elif resample == 'Q':
        title = "Quarterly "
    elif resample == 'A':
        title = "Annual "
    else:
        title = ""

    return _core.plot_histogram(returns,
                                resample=resample,
                                grayscale=grayscale,
                                fontname=fontname,
                                title="Distribution of %sReturns" % title,
                                figsize=figsize,
                                ylabel=ylabel,
                                subtitle=subtitle,
                                compounded=compounded,
                                savefig=savefig, show=show)

# %% ../../nbs/03_plot_wrappers.ipynb 20
def drawdown(returns, grayscale=False, figsize=(10, 3),
             fontname='Arial', lw=1, log_scale=False,
             match_volatility=False, compound=False, ylabel="Drawdown",
             resample=None, subtitle=True, savefig=None, show=True):

    dd = _stats.to_drawdown_series(returns)

    fig = _core.plot_timeseries(dd, title='Underwater Plot',
                                hline=dd.mean(), hlw=2, hllabel="Average",
                                returns_label="Drawdown",
                                compound=compound, match_volatility=match_volatility,
                                log_scale=log_scale, resample=resample,
                                fill=True, lw=lw, figsize=figsize,
                                ylabel=ylabel,
                                fontname=fontname, grayscale=grayscale,
                                subtitle=subtitle,
                                savefig=savefig, show=show)
    if not show:
        return fig

# %% ../../nbs/03_plot_wrappers.ipynb 22
def drawdowns_periods(returns, periods=5, lw=1.5, log_scale=False,
                      fontname='Arial', grayscale=False, figsize=(10, 5),
                      ylabel=True, subtitle=True, compounded=True,
                      savefig=None, show=True,
                      prepare_returns=True):
    if prepare_returns:
        returns = _utils.prepare_returns(returns)

    fig = _core.plot_longest_drawdowns(returns,
                                       periods=periods,
                                       lw=lw,
                                       log_scale=log_scale,
                                       fontname=fontname,
                                       grayscale=grayscale,
                                       figsize=figsize,
                                       ylabel=ylabel,
                                       subtitle=subtitle,
                                       compounded=compounded,
                                       savefig=savefig, show=show)
    if not show:
        return fig

# %% ../../nbs/03_plot_wrappers.ipynb 24
def rolling_beta(returns, benchmark,
                 benchmark_label="Benchmark",
                 window1=126, window1_label="6-Months",
                 window2=252, window2_label="12-Months",
                 lw=1.5, fontname='Arial', grayscale=False,
                 figsize=(10, 3), ylabel=True,
                 subtitle=True, savefig=None, show=True,
                 prepare_returns=True):

    if prepare_returns:
        returns = _utils.prepare_returns(returns)

    benchmark = _utils.prepare_benchmark(benchmark, returns.index)

    fig = _core.plot_rolling_beta(returns, benchmark,
                                  window1=window1, window1_label=window1_label,
                                  window2=window2, window2_label=window2_label,
                                  title="Rolling Beta to %s" % benchmark_label, 
                                  fontname=fontname,
                                  grayscale=grayscale,
                                  lw=lw,
                                  figsize=figsize,
                                  ylabel=ylabel,
                                  subtitle=subtitle,
                                  savefig=savefig, show=show)
    if not show:
        return fig

# %% ../../nbs/03_plot_wrappers.ipynb 26
def rolling_volatility(returns, benchmark=None,
                       returns_label="Strategy", benchmark_label="Benchmark",
                       period=126, period_label="6-Months",
                       periods_per_year=252,
                       lw=1.5, fontname='Arial', grayscale=False,
                       figsize=(10, 3), ylabel="Volatility",
                       subtitle=True, savefig=None, show=True):

    returns = _stats.rolling_volatility(returns, period, periods_per_year)

    if benchmark is not None:
        benchmark = _utils.prepare_benchmark(benchmark, returns.index)
        benchmark = _stats.rolling_volatility(
            benchmark, period, periods_per_year, prepare_returns=False)

    fig = _core.plot_rolling_stats(returns, benchmark,
                                   hline=returns.mean(),
                                   hlw=1.5,
                                   ylabel=ylabel,
                                   title='Rolling Volatility (%s)' % period_label,
                                   returns_label=returns_label,
                                   benchmark_label = benchmark_label,
                                   fontname=fontname,
                                   grayscale=grayscale,
                                   lw=lw,
                                   figsize=figsize,
                                   subtitle=subtitle,
                                   savefig=savefig, show=show)
    if not show:
        return fig


# %% ../../nbs/03_plot_wrappers.ipynb 28
def rolling_sharpe(returns, benchmark=None, rf=0.,
                   returns_label="Strategy", benchmark_label="Benchmark",
                   period=126, period_label="6-Months",
                   periods_per_year=252,
                   lw=1.25, fontname='Arial', grayscale=False,
                   figsize=(10, 3), ylabel="Sharpe",
                   subtitle=True, savefig=None, show=True):

    returns = _stats.rolling_sharpe(
        returns, rf, period, True, periods_per_year, )

    if benchmark is not None:
        benchmark = _utils.prepare_benchmark(benchmark, returns.index, rf)
        benchmark = _stats.rolling_sharpe(
            benchmark, rf, period, True, periods_per_year,
            prepare_returns=False)

    fig = _core.plot_rolling_stats(returns, benchmark,
                                   hline=returns.mean(),
                                   hlw=1.5,
                                   ylabel=ylabel,
                                   title='Rolling Sharpe (%s)' % period_label,
                                   returns_label=returns_label,
                                   benchmark_label = benchmark_label,
                                   fontname=fontname,
                                   grayscale=grayscale,
                                   lw=lw,
                                   figsize=figsize,
                                   subtitle=subtitle,
                                   savefig=savefig, show=show)
    if not show:
        return fig

# %% ../../nbs/03_plot_wrappers.ipynb 30
def rolling_sortino(returns, benchmark=None, rf=0.,
                    returns_label="Strategy", benchmark_label="Benchmark",
                    period=126, period_label="6-Months",
                    periods_per_year=252,
                    lw=1.25, fontname='Arial', grayscale=False,
                    figsize=(10, 3), ylabel="Sortino",
                    subtitle=True, savefig=None, show=True):

    returns = _stats.rolling_sortino(
        returns, rf, period, True, periods_per_year)

    if benchmark is not None:
        benchmark = _utils.prepare_benchmark(benchmark, returns.index, rf)
        benchmark = _stats.rolling_sortino(
            benchmark, rf, period, True, periods_per_year,
            prepare_returns=False)

    fig = _core.plot_rolling_stats(returns, benchmark,
                                   hline=returns.mean(),
                                   hlw=1.5,
                                   ylabel=ylabel,
                                   title='Rolling Sortino (%s)' % period_label,
                                   returns_label=returns_label,
                                   benchmark_label = benchmark_label,
                                   fontname=fontname,
                                   grayscale=grayscale,
                                   lw=lw,
                                   figsize=figsize,
                                   subtitle=subtitle,
                                   savefig=savefig, show=show)
    if not show:
        return fig

# %% ../../nbs/03_plot_wrappers.ipynb 32
def monthly_heatmap(returns, annot_size=10, figsize=(10, 5),
                    cbar=True, square=False,
                    compounded=True, eoy=False,
                    grayscale=False, fontname='Arial',
                    ylabel=True, savefig=None, show=True):

    # colors, ls, alpha = _core._get_colors(grayscale)
    cmap = 'gray' if grayscale else 'RdYlGn'
    
    vmax = (_stats.monthly_returns(returns, eoy=False,
                                     compounded=compounded) * 100).abs().max().max()
    
    #if vmax < 1: vmax = 1 ##
    

    returns = _stats.monthly_returns(returns, eoy=eoy,
                                     compounded=compounded) * 100
    
    

    fig_height = len(returns) / 3

    if figsize is None:
        size = list(plt.gcf().get_size_inches())
        figsize = (size[0], size[1])

    figsize = (figsize[0], max([fig_height, figsize[1]]))

    if cbar:
        figsize = (figsize[0]*1.04, max([fig_height, figsize[1]]))

    fig, ax = plt.subplots(figsize=figsize)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    fig.set_facecolor('white')
    ax.set_facecolor('white')

    ax.set_title('      Monthly Returns (%)\n', fontsize=14, y=.995,
                 fontname=fontname, fontweight='bold', color='black')

    # _sns.set(font_scale=.9)
    ax = sns.heatmap(returns, ax=ax, annot=True, center=0,
                      vmax=vmax, #vmin = -vmax,
                      annot_kws={"size": annot_size},
                      fmt="0.2f", linewidths=0.5,
                      square=square, cbar=cbar, cmap=cmap,
                      cbar_kws={'format': '%.0f%%'})
    # _sns.set(font_scale=1)

    # align plot to match other
    if ylabel:
        ax.set_ylabel('Years', fontname=fontname,
                      fontweight='bold', fontsize=12)
        ax.yaxis.set_label_coords(-.1, .5)

    ax.tick_params(colors="#808080")
    plt.xticks(rotation=0, fontsize=annot_size*1.2)
    plt.yticks(rotation=0, fontsize=annot_size*1.2)

    try:
        plt.subplots_adjust(hspace=0, bottom=0, top=1)
    except Exception:
        pass
    try:
        fig.tight_layout(w_pad=0, h_pad=0)
    except Exception:
        pass

    if savefig:
        if isinstance(savefig, dict):
            plt.savefig(**savefig)
        else:
            plt.savefig(savefig)

    if show:
        plt.show(block=False)

    plt.close()

    if not show:
        return fig

    return None

# %% ../../nbs/03_plot_wrappers.ipynb 34
def outperformance_heatmap(returns, benchmark=None, annot_size=10, figsize=(10, 5),
                    cbar=True, square=False, benchmark_label="Benchmark",
                    compounded=True, eoy=False,
                    grayscale=False, fontname='Arial',
                    ylabel=True, savefig=None, show=True):

    # colors, ls, alpha = _core._get_colors(grayscale)
    cmap = 'gray' if grayscale else 'RdYlGn'
    
    vmax = ((
        _stats.monthly_returns(returns, eoy=False,
                                     compounded=compounded)-
        _stats.monthly_returns(benchmark, eoy=False,
                               compounded=compounded)
            )* 100).abs().max().max()
    
    if vmax < 1: vmax = 1 ##
    

    outperformance = ((
        _stats.monthly_returns(returns, eoy=eoy,
                                     compounded=compounded)-
        _stats.monthly_returns(benchmark, eoy=eoy,
                               compounded=compounded)
            )* 100)
    
    

    fig_height = len(outperformance) / 3

    if figsize is None:
        size = list(plt.gcf().get_size_inches())
        figsize = (size[0], size[1])

    figsize = (figsize[0], max([fig_height, figsize[1]]))

    if cbar:
        figsize = (figsize[0]*1.04, max([fig_height, figsize[1]]))

    fig, ax = plt.subplots(figsize=figsize)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    fig.set_facecolor('white')
    ax.set_facecolor('white')

    ax.set_title('      Monthly Outperformance against %s \n' % benchmark_label, fontsize=14, y=.995,
                 fontname=fontname, fontweight='bold', color='black')

    # _sns.set(font_scale=.9)
    ax = sns.heatmap(outperformance, ax=ax, annot=True, center=0,
                      vmax=vmax, #vmin = -vmax,
                      annot_kws={"size": annot_size},
                      fmt="0.2f", linewidths=0.5,
                      square=square, cbar=cbar, cmap=cmap,
                      cbar_kws={'format': '%.0f%%'})
    # _sns.set(font_scale=1)

    # align plot to match other
    if ylabel:
        ax.set_ylabel('Years', fontname=fontname,
                      fontweight='bold', fontsize=12)
        ax.yaxis.set_label_coords(-.1, .5)

    ax.tick_params(colors="#808080")
    plt.xticks(rotation=0, fontsize=annot_size*1.2)
    plt.yticks(rotation=0, fontsize=annot_size*1.2)

    try:
        plt.subplots_adjust(hspace=0, bottom=0, top=1)
    except Exception:
        pass
    try:
        fig.tight_layout(w_pad=0, h_pad=0)
    except Exception:
        pass

    if savefig:
        if isinstance(savefig, dict):
            plt.savefig(**savefig)
        else:
            plt.savefig(savefig)

    if show:
        plt.show(block=False)

    plt.close()

    if not show:
        return fig

    return None

# %% ../../nbs/03_plot_wrappers.ipynb 36
def monthly_returns(returns, annot_size=10, figsize=(10, 5),
                    cbar=True, square=False,
                    compounded=True, eoy=False,
                    grayscale=False, fontname='Arial',
                    ylabel=True, savefig=None, show=True):
    """A wrapper for monthly heatmaps"""
    return monthly_heatmap(returns, annot_size, figsize,
                           cbar, square,
                           compounded, eoy,
                           grayscale, fontname,
                           ylabel, savefig, show)
