from __future__ import annotations
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from qbt.core.metrics import performance_from_nav, compute_drawdown

def generate_report(nav: pd.Series, name: str, out_dir: str = "reports"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    nav_norm = nav / nav.iloc[0]
    perf = performance_from_nav(nav_norm, risk_free=0.0, periods_per_year=252)
    df = pd.DataFrame([perf])
    df.to_csv(Path(out_dir)/f"{name}_metrics.csv", index=False)
    df.to_markdown(Path(out_dir)/f"{name}_metrics.md", index=False)
    plt.figure(figsize=(10,4))
    nav_norm.plot()
    plt.title(f"Equity Curve ({name})")
    plt.xlabel("Date"); plt.ylabel("Equity")
    plt.tight_layout()
    plt.savefig(Path(out_dir)/f"{name}_equity.png", dpi=150)
    plt.close()
    dd = compute_drawdown(nav_norm)
    plt.figure(figsize=(10,3))
    dd.plot(color="red")
    plt.title(f"Drawdown ({name})")
    plt.xlabel("Date"); plt.ylabel("Drawdown")
    plt.tight_layout()
    plt.savefig(Path(out_dir)/f"{name}_drawdown.png", dpi=150)
    plt.close()
    print(f"Report saved to {out_dir}/")
    return perf
