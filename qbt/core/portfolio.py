from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

@dataclass
class Position:
    qty: int = 0
    cost_basis: float = 0.0  # average price

class Portfolio:
    """Cash + single-symbol position portfolio (MVP).

    Notes
    -----
    - Single-symbol simplifies bookkeeping for beginners.
    - Extending to multi-symbol requires using a dict[str, Position].
    """
    def __init__(self, starting_cash: float = 100_000.0):
        self.cash = float(starting_cash)
        self.position = Position()
        self.equity_history = []  # list of (timestamp, equity)

    def _update_cost_basis_on_buy(self, price: float, qty: int):
        # Weighted average price update
        total_qty = self.position.qty + qty
        if total_qty <= 0:
            # If fully closed (shouldn't happen on buy), reset basis
            self.position.cost_basis = price
        else:
            new_basis = (self.position.cost_basis * self.position.qty + price * qty) / total_qty
            self.position.cost_basis = new_basis

    def on_fill(self, timestamp, executed_price: float, qty: int, side: str, fee: float):
        """Apply a fill to the portfolio.

        Parameters
        ----------
        timestamp : any
            Time label to record equity history.
        executed_price : float
            Fill price.
        qty : int
            Quantity filled.
        side : str
            'buy' or 'sell'.
        fee : float
            Commission in currency deducted from cash.
        """
        if side == 'buy':
            cash_delta = -(executed_price * qty) - fee
            self.cash += cash_delta
            self._update_cost_basis_on_buy(executed_price, qty)
            self.position.qty += qty
        else:  # sell
            cash_delta = (executed_price * qty) - fee
            self.cash += cash_delta
            self.position.qty -= qty
            if self.position.qty == 0:
                # Reset basis when flat
                self.position.cost_basis = 0.0

    def mark_to_market(self, timestamp, last_price: float):
        """Record equity using the latest market price."""
        position_value = self.position.qty * last_price
        equity = self.cash + position_value
        self.equity_history.append((timestamp, equity))

    def equity_series(self):
        import pandas as pd
        if not self.equity_history:
            return pd.Series(dtype=float)
        idx, vals = zip(*self.equity_history)
        return pd.Series(vals, index=idx, name="equity").sort_index()
