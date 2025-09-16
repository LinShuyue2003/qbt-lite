# QBT-Lite 📈  
A lightweight quantitative backtesting framework in Python

![CI](https://github.com/LinShuyue2003/qbt-lite/actions/workflows/ci.yml/badge.svg)

---

## 🌟 Project Overview
QBT-Lite is a **lightweight quantitative backtesting framework** written in Python.  
It covers the full workflow:  
**data import → strategy execution → order simulation → performance evaluation → automated reporting → interactive visualization**.

Designed as both a **learning-friendly framework** and a **portfolio project** showcasing quantitative research & engineering skills.

**Resume Highlights:**
- End-to-end backtesting: from data loading to reporting  
- Supports **multi-asset portfolio backtesting** and strategy evaluation  
- Multiple trading strategies (SMA, Momentum, Bollinger Bands, RSI, MACD)  
- Key metrics (Sharpe, Sortino, Calmar, Max Drawdown, etc.)  
- Automated reports (CSV, Markdown, PNG charts)  
- Interactive **Streamlit app** for strategy testing  
- **NEW in v0.3.0**: Event-driven backtesting engine (intraday), trade-level metrics (win rate, profit factor, etc.)

---

## ⚙️ Tech Stack
- **Python 3.10+**
- **pandas**, **numpy** for data handling & calculations  
- **matplotlib** for visualization  
- **pytest** for testing  
- **streamlit** + **plotly** (optional, for interactive UI)  
- **yfinance / tushare** (optional, for real market data)  

---

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/LinShuyue2003/qbt-lite.git
cd qbt-lite

python -m venv .venv
source .venv/bin/activate   # Linux / Mac
.\.venv\Scripts\Activate.ps1   # Windows PowerShell

pip install -U pip
pip install -e .
```

Optional features:
```bash
pip install 'qbt-lite[interactive]'  # streamlit, plotly, yfinance, pytest, pyyaml
```

### 2. Run a Demo
Run SMA strategy:
```bash
python -m examples.run_sma_example
```
Run momentum strategy with CLI:
```bash
qbt-lite --strategy momentum --symbol MOCK --lookback 60 --report_name cli_mom
```

### 3. View Reports
Reports are saved in `reports/`:
- Performance metrics (`.csv`, `.md`)  
- Equity curve (`.png`)  
- Drawdown curve (`.png`)  

![Equity Curve](docs/event_driven_demo_equity.png)

---

## 🔹 Features

### Daily Backtests
- Vectorized backtesting on daily bars  
- Configurable via CLI or YAML  
- Supports multi-asset Top-N momentum  

### Event-Driven Backtests (NEW 🚀)
- Processes **intraday/minute bars** via event queue (Market → Strategy → Order → Fill)  
- Broker applies **commission + slippage**  
- Portfolio logs fills & equity  
- Produces both return-based & trade-level metrics  

### Interactive Dashboard
Run Streamlit app:
```bash
python -m streamlit run streamlit_app.py
```
Features: upload CSV, choose strategy, set parameters, see equity in real time.  

![Streamlit GUI](docs/Streamlit_screenshot.png)

---

## 📊 Example Metrics

| annual_return | sharpe | sortino | calmar | max_drawdown |
|---------------|--------|---------|--------|--------------|
| 0.1858        | 1.5473 | 2.4103  | 2.8895 | -0.0643      |

Trade-level (event-driven SMA, minute bars):  

| num_trades | win_rate | profit_factor | avg_win | avg_loss |
|------------|----------|---------------|---------|----------|
| 37         | 0.2973   | 1.2227        | 37.21   | -12.87   |

---

## 🧪 Tests & CI
Run unit tests:
```bash
pytest -q
```

GitHub Actions CI included.

---

## 🔮 Roadmap
- More advanced strategies (pairs trading, factor models, CTA futures)  
- Portfolio allocation (Kelly, risk parity, volatility targeting)  
- Live data integration (tushare, Alpaca API, ccxt for crypto)  
- Full Streamlit/Flask dashboard with parameter tuning  
- More order types (stop/limit, latency modeling)

---

## 📜 License
MIT License

---

## 🤝 Acknowledgements
For learning & demonstration purposes only. **Not financial advice.**
