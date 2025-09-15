from __future__ import annotations
import pandas as pd
from .base import Strategy

class SmaCross(Strategy):
    """Simple moving-average crossover strategy (single symbol, full long / flat).

    Rules
    -----
    - Compute SMA_short and SMA_long using the *close* price.
    - If SMA_short crosses above SMA_long -> go long (buy to full size).
    - If SMA_short crosses below SMA_long -> exit to flat (sell all).

    Parameters
    ----------
    params : dict
        short_window : int, default 10
        long_window  : int, default 30
        symbol       : str, required
        unit         : int, default 100  (trade in fixed lots)
    """
    def __init__(self, data: pd.DataFrame, params: dict | None = None):
        super().__init__(params=params)
        self.data = data
        self.short = int(self.params.get("short_window", 10))
        self.long = int(self.params.get("long_window", 30))
        if self.short >= self.long:
            raise ValueError("short_window must be < long_window")
        self.symbol = self.params.get("symbol")
        if not self.symbol:
            raise ValueError("symbol is required")
        self.unit = int(self.params.get("unit", 100))

        # Precompute moving averages to make on_bar trivial
        self.data['sma_short'] = self.data['close'].rolling(self.short).mean()
        self.data['sma_long']  = self.data['close'].rolling(self.long).mean()

        # We keep track of previous signal to detect a cross
        self.prev_above = None

    def on_bar(self, ctx):
        ts = ctx.now
        row = self.data.loc[ts]
        sma_s = row['sma_short']
        sma_l = row['sma_long']
        if pd.isna(sma_s) or pd.isna(sma_l):
            return  # wait until MAs are defined

        above = sma_s > sma_l
        if self.prev_above is None:
            self.prev_above = above
            return

        pos_qty = ctx.portfolio.position.qty

        # Cross up: go long (buy up to 1 unit position)
        if (not self.prev_above) and above:
            if pos_qty <= 0:
                ctx.submit_order(self.symbol, qty=self.unit, side='buy')

        # Cross down: exit to flat
        if self.prev_above and (not above):
            if pos_qty > 0:
                ctx.submit_order(self.symbol, qty=pos_qty, side='sell')

        self.prev_above = above
