import pandas as pd
from qbt.core.metrics import performance_from_nav, compute_drawdown
def test_metrics_basic():
    idx = pd.date_range('2020-01-01', periods=10, freq='D')
    nav = pd.Series([1+0.01*i for i in range(10)], index=idx)
    perf = performance_from_nav(nav, periods_per_year=252)
    assert perf['annual_return'] > 0
    dd = compute_drawdown(nav)
    assert dd.min() <= 0
