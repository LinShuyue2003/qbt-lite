# Usage Guide 📘

This guide explains how to run **QBT-Lite** using examples, the **CLI**, and the **event-driven engine**.

---

## Quick Start
```bash
python -m examples.run_sma_example
qbt-lite --strategy momentum --symbol MOCK --lookback 60 --report_name cli_mom
python -m examples.run_event_driven_demo
```

---

## CLI Reference (from `qbt/cli.py`)
The CLI accepts the following options:

- `--strategy` (default: `sma`) — choices: `sma`, `momentum`, `topn_momentum`, `bbands`, `rsi`, `macd`
- `--config` (default: `None`) — YAML config file path
- `--symbol` (default: `MOCK`) — single ticker symbol
- `--data_csv` (default: `None`) — path to CSV; if omitted, uses mock data / examples
- `--lookback` (default: `60`) — lookback window for momentum/indicators
- `--short` (default: `10`) — short MA window for SMA
- `--long` (default: `30`) — long MA window for SMA
- `--top_n` (default: `2`) — top N assets for `topn_momentum`
- `--commission_bps` (default: `0.0005`) — commission in bps
- `--slippage` (default: `0.01`) — slippage (price impact)
- `--unit` (default: `1000`) — order unit size (shares/contracts)
- `--report_name` (default: `cli_run`) — prefix for report files

Examples:
```bash
qbt-lite --strategy sma --symbol MOCK --short 10 --long 30 --report_name sma10x30
python -m qbt.cli --strategy topn_momentum --config examples/configs/multi_momentum.yml --report_name demo_multi
```

---

## Data Format (from `qbt/data/loader.py`)
CSV columns expected:
```
datetime, open, high, low, close, volume[, symbol]
```
- `datetime` must be parseable to timestamp
- Optional `symbol` column supports multi-asset inputs

---

## Daily Vectorized Backtests
### Single-Asset Momentum
```bash
python -m examples.run_momentum_example
```

### Multi-Asset Top-N Momentum
```bash
python -m qbt.cli --strategy topn_momentum --config examples/configs/multi_momentum.yml --report_name demo_multi
```

---

## Event-Driven Backtests
Run the intraday demo:
```bash
python -m examples.run_event_driven_demo
```
**Event types:** `MarketEvent(timestamp, bar, symbol)`, `FillEvent(timestamp, symbol, side, qty, price, fee)`  
**Core flow:** Market → Strategy → Order → Broker → Portfolio  
**Broker:** `transact()` applies fees via `commission()` and slippage.  
**Portfolio:** handles `on_fill()`, `mark_to_market()`, and outputs `equity_series()` plus `fills_dataframe()`.

**Trade stats:** `qbt.analytics.metrics_ext.trade_stats_from_fills(fills_df)`

Outputs saved to `reports/`:
- `qbt-lite-0.3.0/reports/*_metrics.csv` / `*_metrics.md`
- `qbt-lite-0.3.0/reports/*_equity.png` / `*_drawdown.png`

---

## Performance Metrics
From `qbt/core/metrics.py`:
- `compute_drawdown(nav)` — drawdown series and max drawdown
- `performance_from_nav(nav)` — annualized return/volatility, Sharpe, etc.

From `qbt/analytics/metrics_ext.py`:
- `trade_stats_from_fills(fills_df)` — trade-level metrics: win rate, profit factor, avg win/loss, etc.

---

## Strategies (detected in `qbt/strategies/`)
Available modules: momentum, sma_cross, ta_bbands, ta_macd, ta_rsi, topn_momentum
- `sma_cross.py` — moving-average crossover (`--short`, `--long`)
- `momentum.py` — momentum with `--lookback`
- `topn_momentum.py` — multi-asset ranking with `--top_n`
- `ta_bbands.py`, `ta_rsi.py`, `ta_macd.py` — Bollinger Bands, RSI, MACD

