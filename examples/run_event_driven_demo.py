from __future__ import annotations
import numpy as np, pandas as pd
from qbt.core.event_engine import EventDrivenEngine, MinuteSMA
from qbt.analytics.metrics_ext import trade_stats_from_fills
from qbt.core.metrics import performance_from_nav
from qbt.report.report import generate_report

def make_minute_mock(n_minutes: int = 2000, seed: int = 7, start: str = "2020-01-01 09:30"):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.00005, 0.001, size=n_minutes)
    price = 100 * np.exp(np.cumsum(rets))
    open_ = np.append([price[0]], price[:-1])
    high = np.maximum(open_, price) * (1 + rng.uniform(0.0, 0.001, size=n_minutes))
    low = np.minimum(open_, price) * (1 - rng.uniform(0.0, 0.001, size=n_minutes))
    vol = rng.integers(50, 500, size=n_minutes)
    idx = pd.date_range(start=start, periods=n_minutes, freq="T")
    return pd.DataFrame({'open': open_, 'high': high, 'low': low, 'close': price, 'volume': vol}, index=idx)

def main():
    data = {'MOCK': make_minute_mock()}
    strat = {'MOCK': MinuteSMA(data['MOCK'], short=10, long=30, symbol='MOCK', unit=50)}
    engine = EventDrivenEngine(data, strat)
    nav = engine.run()
    nav_norm = nav / nav.iloc[0]
    perf = performance_from_nav(nav_norm)
    print("Performance (event-driven, return-based):")
    for k,v in perf.items(): print(f"- {k}: {v:.4f}")
    # Build simple trade PnL from fills (FIFO avg-cost approximation)
    fills = engine.portfolio.fills_dataframe()
    pnls = []; qty_cum=0; avg_cost=0.0
    for _, f in fills.iterrows():
        if f['side']=='buy':
            total_cost = avg_cost * qty_cum + (f['price']*f['qty'] + f['fee'])
            qty_cum += f['qty']
            avg_cost = total_cost / max(qty_cum,1)
        else:
            pnl = (f['price'] - avg_cost)*f['qty'] - f['fee']
            qty_cum -= f['qty']
            if qty_cum==0: avg_cost=0.0
            pnls.append({'trade_id': len(pnls)+1, 'timestamp': f['timestamp'], 'symbol': f['symbol'], 'pnl': pnl})
    trades = pd.DataFrame(pnls)
    tstats = trade_stats_from_fills(trades)
    print("Trade metrics (event-driven):")
    for k,v in tstats.items(): print(f"- {k}: {v:.4f}")
    generate_report(nav, "event_driven_demo")

if __name__ == "__main__":
    main()
