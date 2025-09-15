from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

@dataclass
class Position:
    qty: int = 0
    cost_basis: float = 0.0

class PortfolioMulti:
    """Cash + multi-symbol positions portfolio."""
    def __init__(self, starting_cash: float = 100_000.0):
        self.cash = float(starting_cash)
        self.positions: Dict[str, Position] = {}
        self.equity_history = []

    def _pos(self, symbol: str) -> Position:
        if symbol not in self.positions:
            self.positions[symbol] = Position()
        return self.positions[symbol]

    def on_fill(self, timestamp, symbol: str, executed_price: float, qty: int, side: str, fee: float):
        pos = self._pos(symbol)
        if side == "buy":
            cash_delta = -(executed_price * qty) - fee
            self.cash += cash_delta
            total_qty = pos.qty + qty
            if total_qty > 0:
                pos.cost_basis = (pos.cost_basis * pos.qty + executed_price * qty) / total_qty
            else:
                pos.cost_basis = 0.0
            pos.qty += qty
        else:
            cash_delta = (executed_price * qty) - fee
            self.cash += cash_delta
            pos.qty -= qty
            if pos.qty == 0:
                pos.cost_basis = 0.0

    def mark_to_market(self, timestamp, last_prices: Dict[str, float]):
        equity = self.cash
        for sym, pos in self.positions.items():
            px = last_prices.get(sym)
            if px is not None:
                equity += pos.qty * px
        self.equity_history.append((timestamp, equity))

    def equity_series(self):
        import pandas as pd
        if not self.equity_history:
            return pd.Series(dtype=float)
        idx, vals = zip(*self.equity_history)
        return pd.Series(vals, index=idx, name="equity").sort_index()
