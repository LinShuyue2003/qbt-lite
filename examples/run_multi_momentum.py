from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path

from qbt.data.loader import load_csv
from qbt.core.broker import Broker
from qbt.core.engine_multi import BacktestEngineMulti
from qbt.core.metrics import performance_from_nav
from qbt.strategies.topn_momentum import TopNMomentum
from qbt.report.report import generate_report

def make_mock(csv_path: str, seed: int, drift: float = 0.0003, n: int = 600):
    rng = np.random.default_rng(seed)
    rets = rng.normal(loc=drift, scale=0.01, size=n)
    prices = 50 * np.exp(np.cumsum(rets))
    close = prices
    open_ = np.append([prices[0]], prices[:-1])
    high = np.maximum(open_, close) * (1 + rng.uniform(0.0, 0.003, size=n))
    low = np.minimum(open_, close) * (1 - rng.uniform(0.0, 0.003, size=n))
    volume = rng.integers(500, 5000, size=n)
    dates = pd.bdate_range(start=pd.Timestamp("2018-01-01"), periods=n)
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

def main():
    BASE = Path(__file__).resolve().parent
    ddir = BASE / "data_sample"
    out = BASE / "output"
    out.mkdir(parents=True, exist_ok=True)

    files = {"AAA": ddir / "AAA.csv", "BBB": ddir / "BBB.csv", "CCC": ddir / "CCC.csv"}
    make_mock(str(files["AAA"]), seed=1, drift=0.0004)
    make_mock(str(files["BBB"]), seed=2, drift=0.0002)
    make_mock(str(files["CCC"]), seed=3, drift=0.0001)

    data_map = {sym: load_csv(str(path), symbol=sym) for sym, path in files.items()}
    strat = TopNMomentum(data_map, params={"lookback": 60, "top_n": 2})
    engine = BacktestEngineMulti(data_map=data_map, strategy=strat, starting_cash=100_000.0,
                                 broker=Broker(commission_bps=0.0005, slippage=0.01))
    nav = engine.run()
    nav_norm = nav / nav.iloc[0]
    perf = performance_from_nav(nav_norm, risk_free=0.0, periods_per_year=252)
    print("Performance Summary (Multi-Asset Top-N Momentum)")
    for k, v in perf.items():
        print(f"- {k}: {v:.4f}")
    generate_report(nav, "multi_momentum")

if __name__ == "__main__":
    main()
