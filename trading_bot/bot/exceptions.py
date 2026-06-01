"""Custom exceptions for the trading bot.

Keep small, explicit exception types so callers can distinguish
validation, API-level, and transport errors.
"""


class TradingBotError(Exception):
    """Base exception for application-level errors."""


class ValidationError(TradingBotError):
    """Raised when CLI or order input is invalid.

    Used by the validators module to signal user input problems.
    """


class BinanceAPIError(TradingBotError):
    """Raised when Binance returns an error response.

    Represents an API-level rejection (HTTP 4xx/5xx with an error body).
    """


class BinanceRequestError(TradingBotError):
    """Raised when the HTTP request fails before a response is received.

    Represents network/transport issues such as DNS, timeouts, or missing creds.
    """
