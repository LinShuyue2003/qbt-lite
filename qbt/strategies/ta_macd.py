from __future__ import annotations
import pandas as pd
from .base import Strategy
def _ema(series: pd.Series, span: int) -> pd.Series: return series.ewm(span=span, adjust=False).mean()
class MACDStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, params: dict | None = None):
        super().__init__(params=params); self.data = data
        self.symbol = self.params.get("symbol"); assert self.symbol
        self.unit = int(self.params.get("unit", 100))
        self.fast = int(self.params.get("fast", 12)); self.slow = int(self.params.get("slow", 26)); self.signal = int(self.params.get("signal", 9))
        macd = _ema(self.data['close'], self.fast) - _ema(self.data['close'], self.slow)
        sig = macd.ewm(span=self.signal, adjust=False).mean()
        self.data['macd']=macd; self.data['signal']=sig; self.prev_diff=None
    def on_bar(self, ctx):
        ts = ctx.now; row = self.data.loc[ts]
        if row[['macd','signal']].isna().any(): return
        diff = row['macd'] - row['signal']; pos_qty = ctx.portfolio.position.qty if hasattr(ctx.portfolio,'position') else 0
        if self.prev_diff is not None:
            if self.prev_diff <= 0 and diff > 0 and pos_qty <= 0: ctx.submit_order(self.symbol, qty=self.unit, side='buy')
            if self.prev_diff >= 0 and diff < 0 and pos_qty > 0: ctx.submit_order(self.symbol, qty=pos_qty, side='sell')
        self.prev_diff = diff
