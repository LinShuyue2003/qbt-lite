"""qbt-lite: a minimal quant backtesting framework.

This package provides:
- Data loading (CSV to standardized DataFrame)
- A bar-by-bar backtest engine (single symbol MVP)
- A simple broker and portfolio
- Performance metrics and a basic visualization
- Example strategies (SMA crossover)

The design favors readability and teaching. Production features (e.g., exchange calendars,
corporate action handling, tick-level slippage) are intentionally simplified.
"""

__version__ = "0.1.0"
