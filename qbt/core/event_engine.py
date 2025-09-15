from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional, Iterable
import pandas as pd
import numpy as np

@dataclass
class MarketEvent:
    timestamp: pd.Timestamp
    bar: pd.Series
    symbol: str

@dataclass
class OrderEvent:
    timestamp: pd.Timestamp
    symbol: str
    side: str  # 'buy'|'sell'
    qty: int

@dataclass
class FillEvent:
    timestamp: pd.Timestamp
    symbol: str
    side: str
    qty: int
    price: float
    fee: float = 0.0

class DataHandler:
    def __init__(self, data_map: Dict[str, pd.DataFrame]):
        self.data_map = {s: df.copy() for s, df in data_map.items()}
        for df in self.data_map.values():
            assert all(c in df.columns for c in ['open','high','low','close','volume'])
        union_idx = None
        for df in self.data_map.values():
            union_idx = df.index if union_idx is None else union_idx.union(df.index)
        for s in list(self.data_map.keys()):
            self.data_map[s] = self.data_map[s].reindex(union_idx).ffill()
        self.index = union_idx

    def __iter__(self) -> Iterable[MarketEvent]:
        syms = list(self.data_map.keys())
        for ts in self.index:
            for s in syms:
                yield MarketEvent(timestamp=ts, bar=self.data_map[s].loc[ts], symbol=s)

class BrokerED:
    def __init__(self, commission_bps: float = 0.0005, slippage: float = 0.0):
        self.commission_bps = commission_bps
        self.slippage = slippage
        self._orders: List[OrderEvent] = []

    def place_order(self, order: OrderEvent):
        self._orders.append(order)

    def process(self, ts: pd.Timestamp, price_lookup: Dict[str, float]) -> List[FillEvent]:
        fills: List[FillEvent] = []
        for o in self._orders:
            px = price_lookup[o.symbol] + (self.slippage if o.side == 'buy' else -self.slippage)
            fee = abs(px * o.qty) * self.commission_bps
            fills.append(FillEvent(timestamp=ts, symbol=o.symbol, side=o.side, qty=o.qty, price=px, fee=fee))
        self._orders.clear()
        return fills

class PortfolioED:
    def __init__(self, starting_cash: float = 100_000.0):
        self.cash = float(starting_cash)
        self.positions: Dict[str, int] = {}
        self.timestamps: List[pd.Timestamp] = []
        self.equity: List[float] = []
        self.fills_log: List[Dict] = []

    def on_fill(self, fill: FillEvent):
        sign = 1 if fill.side == 'buy' else -1
        qty = sign * fill.qty
        self.positions[fill.symbol] = self.positions.get(fill.symbol, 0) + qty
        self.cash -= fill.price * qty + fill.fee
        self.fills_log.append({'timestamp': fill.timestamp, 'symbol': fill.symbol, 'side': fill.side,
                               'qty': fill.qty, 'price': fill.price, 'fee': fill.fee})

    def mark_to_market(self, ts: pd.Timestamp, prices: Dict[str, float]):
        eq = self.cash
        for sym, qty in self.positions.items():
            eq += qty * prices.get(sym, 0.0)
        self.timestamps.append(ts)
        self.equity.append(eq)

    def equity_series(self) -> pd.Series:
        return pd.Series(self.equity, index=pd.DatetimeIndex(self.timestamps), name='equity')

    def fills_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.fills_log)

class ContextED:
    def __init__(self, now, bar, symbol, portfolio, submit_order):
        self.now = now; self.data = bar; self.symbol = symbol
        self.portfolio = portfolio; self.submit_order = submit_order

class MinuteSMA:
    def __init__(self, data: pd.DataFrame, short: int = 10, long: int = 30, symbol: str = "MOCK", unit: int = 10):
        self.data = data; self.short=short; self.long=long; self.symbol=symbol; self.unit=unit
        self.data['sma_s'] = self.data['close'].rolling(self.short, min_periods=1).mean()
        self.data['sma_l'] = self.data['close'].rolling(self.long, min_periods=1).mean()
    def on_bar(self, ctx: ContextED):
        row = self.data.loc[ctx.now]
        cross_up = row['sma_s'] > row['sma_l']
        pos = ctx.portfolio.positions.get(self.symbol, 0)
        if cross_up and pos <= 0:
            ctx.submit_order(OrderEvent(timestamp=ctx.now, symbol=self.symbol, side='buy', qty=self.unit))
        elif (not cross_up) and pos > 0:
            ctx.submit_order(OrderEvent(timestamp=ctx.now, symbol=self.symbol, side='sell', qty=pos))

class EventDrivenEngine:
    def __init__(self, data_map: Dict[str, pd.DataFrame], strategy_map: Dict[str, MinuteSMA],
                 starting_cash: float = 100_000.0, broker: Optional[BrokerED] = None):
        self.dh = DataHandler(data_map); self.strategy_map=strategy_map
        self.broker = broker or BrokerED(); self.portfolio = PortfolioED(starting_cash=starting_cash)
        self.last_prices: Dict[str, float] = {}

    def run(self) -> pd.Series:
        for ev in self.dh:
            if self.last_prices:
                self.portfolio.mark_to_market(ev.timestamp, self.last_prices)
            self.last_prices[ev.symbol] = float(ev.bar['close'])
            strat = self.strategy_map.get(ev.symbol)
            if strat:
                ctx = ContextED(ev.timestamp, ev.bar, ev.symbol, self.portfolio, self.broker.place_order)
                strat.on_bar(ctx)
            open_prices = {s: float(df.loc[ev.timestamp]['open']) if ev.timestamp in df.index else self.last_prices.get(s, np.nan)
                           for s, df in self.dh.data_map.items()}
            for fill in self.broker.process(ev.timestamp, open_prices):
                self.portfolio.on_fill(fill)
        if self.last_prices:
            self.portfolio.mark_to_market(list(self.dh.index)[-1], self.last_prices)
        return self.portfolio.equity_series()
