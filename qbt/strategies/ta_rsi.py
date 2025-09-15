from __future__ import annotations
import pandas as pd
from .base import Strategy
def _rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff(); gain = delta.clip(lower=0).ewm(alpha=1/window, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/window, adjust=False).mean(); rs = gain/(loss.replace(0, 1e-12))
    return 100 - (100/(1+rs))
class RSIStrategy(Strategy):
    def __init__(self, data: pd.DataFrame, params: dict | None = None):
        super().__init__(params=params); self.data = data
        self.symbol = self.params.get("symbol"); assert self.symbol
        self.unit = int(self.params.get("unit", 100))
        self.lookback = int(self.params.get("lookback", 14))
        self.lower = float(self.params.get("lower", 30)); self.upper = float(self.params.get("upper", 70))
        self.data['rsi'] = _rsi(self.data['close'], window=self.lookback)
    def on_bar(self, ctx):
        ts = ctx.now; rsi = self.data.loc[ts,'rsi']
        if pd.isna(rsi): return
        pos_qty = ctx.portfolio.position.qty if hasattr(ctx.portfolio,'position') else 0
        if rsi < self.lower and pos_qty <= 0:
            ctx.submit_order(self.symbol, qty=self.unit, side='buy')
        elif rsi > self.upper and pos_qty > 0:
            ctx.submit_order(self.symbol, qty=pos_qty, side='sell')
