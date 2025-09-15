from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from qbt.config import load_config
from qbt.data.loader import load_csv
from qbt.core.engine import BacktestEngine
from qbt.core.engine_multi import BacktestEngineMulti
from qbt.core.broker import Broker
from qbt.core.metrics import performance_from_nav
from qbt.report.report import generate_report
from qbt.strategies.sma_cross import SmaCross
from qbt.strategies.momentum import Momentum
from qbt.strategies.ta_bbands import BollingerBands
from qbt.strategies.ta_rsi import RSIStrategy
from qbt.strategies.ta_macd import MACDStrategy
from qbt.strategies.topn_momentum import TopNMomentum

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="QBT-Lite CLI")
    p.add_argument("--strategy", default="sma", choices=["sma","momentum","topn_momentum","bbands","rsi","macd"])
    p.add_argument("--config", default=None)
    p.add_argument("--symbol", default="MOCK")
    p.add_argument("--data_csv", default=None)
    p.add_argument("--lookback", type=int, default=60)
    p.add_argument("--short", type=int, default=10)
    p.add_argument("--long", type=int, default=30)
    p.add_argument("--top_n", type=int, default=2)
    p.add_argument("--commission_bps", type=float, default=0.0005)
    p.add_argument("--slippage", type=float, default=0.01)
    p.add_argument("--unit", type=int, default=1000)
    p.add_argument("--report_name", default="cli_run")
    return p.parse_args(argv)

def make_mock_df(n: int = 600, seed: int = 7, start: str = "2018-01-01") -> pd.DataFrame:
    import numpy as np
    rng = np.random.default_rng(seed)
    rets = rng.normal(loc=0.0003, scale=0.01, size=n)
    prices = 100 * np.exp(np.cumsum(rets))
    close = prices
    open_ = pd.Series(close).shift(1).fillna(close[0]).to_numpy()
    high = (pd.Series([max(o,c) for o,c in zip(open_, close)]) * (1 + rng.uniform(0.0, 0.003, size=n))).to_numpy()
    low = (pd.Series([min(o,c) for o,c in zip(open_, close)]) * (1 - rng.uniform(0.0, 0.003, size=n))).to_numpy()
    volume = rng.integers(1_000, 10_000, size=n)
    idx = pd.bdate_range(start=start, periods=n)
    return pd.DataFrame({"datetime": idx, "open": open_, "high": high, "low": low, "close": close, "volume": volume})

def main():
    args = parse_args()
    cfg = load_config(args.config) if args.config else {}
    strategy_name = cfg.get("strategy", args.strategy)
    commission_bps = cfg.get("params", {}).get("commission_bps", args.commission_bps)
    slippage = cfg.get("params", {}).get("slippage", args.slippage)
    broker = Broker(commission_bps=commission_bps, slippage=slippage)

    if strategy_name == "topn_momentum":
        data_map = {}
        symbols = cfg.get("data", {}).get("symbols", ["AAA","BBB","CCC"])
        start = cfg.get("data", {}).get("start", "2018-01-01")
        for i, sym in enumerate(symbols, start=1):
            df = make_mock_df(seed=7+i, start=start)
            path = f"examples/data_sample/{sym}.csv"
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(path, index=False)
            data_map[sym] = load_csv(path, symbol=sym)
        lookback = cfg.get("params", {}).get("lookback", args.lookback)
        top_n = cfg.get("params", {}).get("top_n", args.top_n)
        strat = TopNMomentum(data_map, params={"lookback": lookback, "top_n": top_n})
        engine = BacktestEngineMulti(data_map=data_map, strategy=strat, starting_cash=100_000.0, broker=broker)
        nav = engine.run()
    else:
        if args.data_csv:
            data = load_csv(args.data_csv, symbol=args.symbol)
        else:
            df = make_mock_df()
            path = f"examples/data_sample/{args.symbol}.csv"
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(path, index=False)
            data = load_csv(path, symbol=args.symbol)
        if strategy_name == "sma":
            strat = SmaCross(data, params={"short_window": args.short, "long_window": args.long, "symbol": args.symbol, "unit": args.unit})
        elif strategy_name == "momentum":
            strat = Momentum(data, params={"lookback": args.lookback, "threshold": 0.0, "symbol": args.symbol, "unit": args.unit})
        elif strategy_name == "bbands":
            strat = BollingerBands(data, params={"lookback": args.lookback, "num_std": 2.0, "symbol": args.symbol, "unit": args.unit})
        elif strategy_name == "rsi":
            strat = RSIStrategy(data, params={"lookback": args.lookback, "lower": 30, "upper": 70, "symbol": args.symbol, "unit": args.unit})
        elif strategy_name == "macd":
            strat = MACDStrategy(data, params={"fast":12, "slow":26, "signal":9, "symbol": args.symbol, "unit": args.unit})
        engine = BacktestEngine(data=data, symbol=args.symbol, strategy=strat, starting_cash=100_000.0, broker=broker)
        nav = engine.run()

    nav_norm = nav / nav.iloc[0]
    perf = performance_from_nav(nav_norm, risk_free=0.0, periods_per_year=252)
    print("Performance Summary (CLI)")
    for k, v in perf.items():
        print(f"- {k}: {v:.4f}")
    from qbt.report.report import generate_report
    generate_report(nav, args.report_name)

if __name__ == "__main__":
    main()
