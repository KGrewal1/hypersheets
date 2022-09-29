# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_reports.ipynb.

# %% auto 0
__all__ = ['std_path']

# %% ../nbs/04_reports.ipynb 2
#| echo: false
import io
import inspect
from typing import Union,TypeVar
import datetime as dt
import pandas as pd
import numpy as np
import yfinance as yf
import hypersheets
import hypersheets.stats as stats



# %% ../nbs/04_reports.ipynb 3
#| echo: false
# path to location of default report template
std_path = hypersheets.__path__[0]+ '/report.html' 
