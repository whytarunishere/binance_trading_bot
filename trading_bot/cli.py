"""CLI entry point for Binance Futures Testnet orders.

The CLI is intentionally simple: parse args, load `.env`, validate input,
build an OrderRequest and call the OrderService. Errors are printed
concisely while detailed traces are sent to the log file.
"""

from __future__ import annotations

import argparse
from decimal import Decimal
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv

from bot.client import BinanceFuturesTestnetClient
from bot.exceptions import BinanceAPIError, BinanceRequestError, ValidationError
from bot.logging_config import configure_logging
from bot.orders import OrderRequest, OrderService
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place MARKET or LIMIT orders on Binance Futures Testnet.",
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, for example BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--type", dest="order_type", required=True, help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", help="Limit price, required for LIMIT orders")
    parser.add_argument(
        "--time-in-force",
        default="GTC",
        help="Time in force for LIMIT orders, default: GTC",
    )
    parser.add_argument(
        "--base-url",
        default="https://testnet.binancefuture.com",
        help="Binance Futures Testnet base URL",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Binance Futures Testnet API key. Defaults to BINANCE_API_KEY.",
    )
    parser.add_argument(
        "--api-secret",
        default=None,
        help="Binance Futures Testnet API secret. Defaults to BINANCE_API_SECRET.",
    )
    parser.add_argument(
        "--log-dir",
        default="logs",
        help="Directory where log files are stored.",
    )
    return parser


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logger = configure_logging(Path(args.log_dir))
    # Load credentials from .env (if present) into the environment
    load_dotenv()

    # Validate CLI inputs and fail fast with helpful messages
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)
        price = validate_price(args.price, order_type)
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        parser.error(str(exc))

    if order_type == "LIMIT" and price is None:
        parser.error("price is required for LIMIT orders.")

    order_request = OrderRequest(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
    )

    # Print a human friendly request summary before submission
    print("Order request summary")
    print(f"  Symbol: {order_request.symbol}")
    print(f"  Side: {order_request.side}")
    print(f"  Type: {order_request.order_type}")
    print(f"  Quantity: {order_request.quantity}")
    if order_request.price is not None:
        print(f"  Price: {order_request.price}")

    client = BinanceFuturesTestnetClient(
        api_key=args.api_key,
        api_secret=args.api_secret,
        base_url=args.base_url,
        logger=logger,
    )
    service = OrderService(client)

    # Place the order and handle expected API/network errors concisely.
    try:
        response = service.place_order(order_request)
    except (BinanceAPIError, BinanceRequestError) as exc:
        # Log details to file (INFO) and show a short failure line on console
        logger.info("Order placement failed: %s", exc)
        print(f"FAILED! : {exc}")
        return 1

    # Show the immediate response fields returned by Binance.
    print("\nOrder response details")
    print(f"  orderId: {response.order_id}")
    print(f"  status: {response.status}")
    print(f"  executedQty: {response.executed_qty}")
    print(f"  avgPrice: {response.avg_price}")
    print("SUCCESS! : order submitted to Binance Futures Testnet.")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
