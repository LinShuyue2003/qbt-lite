from __future__ import annotations
import pandas as pd
from typing import Optional

REQUIRED_COLS = ["datetime", "open", "high", "low", "close", "volume"]

def load_csv(path: str, symbol: Optional[str] = None, tz: Optional[str] = None) -> pd.DataFrame:
    """Load OHLCV data from a CSV and return a standardized DataFrame.

    Parameters
    ----------
    path : str
        File path to the CSV.
    symbol : Optional[str]
        Symbol identifier to attach as a column if not present in the CSV.
    tz : Optional[str]
        Timezone to localize the datetime index; leave None to keep naive.

    Returns
    -------
    pd.DataFrame
        Columns: ['open','high','low','close','volume'] indexed by DatetimeIndex (ascending).
        If 'symbol' exists or provided, it's kept as a column for reference.

    Notes
    -----
    - Expected columns: datetime, open, high, low, close, volume (case-insensitive allowed).
    - For simplicity we assume the CSV is already adjusted (no split/dividend adjustments here).
    """
    df = pd.read_csv(path)
    lower_cols = {c.lower(): c for c in df.columns}
    # Normalize column names (case-insensitive)
    missing = [c for c in REQUIRED_COLS if c not in lower_cols]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")
    # Build a normalized frame
    df = df.rename(columns={lower_cols['datetime']:'datetime',
                            lower_cols['open']:'open',
                            lower_cols['high']:'high',
                            lower_cols['low']:'low',
                            lower_cols['close']:'close',
                            lower_cols['volume']:'volume'})
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime').drop_duplicates('datetime')
    df = df.set_index('datetime')
    if tz:
        # Localize naive -> tz; if already tz-aware, convert
        if df.index.tz is None:
            df.index = df.index.tz_localize(tz)
        else:
            df.index = df.index.tz_convert(tz)
    if 'symbol' not in df.columns and symbol is not None:
        df['symbol'] = symbol
    # Ensure numeric types
    for col in ['open','high','low','close','volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['open','high','low','close'])
    return df[['open','high','low','close','volume'] + (['symbol'] if 'symbol' in df.columns else [])]
