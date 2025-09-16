import pandas as pd
import numpy as np
import math

from qbt.core.metrics import performance_from_nav

def test_performance_keys_and_total_return():
    idx = pd.date_range("2020-01-01", periods=10, freq="D")
    nav = pd.Series(np.linspace(100.0, 110.0, len(idx)), index=idx, name="equity")
    nav_norm = nav / nav.iloc[0]

    perf = performance_from_nav(nav_norm, risk_free=0.0, periods_per_year=252)

    required = {"annual_return","annual_vol","sharpe","sortino","calmar","max_drawdown","total_return","information_ratio"}
    assert required.issubset(perf.keys())

    expected_total_return = float(nav_norm.iloc[-1] - 1.0)
    assert math.isclose(perf["total_return"], expected_total_return, rel_tol=1e-6, abs_tol=1e-6)

def test_max_drawdown_non_negative():
    idx = pd.date_range("2020-01-01", periods=6, freq="D")
    nav = pd.Series([100, 105, 110, 108, 104, 106], index=idx, name="equity")
    perf = performance_from_nav(nav / nav.iloc[0])
    assert perf["max_drawdown"] <= 0.0
