"""Validation helpers for order input.

This module centralises simple, deterministic validation rules for the CLI
and service layer (symbol format, side, order type, numeric parsing).
Raise `ValidationError` for recoverable user-facing errors.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from .exceptions import ValidationError

# Allowed values for discrete fields
VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def _to_decimal(value: str, field_name: str) -> Decimal:
    # Parse a user-provided numeric string to Decimal and enforce > 0.
    try:
        decimal_value = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a valid decimal number.") from exc

    if decimal_value <= 0:
        raise ValidationError(f"{field_name} must be greater than zero.")

    return decimal_value


def validate_symbol(symbol: str) -> str:
    # Normalize and perform minimal syntactic checks on trading pair
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValidationError("symbol is required.")
    if not normalized.endswith("USDT"):
        raise ValidationError("symbol must look like a USDT-M futures pair such as BTCUSDT.")
    return normalized


def validate_side(side: str) -> str:
    # Ensure the side is one of the allowed enumerations
    normalized = side.strip().upper()
    if normalized not in VALID_SIDES:
        raise ValidationError("side must be BUY or SELL.")
    return normalized


def validate_order_type(order_type: str) -> str:
    # Validate order type (MARKET/LIMIT)
    normalized = order_type.strip().upper()
    if normalized not in VALID_ORDER_TYPES:
        raise ValidationError("order type must be MARKET or LIMIT.")
    return normalized


def validate_quantity(quantity: str) -> Decimal:
    return _to_decimal(quantity, "quantity")


def validate_price(price: str | None, order_type: str) -> Decimal | None:
    if order_type == "LIMIT":
        if price is None or not str(price).strip():
            raise ValidationError("price is required for LIMIT orders.")
        return _to_decimal(str(price), "price")

    if price is None or not str(price).strip():
        return None

    return _to_decimal(str(price), "price")
