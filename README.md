# Trading Bot — Binance Futures Testnet (USDT-M)

Small Python CLI app to place MARKET and LIMIT orders on Binance USDT-M Futures Testnet.

Quick summary
- CLI: parse/validate inputs, load `.env`, build an OrderRequest and submit to Binance testnet.
- Structure: small client layer, thin service/orchestration, validator helpers, and concise logging.

Repository layout

```
trading_bot/
  bot/
    __init__.py          # package marker
    client.py            # Binance HTTP client (signing + order create)
    exceptions.py        # small domain exceptions
    logging_config.py    # file + console logger configuration
    orders.py            # OrderRequest DTO and OrderService
    validators.py        # CLI input validation
  cli.py                 # CLI entrypoint and user-facing flow
README.md
requirements.txt
logs/                   # runtime logs (created automatically)
```

Prerequisites

- Python 3.10+ (project used 3.13 in development)
- A Binance Futures Testnet account: https://testnet.binancefuture.com
- API key + secret for the Testnet (keep them private)

Setup

1. From the repository root, activate your virtual environment and allow script execution:

```powershell
cd /d C:\Users\ACER\Desktop\primetrade
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
\.venv\Scripts\Activate.ps1
```

2. Create a `.env` file at the repository root containing:

```env
BINANCE_API_KEY=your_testnet_key
BINANCE_API_SECRET=your_testnet_secret
```

3. Install runtime dependencies:

```powershell
pip install -r requirements.txt
```

Running the CLI

Place a MARKET order:

```powershell
\.venv\Scripts\python.exe trading_bot\cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Place a LIMIT order:

```powershell
\.venv\Scripts\python.exe trading_bot\cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 120000
```

Notes on responses

- A `status: NEW` with `executedQty: 0.0000` means the order was accepted but has not been matched (no fills yet).
- MARKET orders typically execute immediately; if you see zero fills check margin, notional minimums, or testnet liquidity.

Logging

- Logs are written to `logs/trading_bot.log`.
- Console output is intentionally concise; full request/response JSON and stack traces are kept in the log file for debugging.

Quick tests and edge cases

Run these one at a time to exercise validation and error handling:

```powershell
# 1. CLI help
\.venv\Scripts\python.exe trading_bot\cli.py --help

# 2. Invalid symbol
\.venv\Scripts\python.exe trading_bot\cli.py --symbol '' --side BUY --type MARKET --quantity 0.001

# 3. Invalid side
\.venv\Scripts\python.exe trading_bot\cli.py --symbol BTCUSDT --side HOLD --type MARKET --quantity 0.001

# 4. Invalid order type
\.venv\Scripts\python.exe trading_bot\cli.py --symbol BTCUSDT --side BUY --type FOO --quantity 0.001

# 5. LIMIT missing price
\.venv\Scripts\python.exe trading_bot\cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001

# 6. Malformed quantity
\.venv\Scripts\python.exe trading_bot\cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity abc

# 7. Missing credentials (temporarily rename .env)
if (Test-Path .env) { Rename-Item .env .env.bak }
\.venv\Scripts\python.exe trading_bot\cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
if (Test-Path .env.bak) { Rename-Item .env.bak .env }

# 8. MARKET order (commonly returns margin errors on testnet if wallet empty)
\.venv\Scripts\python.exe trading_bot\cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# 9. MARKET small quantity (try to hit minimum notional)
\.venv\Scripts\python.exe trading_bot\cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.0001

# 10. LIMIT far away (will remain NEW)
\.venv\Scripts\python.exe trading_bot\cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 999999

# 11. LIMIT near market (may fill)
\.venv\Scripts\python.exe trading_bot\cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 20000

# 12. Simulate network failure
\.venv\Scripts\python.exe trading_bot\cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --base-url https://example.invalid

# 13. Inspect logs
Get-Content logs\trading_bot.log -Tail 200
```

Extending the project

- Add `check-order` (GET /fapi/v1/order) and a `--wait-for-fill` flag to poll for fills.
- Add preflight balance/notional checks to avoid obvious API rejections.

Assumptions

- This repo targets Binance Futures Testnet only.
- Keep your `.env` private — `.gitignore` already includes `.env`.

If you'd like, I can add `check-order` and `--wait-for-fill` in the next update.
