from __future__ import annotations
import pandas as pd
from .base import Strategy

class Momentum(Strategy):
    """Momentum strategy (single symbol, full long / flat by fixed unit).

    Idea
    ----
    If recent return over `lookback` bars exceeds `threshold`, we go long; otherwise flat.

    Parameters
    ----------
    params : dict
        lookback   : int, default 60
        threshold  : float, default 0.0  (e.g., 0.05 = +5% over lookback)
        symbol     : str, required
        unit       : int, default 100    (trade in fixed lots)
    """
    def __init__(self, data: pd.DataFrame, params: dict | None = None):
        super().__init__(params=params)
        self.data = data
        self.lookback = int(self.params.get("lookback", 60))
        self.threshold = float(self.params.get("threshold", 0.0))
        self.symbol = self.params.get("symbol")
        if not self.symbol:
            raise ValueError("symbol is required")
        self.unit = int(self.params.get("unit", 100))

        # Precompute momentum as percentage change over lookback
        self.data['mom'] = self.data['close'].pct_change(self.lookback)

    def on_bar(self, ctx):
        ts = ctx.now
        row = self.data.loc[ts]
        mom = row['mom']
        if pd.isna(mom):
            return

        pos_qty = ctx.portfolio.position.qty
        # Enter long when momentum is above threshold
        if mom > self.threshold and pos_qty <= 0:
            ctx.submit_order(self.symbol, qty=self.unit, side='buy')
        # Exit to flat when momentum is below/equal threshold
        if mom <= self.threshold and pos_qty > 0:
            ctx.submit_order(self.symbol, qty=pos_qty, side='sell')
