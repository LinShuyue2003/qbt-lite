from __future__ import annotations
import pandas as pd
from typing import Dict

def trade_stats_from_fills(fills: pd.DataFrame) -> Dict[str, float]:
    if fills is None or len(fills) == 0:
        return {k: float('nan') for k in ['num_trades','win_rate','profit_factor','avg_win','avg_loss','max_win','max_loss']}
    if 'trade_id' in fills.columns:
        pnl = fills.groupby('trade_id', as_index=False)['pnl'].sum()['pnl']
    else:
        pnl = fills['pnl']
    num = len(pnl)
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    win_rate = float(len(wins) / num) if num > 0 else float('nan')
    total_win = float(wins.sum()) if len(wins) > 0 else 0.0
    total_loss = float(-losses.sum()) if len(losses) > 0 else 0.0
    profit_factor = float('nan') if total_loss == 0 else float(total_win / total_loss)
    avg_win = float(wins.mean()) if len(wins) > 0 else float('nan')
    avg_loss = float(losses.mean()) if len(losses) > 0 else float('nan')
    max_win = float(wins.max()) if len(wins) > 0 else float('nan')
    max_loss = float(losses.min()) if len(losses) > 0 else float('nan')
    return {'num_trades': float(num), 'win_rate': float(win_rate), 'profit_factor': float(profit_factor),
            'avg_win': float(avg_win), 'avg_loss': float(avg_loss), 'max_win': float(max_win), 'max_loss': float(max_loss)}
