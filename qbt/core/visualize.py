from __future__ import annotations
import matplotlib.pyplot as plt
import pandas as pd

def plot_equity(nav: pd.Series, title: str = "Equity Curve", save_path: str | None = None):
    """Plot the NAV/equity curve.

    Notes
    -----
    - For a quick report, you can also plot drawdown using metrics.compute_drawdown.
    """
    plt.figure(figsize=(10, 4))
    nav.plot()
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Equity")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    # Return figure handle for interactive use
    return plt.gcf()
