"""Grid-search a few SMA parameters to see sensitivity.

Usage
-----
python -m examples.run_sma_sensitivity
"""
from __future__ import annotations
import itertools
import numpy as np
import pandas as pd
from pathlib import Path

from qbt.data.loader import load_csv
from qbt.core.engine import BacktestEngine
from qbt.core.broker import Broker
from qbt.core.metrics import performance_from_nav
from qbt.strategies.sma_cross import SmaCross

def make_mock_csv(csv_path: str, seed: int = 7, n: int = 600):
    rng = np.random.default_rng(seed)
    rets = rng.normal(loc=0.0003, scale=0.01, size=n)
    prices = 100 * np.exp(np.cumsum(rets))
    close = prices
    open_ = np.append([prices[0]], prices[:-1])
    high = np.maximum(open_, close) * (1 + rng.uniform(0.0, 0.003, size=n))
    low = np.minimum(open_, close) * (1 - rng.uniform(0.0, 0.003, size=n))
    volume = rng.integers(1_000, 10_000, size=n)

    start = pd.Timestamp("2018-01-01")
    dates = pd.bdate_range(start=start, periods=n)
    df = pd.DataFrame({
        "datetime": dates,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume
    })
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)

def run_once(data, short, long, unit=1000):
    strat = SmaCross(data.copy(), params={"short_window": short, "long_window": long, "symbol": "MOCK", "unit": unit})
    engine = BacktestEngine(
        data=data,
        symbol="MOCK",
        strategy=strat,
        starting_cash=100_000.0,
        broker=Broker(commission_bps=0.0, slippage=0.0)
    )
    nav = engine.run()
    nav = nav / nav.iloc[0]
    return performance_from_nav(nav, risk_free=0.0, periods_per_year=252)

def main():
    BASE = Path(__file__).resolve().parent
    data_csv = BASE / "data_sample" / "MOCK_STOCK_SMA.csv"
    make_mock_csv(str(data_csv))
    data = load_csv(str(data_csv), symbol="MOCK")

    grid = [(s,l) for s in [5,10,20] for l in [20,50,100] if s < l]
    results = []
    for s,l in grid:
        perf = run_once(data, s, l, unit=1000)
        results.append({"short": s, "long": l, **perf})

    df = pd.DataFrame(results).sort_values("sharpe", ascending=False)
    # Pretty print
    pd.set_option("display.float_format", lambda x: f"{x:.4f}")
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
