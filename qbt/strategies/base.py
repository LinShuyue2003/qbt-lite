from __future__ import annotations

class Strategy:
    """Base class for strategies.

    Child classes should override 'on_bar'.
    """
    def __init__(self, params: dict | None = None):
        self.params = params or {}

    def on_bar(self, ctx) -> None:
        """Called each bar. Access data via 'ctx.data', portfolio via 'ctx.portfolio'.

        Use 'ctx.submit_order(symbol, qty, side)' to queue a market order that will be
        executed on the NEXT bar open.
        """
        raise NotImplementedError
