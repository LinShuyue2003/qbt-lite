from __future__ import annotations
import pandas as pd
from typing import Optional
from .broker import Broker, Order
from .portfolio import Portfolio

class Context:
    # Lightweight context passed to strategies each bar.
    def __init__(self, now, data_slice: pd.Series, portfolio: Portfolio, submit_order_cb):
        self.now = now
        self.data = data_slice       # current row (open/high/low/close/volume)
        self.portfolio = portfolio
        self.submit_order = submit_order_cb  # function(symbol, qty, side)

class BacktestEngine:
    """Event-driven backtest engine (single symbol, daily bars).

    Execution model
    ---------------
    - Signals are generated on bar t (after seeing close[t]).
    - Market orders are executed at the NEXT bar open (open[t+1]) with slippage/commission.
    - This avoids lookahead bias for close-to-next-open execution.
    """
    def __init__(self,
                 data: pd.DataFrame,
                 symbol: str,
                 strategy,
                 starting_cash: float = 100_000.0,
                 broker: Optional[Broker] = None):
        self.data = data.copy()
        self.symbol = symbol
        self.strategy = strategy
        self.portfolio = Portfolio(starting_cash=starting_cash)
        self.broker = broker or Broker()
        self._pending_order = None  # will execute at next bar open

        # Basic input checks
        for col in ["open","high","low","close","volume"]:
            if col not in self.data.columns:
                raise ValueError(f"Data missing required column: {col}")
        if not isinstance(self.data.index, pd.DatetimeIndex):
            raise ValueError("Data index must be DatetimeIndex.")
        self.data = self.data.sort_index()

    def submit_order(self, symbol: str, qty: int, side: str):
        """Queue a market order to be executed on the next bar open.

        For MVP we allow only a single pending order per bar. The last one wins.
        """
        self._pending_order = Order(symbol=symbol, qty=int(qty), side=side)

    def run(self):
        # Iterate bars and execute: mark-to-market -> strategy -> execute pending on next open
        index = self.data.index
        for i, ts in enumerate(index):
            row = self.data.iloc[i]
            # Mark-to-market at close
            self.portfolio.mark_to_market(ts, last_price=row["close"])

            # Build context for strategy
            ctx = Context(now=ts, data_slice=row, portfolio=self.portfolio, submit_order_cb=self.submit_order)
            # Strategy generates a signal using CURRENT bar
            self.strategy.on_bar(ctx)

            # If there is a pending order from PREVIOUS bar, execute now at this bar's OPEN
            if self._pending_order is not None and i < len(index):
                # Execute at current bar open (order placed last bar)
                exec_price = self.broker.transact(price=row["open"], order=self._pending_order)
                fee = self.broker.commission(exec_price, self._pending_order.qty)
                self.portfolio.on_fill(timestamp=ts,
                                       executed_price=exec_price,
                                       qty=self._pending_order.qty,
                                       side=self._pending_order.side,
                                       fee=fee)
                self._pending_order = None

        # Return equity series for convenience
        return self.portfolio.equity_series()
