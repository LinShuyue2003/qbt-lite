from __future__ import annotations
import pandas as pd
from typing import Dict
from .base import Strategy

class TopNMomentum(Strategy):
    def __init__(self, data_map: Dict[str, pd.DataFrame], params: dict | None = None):
        super().__init__(params=params)
        self.data_map = {k: v.copy() for k, v in data_map.items()}
        self.lookback = int(self.params.get("lookback", 60))
        self.top_n = int(self.params.get("top_n", 2))
        self.unit_cap = int(self.params.get("unit_cap", 0))
        for sym, df in self.data_map.items():
            self.data_map[sym]["mom"] = df["close"].pct_change(self.lookback)

    def on_bar(self, ctx):
        ts = ctx.now
        moms = {}
        for sym in ctx.symbols:
            mom = self.data_map[sym].loc[ts, "mom"]
            moms[sym] = mom if pd.notna(mom) else float("-inf")
        ranked = sorted(moms.items(), key=lambda kv: kv[1], reverse=True)
        top = [sym for sym, _ in ranked[:self.top_n] if moms[sym] != float("-inf")]
        targets = {sym: (1.0/len(top)) if (len(top)>0 and sym in top) else 0.0 for sym in ctx.symbols}
        equity = ctx.portfolio.cash
        prices = {}
        for sym in ctx.symbols:
            px = ctx.data[sym]["close"]
            prices[sym] = px
            if sym in ctx.portfolio.positions:
                equity += ctx.portfolio.positions[sym].qty * px
        for sym in ctx.symbols:
            px = prices[sym]
            current_qty = ctx.portfolio.positions.get(sym, None).qty if sym in ctx.portfolio.positions else 0
            target_value = targets[sym] * equity
            target_qty = int(target_value // max(px, 1e-8))
            delta = target_qty - current_qty
            if self.unit_cap > 0:
                if delta > 0:
                    delta = min(delta, self.unit_cap)
                else:
                    delta = max(delta, -self.unit_cap)
            if delta > 0:
                ctx.submit_order(sym, qty=delta, side="buy")
            elif delta < 0:
                ctx.submit_order(sym, qty=abs(delta), side="sell")
