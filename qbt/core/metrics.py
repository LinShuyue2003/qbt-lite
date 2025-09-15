from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict

def compute_drawdown(nav: pd.Series) -> pd.Series:
    """Compute drawdown series from a NAV (equity) series.

    Parameters
    ----------
    nav : pd.Series
        Equity curve indexed by datetime.

    Returns
    -------
    pd.Series
        Drawdown series (0 at peaks, negative elsewhere).
    """
    peak = nav.cummax()
    dd = nav / peak - 1.0
    return dd

def performance_from_nav(nav: pd.Series, risk_free: float = 0.0, periods_per_year: int = 252) -> Dict[str, float]:
    """Compute basic performance metrics from a NAV (equity) series.

    Parameters
    ----------
    nav : pd.Series
        Equity curve (e.g., starting at 1.0). Must be positive.
    risk_free : float
        Annualized risk-free rate (as a decimal, e.g. 0.02 = 2%).
    periods_per_year : int
        Number of bars per year (252 for daily, 12 for monthly).

    Returns
    -------
    Dict[str, float]
        annual_return, annual_vol, sharpe, max_drawdown, total_return
    """
    rets = nav.pct_change().dropna()
    if rets.empty:
        return {k: float('nan') for k in ['annual_return','annual_vol','sharpe','max_drawdown','total_return']}
    mean_r = rets.mean()
    std_r = rets.std(ddof=0)
    ann_ret = (1.0 + mean_r)**periods_per_year - 1.0
    ann_vol = std_r * np.sqrt(periods_per_year)
    # Convert risk-free to per-period to compute excess return approximately
    rf_period = (1.0 + risk_free)**(1.0/periods_per_year) - 1.0
    excess_ret = mean_r - rf_period
    sharpe = np.nan if ann_vol == 0 else (excess_ret * periods_per_year) / ann_vol
    dd = compute_drawdown(nav)
    max_dd = dd.min()
    total_ret = nav.iloc[-1] / nav.iloc[0] - 1.0
    return {
        "annual_return": float(ann_ret),
        "annual_vol": float(ann_vol),
        "sharpe": float(sharpe),
        "max_drawdown": float(max_dd),
        "total_return": float(total_ret),
    }
