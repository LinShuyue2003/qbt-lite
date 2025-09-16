import pandas as pd
import numpy as np

from qbt.core.event_engine import EventDrivenEngine, MinuteSMA
from qbt.analytics.metrics_ext import trade_stats_from_fills
from qbt.core.metrics import performance_from_nav

def make_minute_mock(n_minutes: int = 600, seed: int = 123, start: str = "2020-01-01 09:30"):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.00005, 0.001, size=n_minutes)
    price = 100 * np.exp(np.cumsum(rets))
    open_ = np.append([price[0]], price[:-1])
    high = np.maximum(open_, price)
    low = np.minimum(open_, price)
    vol = rng.integers(50, 200, size=n_minutes)
    idx = pd.date_range(start=start, periods=n_minutes, freq="min")
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": price, "volume": vol}, index=idx)

def test_event_engine_runs_and_metrics():
    df = make_minute_mock()
    engine = EventDrivenEngine(data_map={"MOCK": df}, strategy_map={"MOCK": MinuteSMA(df, short=5, long=15, symbol="MOCK", unit=10)})
    nav = engine.run()
    assert isinstance(nav, pd.Series)
    assert len(nav) > 0
    perf = performance_from_nav(nav / nav.iloc[0])
    assert "sharpe" in perf and "max_drawdown" in perf
    fills = engine.portfolio.fills_dataframe()
    qty_cum = 0
    avg_cost = 0.0
    pnls = []
    for _, f in fills.iterrows():
        if f["side"] == "buy":
            total_cost = avg_cost * qty_cum + (f["price"] * f["qty"] + f["fee"])
            qty_cum += f["qty"]
            avg_cost = total_cost / max(qty_cum, 1)
        else:
            pnl = (f["price"] - avg_cost) * f["qty"] - f["fee"]
            qty_cum -= f["qty"]
            if qty_cum == 0:
                avg_cost = 0.0
            pnls.append({"trade_id": len(pnls) + 1, "timestamp": f["timestamp"], "symbol": f["symbol"], "pnl": pnl})
    trades = pd.DataFrame(pnls)
    stats = trade_stats_from_fills(trades)
    for k in ["num_trades","win_rate","profit_factor","avg_win","avg_loss","max_win","max_loss"]:
        assert k in stats
