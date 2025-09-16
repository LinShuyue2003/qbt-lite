# QBT-Lite – Detailed Usage Guide

(1) Installation
----------------
```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -U pip
pip install -e .
pip install 'qbt-lite[interactive]'
```

(2) Daily Vectorized Backtests
------------------------------
Single-Asset (CLI):
```bash
qbt-lite --strategy momentum --symbol MOCK --lookback 60 --report_name cli_mom
```

Multi-Asset (Config):
```yaml
# examples/configs/multi_momentum.yml
strategy: topn_momentum
params:
  lookback: 60
  top_n: 2
  commission_bps: 0.0005
  slippage: 0.01
data:
  source: mock
  symbols: [AAA, BBB, CCC]
  start: 2018-01-01
  end: 2020-06-01
```
Run:
```bash
python -m qbt.cli --strategy topn_momentum --config examples/configs/multi_momentum.yml --report_name demo_multi
```

(3) Event-Driven Backtests
--------------------------
Run demo:
```bash
python -m examples.run_event_driven_demo
```
Outputs saved to `reports/event_driven_demo_*`.
Trade metrics via `qbt.analytics.metrics_ext.trade_stats_from_fills`.

(4) Streamlit
-------------
```bash
python -m streamlit run streamlit_app.py
```

(5) Parameter Tuning
--------------------
- CLI flags or YAML `params:`
- Streamlit sliders

(6) Outputs
-----------
- `*_metrics.csv`, `*_metrics.md`, `*_equity.png`, `*_drawdown.png`
- Event-driven fills via `engine.portfolio.fills_dataframe()`

(7) Tests & CI
--------------
```bash
pytest -q
```
GitHub Actions workflow: `.github/workflows/ci.yml`