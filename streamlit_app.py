import streamlit as st
import pandas as pd
from qbt.core.engine import BacktestEngine
from qbt.core.broker import Broker
from qbt.strategies.sma_cross import SmaCross
from qbt.strategies.momentum import Momentum
from qbt.strategies.ta_bbands import BollingerBands
from qbt.strategies.ta_rsi import RSIStrategy
from qbt.strategies.ta_macd import MACDStrategy
from qbt.core.metrics import performance_from_nav
from qbt.report.report import generate_report
from qbt.data.loader import load_csv

st.title("QBT-Lite Interactive Backtester")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
strategy = st.selectbox("Choose strategy", ["sma", "momentum", "bbands", "rsi", "macd"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)

    # Ensure numeric columns
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    symbol = "UPLOADED"
    if strategy == "sma":
        short = st.number_input("Short Window", value=10)
        long = st.number_input("Long Window", value=30)
        strat = SmaCross(df, {"short_window": short, "long_window": long, "symbol": symbol, "unit": 100})
    elif strategy == "momentum":
        lookback = st.number_input("Lookback", value=60)
        strat = Momentum(df, {"lookback": lookback, "threshold": 0.0, "symbol": symbol, "unit": 100})
    elif strategy == "bbands":
        lookback = st.number_input("Lookback", value=20)
        strat = BollingerBands(df, {"lookback": lookback, "num_std": 2.0, "symbol": symbol, "unit": 100})
    elif strategy == "rsi":
        lookback = st.number_input("Lookback", value=14)
        strat = RSIStrategy(df, {"lookback": lookback, "lower": 30, "upper": 70, "symbol": symbol, "unit": 100})
    elif strategy == "macd":
        strat = MACDStrategy(df, {"fast": 12, "slow": 26, "signal": 9, "symbol": symbol, "unit": 100})

    engine = BacktestEngine(data=df, symbol=symbol, strategy=strat, starting_cash=100_000.0,
                            broker=Broker(commission_bps=0.0005, slippage=0.01))
    nav = engine.run()
    nav_norm = nav / nav.iloc[0]
    st.line_chart(nav_norm)

    perf = performance_from_nav(nav_norm)
    st.write("Performance:", perf)

    if st.button("Generate Report"):
        metrics = generate_report(nav, "streamlit_run")
        st.success("Report generated in reports/")
