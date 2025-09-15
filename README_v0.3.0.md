# QBT-Lite 📈
A lightweight quantitative backtesting framework in Python

## v0.3.0 Highlights
- Daily vectorized engine (existing) + **NEW: event-driven engine** for intraday minute bars
- **Richer metrics**: Sharpe, Sortino, Calmar, Max Drawdown, Total Return, Information Ratio (*needs benchmark*), **win rate / profit factor**
- **Multi-asset ready** strategies (e.g., Top-N momentum), clear symbol/weights APIs
- **Streamlit app** for interactive backtests

## Install
```bash
python -m venv .venv
# .\.venv\Scripts\Activate.ps1  (Windows)   |   source .venv/bin/activate  (macOS/Linux)
pip install -U pip
pip install -e .
pip install pyyaml streamlit yfinance pytest
```

## Quick Start (Daily Vectorized)
```bash
qbt-lite --strategy momentum --symbol MOCK --lookback 60 --report_name cli_mom
# or
python -m qbt.cli --strategy topn_momentum --config examples/configs/multi_momentum.yml --report_name demo_multi
```
Outputs in `reports/`: `_metrics.csv/.md`, `_equity.png`, `_drawdown.png`

> **Image placeholder #1 (equity)** – insert `reports/xxx_equity.png` here  
> **Image placeholder #2 (drawdown)** – insert `reports/xxx_drawdown.png` here

## Event-Driven Demo (Intraday)
```bash
python -m examples.run_event_driven_demo
```
- Event flow: `Market → Strategy → Order → Fill`
- Broker: commission + slippage
- Portfolio: logs fills & equity
- Metrics: return-based + trade-level

> **Image placeholder #3 (event-driven equity)** – insert `reports/event_driven_demo_equity.png` here

## Streamlit (Interactive)
```bash
python -m streamlit run streamlit_app.py
```
Upload CSV with columns: `datetime, open, high, low, close, volume`  
Select strategy (SMA/Momentum/Bollinger/RSI/MACD), tune params, view equity live, export reports.

> **Image placeholder #4 (Streamlit screenshot)** – insert a screenshot of the UI with an equity chart

## Metrics
Return-based (`qbt.core.metrics.performance_from_nav`):
- `annual_return, annual_vol, sharpe, sortino, calmar, max_drawdown, total_return, information_ratio`

Trade-based (`qbt.analytics.metrics_ext.trade_stats_from_fills`):
- `num_trades, win_rate, profit_factor, avg_win, avg_loss, max_win, max_loss`

## Roadmap
- More data providers (tushare, ccxt)
- Order types (stop/limit), latency/partial fills
- Portfolio allocators (risk parity, vol targeting, Kelly)
