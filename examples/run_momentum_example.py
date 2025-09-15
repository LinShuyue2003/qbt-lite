"""Run momentum strategy on mock data.

Usage
-----
python -m examples.run_momentum_example
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
from pathlib import Path

# These imports assume the rest of the project exists locally.
from qbt.data.loader import load_csv
from qbt.core.engine import BacktestEngine
from qbt.core.broker import Broker
from qbt.core.metrics import performance_from_nav
from qbt.core.visualize import plot_equity
from qbt.strategies.momentum import Momentum

def make_mock_csv(csv_path: str, seed: int = 42, n: int = 600):
    rng = np.random.default_rng(seed)
    # Slight positive drift to favor momentum in trending regimes
    rets = rng.normal(loc=0.0004, scale=0.01, size=n)
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
    Path(os.path.dirname(csv_path)).mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)

def main():
    BASE = Path(__file__).resolve().parent
    data_csv = BASE / "data_sample" / "MOCK_STOCK_MOM.csv"
    out_dir = BASE / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    make_mock_csv(str(data_csv))
    data = load_csv(str(data_csv), symbol="MOCK")

    # Use a bigger unit to utilize capital better; set costs to zero to inspect raw signal
    strat = Momentum(data, params={"lookback": 60, "threshold": 0.0, "symbol": "MOCK", "unit": 1000})
    engine = BacktestEngine(
        data=data,
        symbol="MOCK",
        strategy=strat,
        starting_cash=100_000.0,
        broker=Broker(commission_bps=0.0, slippage=0.0)
    )
    nav = engine.run()
    nav_norm = nav / nav.iloc[0]

    perf = performance_from_nav(nav_norm, risk_free=0.0, periods_per_year=252)
    print("Performance Summary (Momentum)")
    for k, v in perf.items():
        print(f"- {k}: {v:.4f}")

    fig_path = out_dir / "equity_momentum.png"
    plot_equity(nav_norm, title="Momentum Equity (Normalized)", save_path=str(fig_path))
    print(f"Saved equity curve to: {fig_path}")

if __name__ == "__main__":
    main()
