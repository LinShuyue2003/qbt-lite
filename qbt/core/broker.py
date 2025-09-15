from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Order:
    """A very minimal market order representation.

    Attributes
    ----------
    symbol : str
        Ticker or identifier.
    qty : int
        Positive integer. For MVP we do not support shorting; sell is handled by selling current position.
    side : str
        'buy' or 'sell'.
    """
    symbol: str
    qty: int
    side: str  # 'buy' or 'sell'

class Broker:
    """A simple broker that applies commission and slippage in a naive way.

    Notes
    -----
    - Commission is a fixed bps (basis points) rate applied to traded notional (price * qty).
      Example: 10 bps = 0.001 = 0.1%
    - Slippage is a fixed absolute price add-on for buys, subtract for sells.
      Example: slippage=0.01 means buy at price+0.01, sell at price-0.01
    """
    def __init__(self, commission_bps: float = 0.0, slippage: float = 0.0):
        self.commission_bps = commission_bps
        self.slippage = slippage

    def transact(self, price: float, order: Order) -> float:
        """Return the executed price including slippage.

        Parameters
        ----------
        price : float
            Reference price (e.g., next open).
        order : Order
            The order to execute.

        Returns
        -------
        float
            Executed price.
        """
        if order.side == 'buy':
            return price + self.slippage
        else:
            return price - self.slippage

    def commission(self, executed_price: float, qty: int) -> float:
        # Compute commission in cash units (currency).
        notional = executed_price * qty
        return notional * self.commission_bps
