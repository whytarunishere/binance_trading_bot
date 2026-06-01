"""Order orchestration layer.

This module defines a small `OrderRequest` DTO and an `OrderService`
that delegates to the HTTP client. It keeps business-level wiring
separate from transport details.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .client import BinanceFuturesTestnetClient, OrderResponse


@dataclass(slots=True)
class OrderRequest:
    # Simple container for order parameters validated by the CLI
    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Decimal | None = None


class OrderService:
    """Thin service exposing order operations used by the CLI.

    We keep service methods small so they are easy to extend (preflight
    checks, risk controls, etc.) without touching the client plumbing.
    """

    def __init__(self, client: BinanceFuturesTestnetClient) -> None:
        self.client = client

    def place_order(self, order: OrderRequest) -> OrderResponse:
        # Delegate to the client; future hooks (balance checks) belong here
        return self.client.place_order(
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            price=order.price,
        )
