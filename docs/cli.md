# CLI Reference 💻

Run from repository root after installation.

## Examples
```bash
qbt-lite --strategy momentum --symbol MOCK --lookback 60 --report_name cli_mom
python -m qbt.cli --strategy topn_momentum --config examples/configs/multi_momentum.yml --report_name demo_multi
```

## Options
- `--strategy` {sma|momentum|topn_momentum|bbands|rsi|macd} (default: sma)
- `--config` YAML config file
- `--symbol` ticker symbol (default: MOCK)
- `--data_csv` path to CSV data
- `--lookback` indicator lookback (default: 60)
- `--short` fast MA for SMA (default: 10)
- `--long` slow MA for SMA (default: 30)
- `--top_n` for Top-N momentum (default: 2)
- `--commission_bps` commission bps (default: 0.0005)
- `--slippage` price impact (default: 0.01)
- `--unit` order size (default: 1000)
- `--report_name` output prefix (default: cli_run)
