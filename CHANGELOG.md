# Changelog

## [v0.3.0] - 2025-09-15
### Added
- Event-driven backtest engine (`qbt/core/event_engine.py`) with intraday minute-bar support
- Trade-level metrics: win rate, profit factor, avg win/loss, max win/loss
- Example script: `examples/run_event_driven_demo.py`
- Updated README with image placeholders for equity and Streamlit screenshots

### Changed
- README.md reorganized: integrated v0.2 usage guide with new v0.3.0 features
- Streamlit app emphasized as interactive dashboard

### Fixed
- Clarified Information Ratio requires benchmark NAV

---

## [v0.2.0] - 2025-09-10
### Added
- CLI entry point `qbt-lite`
- Config-driven runs (YAML/JSON)
- New strategies: Bollinger Bands, RSI, MACD
- Reporting module: metrics table + equity & drawdown charts
- Streamlit app (`streamlit_app.py`) for interactive runs
- Extended metrics: Sortino, Calmar, Information Ratio

### Changed
- Project structured into `qbt/` package
- Improved README with installation, usage, and demo

---

## [v0.1.0] - Initial release
### Added
- Basic backtest engine (daily bar, vectorized)
- SMA crossover & Momentum strategies
- Metrics: annual_return, annual_vol, Sharpe, Max Drawdown, Total Return
- Simple reporting of performance summary
