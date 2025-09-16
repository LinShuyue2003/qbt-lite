# Data Sources 📡

## CSV Format
Columns required:
```
datetime, open, high, low, close, volume[, symbol]
```
- `datetime` will be parsed to `pd.Timestamp`
- Optional `symbol` supports multi-asset files

## yfinance Example
```python
import yfinance as yf, pandas as pd
df = yf.download("AAPL", start="2018-01-01", progress=False)
df = df.rename(columns={
    "Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"
}).reset_index().rename(columns={"Date":"datetime"})
df.to_csv("examples/data_sample/AAPL.csv", index=False)
```

## Notes
- Ensure timezone consistency for intraday/event-driven runs.
- Commission & slippage are configurable via CLI or config.
