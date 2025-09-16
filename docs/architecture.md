# Architecture 🏗️

QBT-Lite provides **two engines** and a modular set of components.

```
Data → Strategy → Engine → Broker → Portfolio → Metrics → Report → Visualization
```

## Engines
- **Vectorized Engines**: `qbt/core/engine.py` (single-asset), `qbt/core/engine_multi.py` (multi-asset)
- **Event-Driven Engine**: `qbt/core/event_engine.py` (intraday with events)

## Events (from `event_engine.py`)
- `MarketEvent(timestamp: pd.Timestamp, bar: pd.Series, symbol: str)`
- `FillEvent(timestamp: pd.Timestamp, symbol: str, side: str, qty: int, price: float, fee: float)`

## Broker
- `qbt/core/broker.py`: `transact(order)` applies `commission()` and slippage.

## Portfolio
- `on_fill(fill)`, `mark_to_market(last_prices)`, `equity_series()`.

## Metrics
- `performance_from_nav`, `compute_drawdown` (core)
- `trade_stats_from_fills` (analytics)

## Reports
- `qbt/report/report.py` writes CSV/MD and saves `equity.png` & `drawdown.png`.

## CLI
- `qbt/cli.py` exposes the backtester to the command line with common options.
