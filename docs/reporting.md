# Reporting & Metrics 📊

Outputs are written to `reports/` with a `report_name` prefix.

## Files
- `*_metrics.csv` — machine-readable metrics
- `*_metrics.md` — human-readable summary
- `*_equity.png` — equity curve
- `*_drawdown.png` — drawdown chart

## Core Metrics (`qbt/core/metrics.py`)
- Annualized Return, Volatility
- Sharpe Ratio
- Drawdown series & Max Drawdown (`compute_drawdown`)

## Trade Metrics (`qbt/analytics/metrics_ext.py`)
- `trade_stats_from_fills(fills_df)` returns:
  - `num_trades`, `win_rate`, `profit_factor`
  - `avg_win`, `avg_loss`, `max_win`, `max_loss`
