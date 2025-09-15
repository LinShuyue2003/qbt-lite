from __future__ import annotations
from typing import Dict, Optional
import pandas as pd
from .broker import Broker, Order
from .portfolio_multi import PortfolioMulti

class ContextMulti:
    def __init__(self, now, data_bar_map: Dict[str, pd.Series], portfolio: PortfolioMulti, submit_order_cb, submit_target_weights_cb):
        self.now = now
        self.data = data_bar_map
        self.portfolio = portfolio
        self.submit_order = submit_order_cb
        self.submit_target_weights = submit_target_weights_cb
        self.symbols = list(data_bar_map.keys())

class BacktestEngineMulti:
    def __init__(self, data_map: Dict[str, pd.DataFrame], strategy, starting_cash: float = 100_000.0, broker: Optional[Broker] = None):
        if not data_map:
            raise ValueError("data_map is empty")
        indices = [df.index for df in data_map.values()]
        common = indices[0]
        for idx in indices[1:]:
            common = common.intersection(idx)
        if len(common) < 3:
            raise ValueError("Not enough overlapping timestamps.")
        self.data_map = {sym: df.loc[common].sort_index() for sym, df in data_map.items()}
        for sym, df in self.data_map.items():
            for col in ["open","high","low","close","volume"]:
                if col not in df.columns:
                    raise ValueError(f"{sym} missing column: {col}")
        self.symbols = list(self.data_map.keys())
        self.index = common
        self.strategy = strategy
        self.portfolio = PortfolioMulti(starting_cash=starting_cash)
        self.broker = broker or Broker()
        self._pending: Dict[str, Order] = {}

    def submit_order(self, symbol: str, qty: int, side: str):
        if symbol not in self.symbols:
            raise ValueError(f"Unknown symbol: {symbol}")
        self._pending[symbol] = Order(symbol=symbol, qty=int(qty), side=side)

    def submit_target_weights(self, weights: Dict[str, float], prices: Dict[str, float]):
        total = sum(max(w, 0.0) for w in weights.values())
        if total <= 0:
            return
        weights = {sym: max(0.0, w) / total for sym, w in weights.items() if sym in self.symbols}
        equity = self.portfolio.cash
        for sym in self.symbols:
            if sym in self.portfolio.positions:
                equity += self.portfolio.positions[sym].qty * prices[sym]
        for sym in self.symbols:
            target_val = weights.get(sym, 0.0) * equity
            px = prices[sym]
            current_qty = self.portfolio.positions.get(sym, None).qty if sym in self.portfolio.positions else 0
            target_qty = int(target_val // max(px, 1e-8))
            delta = target_qty - current_qty
            if delta > 0:
                self.submit_order(sym, qty=delta, side="buy")
            elif delta < 0:
                self.submit_order(sym, qty=abs(delta), side="sell")

    def run(self):
        idx = self.index
        for i, ts in enumerate(idx):
            last_prices = {sym: self.data_map[sym].iloc[i]["close"] for sym in self.symbols}
            self.portfolio.mark_to_market(ts, last_prices)
            bar_map = {sym: self.data_map[sym].iloc[i] for sym in self.symbols}
            ctx = ContextMulti(now=ts, data_bar_map=bar_map, portfolio=self.portfolio,
                               submit_order_cb=self.submit_order,
                               submit_target_weights_cb=lambda w: self.submit_target_weights(w, last_prices))
            self.strategy.on_bar(ctx)
            if self._pending and i < len(idx):
                for sym, order in list(self._pending.items()):
                    open_px = self.data_map[sym].iloc[i]["open"]
                    exec_px = self.broker.transact(price=open_px, order=order)
                    fee = self.broker.commission(exec_px, order.qty)
                    self.portfolio.on_fill(timestamp=ts, symbol=sym, executed_price=exec_px, qty=order.qty, side=order.side, fee=fee)
                self._pending.clear()
        return self.portfolio.equity_series()
