from __future__ import annotations
import pandas as pd
from .base import Strategy
class BollingerBands(Strategy):
    def __init__(self, data: pd.DataFrame, params: dict | None = None):
        super().__init__(params=params)
        self.data = data
        self.symbol = self.params.get("symbol"); assert self.symbol
        self.unit = int(self.params.get("unit", 100))
        self.lookback = int(self.params.get("lookback", 20))
        self.num_std = float(self.params.get("num_std", 2.0))
        mid = self.data['close'].rolling(self.lookback).mean()
        std = self.data['close'].rolling(self.lookback).std(ddof=0)
        self.data['bb_mid'] = mid; self.data['bb_up'] = mid + self.num_std * std; self.data['bb_lo'] = mid - self.num_std * std
    def on_bar(self, ctx):
        ts = ctx.now; row = self.data.loc[ts]
        if row[['bb_up','bb_lo']].isna().any(): return
        pos_qty = ctx.portfolio.position.qty if hasattr(ctx.portfolio,'position') else 0
        if row['close'] > row['bb_up'] and pos_qty <= 0:
            ctx.submit_order(self.symbol, qty=self.unit, side='buy')
        elif row['close'] < row['bb_lo'] and pos_qty > 0:
            ctx.submit_order(self.symbol, qty=pos_qty, side='sell')
