# Strategies 📈

This section summarizes built-in strategies. See the module docstrings for details.

## SMA Crossover (`sma_cross.py`)
- Parameters: `short` (default 10), `long` (default 30)
- Signal: long when fast MA > slow MA; flat otherwise.

## Momentum (`momentum.py`)
- Parameter: `lookback` (default 60). Uses past return to compute momentum.

## Top-N Momentum (`topn_momentum.py`)
- Parameters: `lookback`, `top_n` (default 2). Ranks assets and allocates to top performers.

## Bollinger Bands (`ta_bbands.py`)
- Typical parameters: window, number of stds.
- Long near lower band; reduce/exit near upper band.

## RSI (`ta_rsi.py`)
- Typical parameter: period (e.g., 14). Mean-reversion behavior near overbought/oversold zones.

## MACD (`ta_macd.py`)
- EMAs and signal line; long when MACD crosses above signal.
