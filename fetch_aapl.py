import yfinance as yf, pandas as pd, os
os.makedirs("examples/data_sample", exist_ok=True)
df = yf.download("AAPL", start="2018-01-01", progress=False)
df = df.rename(columns={"Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"}).reset_index().rename(columns={"Date":"datetime"})
df.to_csv("examples/data_sample/AAPL.csv", index=False)
print("saved AAPL.csv")