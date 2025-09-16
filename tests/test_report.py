import pandas as pd
import numpy as np
from pathlib import Path

from qbt.report.report import generate_report

def test_generate_report_creates_files(tmp_path: Path):
    idx = pd.date_range("2020-01-01", periods=50, freq="D")
    nav = pd.Series(np.linspace(100, 115, len(idx)), index=idx, name="equity")
    generate_report(nav, name="pytest_demo")
    reports = Path("reports")
    assert (reports / "pytest_demo_metrics.csv").exists()
    assert (reports / "pytest_demo_metrics.md").exists()
    assert (reports / "pytest_demo_equity.png").exists()
    assert (reports / "pytest_demo_drawdown.png").exists()
