"""Run a minimal end-to-end backtest on generated mock data.

Usage
-----
python -m examples.run_sma_example

This script:
- Generates a random-walk price series as mock data
- Runs the SMA crossover strategy
- Prints performance metrics
- Saves an equity curve to examples/output/equity.png
"""
from __future__ import annotations
import os
import pandas as pd
import numpy as np
from pathlib import Path

from qbt.data.loader import load_csv
from qbt.core.engine import BacktestEngine
from qbt.core.broker import Broker
from qbt.core.metrics import performance_from_nav
from qbt.core.visualize import plot_equity
from qbt.strategies.sma_cross import SmaCross

def make_mock_csv(csv_path: str, seed: int = 7, n: int = 600):
    rng = np.random.default_rng(seed)
    # lognormal-ish random walk
    rets = rng.normal(loc=0.0003, scale=0.01, size=n)
    prices = 100 * np.exp(np.cumsum(rets))
    # create OHLC from close with small ranges
    close = prices
    open_ = np.append([prices[0]], prices[:-1])
    high = np.maximum(open_, close) * (1 + rng.uniform(0.0, 0.003, size=n))
    low = np.minimum(open_, close) * (1 - rng.uniform(0.0, 0.003, size=n))
    volume = rng.integers(1_000, 10_000, size=n)

    start = pd.Timestamp("2018-01-01")
    dates = pd.bdate_range(start=start, periods=n)  # business days
    df = pd.DataFrame({
        "datetime": dates,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume
    })
    Path(os.path.dirname(csv_path)).mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)

def main():
    BASE = Path(__file__).resolve().parent
    data_csv = BASE / "data_sample" / "MOCK_STOCK.csv"
    out_dir = BASE / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Generate mock data
    make_mock_csv(str(data_csv))

    # Load data
    data = load_csv(str(data_csv), symbol="MOCK")

    # Strategy
    strat = SmaCross(data, params={"short_window": 10, "long_window": 30, "symbol": "MOCK", "unit": 100})

    # Engine + Broker
    engine = BacktestEngine(
        data=data,
        symbol="MOCK",
        strategy=strat,
        starting_cash=100_000.0,
        broker=Broker(commission_bps=0.0005, slippage=0.01)
    )

    nav = engine.run()

    # Normalize NAV to start at 1 for easier interpretation
    nav_norm = nav / nav.iloc[0]

    # Metrics
    perf = performance_from_nav(nav_norm, risk_free=0.0, periods_per_year=252)
    print("Performance Summary")
    for k, v in perf.items():
        print(f"- {k}: {v:.4f}")

    # Plot equity curve
    fig_path = out_dir / "equity.png"
    plot_equity(nav_norm, title="SMA Crossover Equity (Normalized)", save_path=str(fig_path))
    print(f"Saved equity curve to: {fig_path}")

if __name__ == "__main__":
    main()
