"""Binance Futures Testnet API client.

This module implements a small, synchronous HTTP client that signs and
submits order requests to the USDT-M Futures testnet. It intentionally
keeps behavior minimal to be easy to read and test.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from urllib import error, parse, request

from .exceptions import BinanceAPIError, BinanceRequestError


@dataclass(slots=True)
class OrderResponse:
    """Lightweight container for the important order fields returned by Binance.

    Fields mirror keys returned by the /fapi/v1/order create response.
    """
    order_id: int | None
    status: str | None
    executed_qty: str | None
    avg_price: str | None
    raw: dict[str, Any]


class BinanceFuturesTestnetClient:
    """Minimal Binance Futures client used by the CLI and OrderService.

    It reads API credentials from constructor args or the environment and
    exposes a single `place_order` method for MARKET and LIMIT orders.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str = "https://testnet.binancefuture.com",
        logger: logging.Logger | None = None,
    ) -> None:
        # Credentials may come from args or from environment variables (populated
        # by python-dotenv in the CLI). Missing credentials produce a request error.
        self.api_key = api_key or os.environ.get("BINANCE_API_KEY", "")
        self.api_secret = api_secret or os.environ.get("BINANCE_API_SECRET", "")
        self.base_url = base_url.rstrip("/")
        self.logger = logger or logging.getLogger("trading_bot")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Decimal | None = None,
        time_in_force: str = "GTC",
    ) -> OrderResponse:
        """Create and submit an order to the testnet.

        The method builds the signed query string, performs a POST request, and
        returns an OrderResponse. API and network errors are converted to
        domain exceptions so the CLI can handle them cleanly.
        """
        if not self.api_key or not self.api_secret:
            raise BinanceRequestError(
                "API credentials are required. Set BINANCE_API_KEY and BINANCE_API_SECRET."
            )

        # Build the canonical payload for the order create endpoint
        payload: dict[str, str] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": format(quantity, "f"),
            "timestamp": str(int(time.time() * 1000)),
            "newOrderRespType": "RESULT"
        }

        if order_type == "LIMIT":
            payload["price"] = format(price if price is not None else Decimal("0"), "f")
            payload["timeInForce"] = time_in_force

        body = self._encode_signed_payload(payload)
        endpoint = "/fapi/v1/order"
        url = f"{self.base_url}{endpoint}?{body}"
        # Log the outgoing request payload (timestamp removed for readability)
        self.logger.info("Submitting order request: %s", {k: v for k, v in payload.items() if k != "timestamp"})

        req = request.Request(url, method="POST")
        req.add_header("X-MBX-APIKEY", self.api_key)

        try:
            with request.urlopen(req, timeout=20) as response:
                raw_text = response.read().decode("utf-8")
                raw_json = json.loads(raw_text)
                self.logger.info("Order response received: %s", raw_json)
                return OrderResponse(
                    order_id=raw_json.get("orderId"),
                    status=raw_json.get("status"),
                    executed_qty=raw_json.get("executedQty"),
                    avg_price=raw_json.get("avgPrice"),
                    raw=raw_json,
                )
        except error.HTTPError as exc:
            # Read the error body and surface a sanitized message to the caller.
            error_text = exc.read().decode("utf-8", errors="replace")
            # Log API error details to the file (INFO) but avoid noisy console output.
            self.logger.info("Binance API error %s: %s", exc.code, error_text)
            raise BinanceAPIError(self._format_error_message(exc.code, error_text)) from exc
        except error.URLError as exc:
            # Record network failures in file-level logs.
            self.logger.info("Network failure during order submission: %s", exc)
            raise BinanceRequestError(f"Network failure during order submission: {exc}") from exc
        except json.JSONDecodeError as exc:
            self.logger.info("Unexpected non-JSON response from Binance.")
            raise BinanceAPIError("Unexpected non-JSON response from Binance.") from exc

    def _encode_signed_payload(self, payload: dict[str, str]) -> str:
        """URL-encode the payload and append HMAC-SHA256 signature required by Binance."""
        query_string = parse.urlencode(payload)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return f"{query_string}&signature={signature}"

    @staticmethod
    def _format_error_message(status_code: int, response_body: str) -> str:
        """Extract a human-friendly error message from Binance error responses."""
        try:
            parsed = json.loads(response_body)
            message = parsed.get("msg") or response_body
        except json.JSONDecodeError:
            message = response_body
        return f"Binance returned HTTP {status_code}: {message}"
