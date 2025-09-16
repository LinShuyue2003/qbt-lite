# Installation ⚙️

## Requirements
- Python 3.10+
- Dependencies: pandas, numpy, matplotlib, pytest, streamlit, plotly, yfinance, tushare (optional)

## Install from source
```bash
git clone https://github.com/LinShuyue2003/qbt-lite.git
cd qbt-lite

python -m venv .venv
source .venv/bin/activate   # Linux / Mac
.\.venv\Scripts\Activate.ps1   # Windows

pip install -U pip
pip install -e .
pip install 'qbt-lite[interactive]'
```

## Quick verification
```bash
python -m examples.run_sma_example
```
