from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, Optional

def compute_drawdown(nav: pd.Series) -> pd.Series:
    peak = nav.cummax()
    return nav / peak - 1.0

def performance_from_nav(nav: pd.Series, risk_free: float = 0.0, periods_per_year: int = 252,
                         benchmark_nav: Optional[pd.Series] = None) -> Dict[str, float]:
    nav = nav.dropna()
    rets = nav.pct_change().dropna()
    if rets.empty:
        return {k: float('nan') for k in ['annual_return','annual_vol','sharpe','max_drawdown','total_return','sortino','calmar','information_ratio']}
    mean_r = rets.mean(); std_r = rets.std(ddof=0)
    ann_ret = (1+mean_r)**periods_per_year - 1
    ann_vol = std_r * np.sqrt(periods_per_year)
    rf_period = (1+risk_free)**(1/periods_per_year) - 1
    excess_ret = mean_r - rf_period
    sharpe = np.nan if ann_vol==0 else (excess_ret*periods_per_year)/ann_vol
    dd = compute_drawdown(nav); max_dd = dd.min()
    total_ret = nav.iloc[-1]/nav.iloc[0]-1
    downside = rets[rets < rf_period]; downside_std = downside.std(ddof=0) if not downside.empty else 0.0
    ann_down = downside_std * np.sqrt(periods_per_year)
    sortino = np.nan if ann_down==0 else (excess_ret*periods_per_year)/ann_down
    calmar = np.nan if max_dd==0 else ann_ret/abs(max_dd)
    information_ratio = float('nan')
    if benchmark_nav is not None:
        bench = benchmark_nav.reindex(nav.index).ffill().dropna()
        if len(bench)==len(nav):
            active = rets - bench.pct_change().dropna()
            if not active.empty:
                sd = active.std(ddof=0)
                information_ratio = float('nan') if sd==0 else (active.mean()*periods_per_year)/(sd*np.sqrt(periods_per_year))
    return {"annual_return": float(ann_ret), "annual_vol": float(ann_vol), "sharpe": float(sharpe),
            "max_drawdown": float(max_dd), "total_return": float(total_ret), "sortino": float(sortino),
            "calmar": float(calmar), "information_ratio": float(information_ratio)}
