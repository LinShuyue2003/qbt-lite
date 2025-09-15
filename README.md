# qbt-lite (Mini Quant Backtester)

A teaching-first, minimal backtesting framework in Python that runs end-to-end:
**data → strategy → backtest → equity curve → metrics**.

> ⚠️ Simplified by design. Great for learning; not intended for live trading.

## Features
- CSV data loader (OHLCV)
- Event-driven backtest engine (daily bars, single symbol)
- Simple broker (commission bps, fixed slippage)
- Portfolio accounting (cash + position)
- Performance metrics (annual return, vol, Sharpe, max drawdown)
- Example strategy: SMA crossover
- Example script to run an end-to-end demo

## Quickstart

### 1) Install
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Run the example
```bash
python -m examples.run_sma_example
```

This will print metrics and save a chart to `examples/output/equity.png`.

## Project Layout
```
qbt/
  data/loader.py
  core/{engine.py,broker.py,portfolio.py,metrics.py,visualize.py}
  strategies/{base.py,sma_cross.py}
examples/
  run_sma_example.py
```

## Notes
- Execution model: signal at close[t] executes at open[t+1], to avoid lookahead bias.
- Commission is in **bps** (basis points) of traded notional; slippage is absolute price add-on/subtract.
- Extend to multi-symbol by generalizing `Portfolio` (use dict of positions) and adjusting `Engine`.

## License
MIT
