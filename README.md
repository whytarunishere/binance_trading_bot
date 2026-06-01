=======
# Binance Futures Testnet Trading Bot

A robust, modular Command Line Interface (CLI) application for placing Market and Limit orders on the Binance Futures Testnet (USDT-M).

This project was built with a strong emphasis on **Separation of Concerns (SoC)**, zero-dependency network communication, and clean error handling.

---

## 🏗️ Architecture & Engineering Decisions

### Zero-Dependency Networking

The API client is built entirely using Python's standard `urllib` and `hmac` libraries, demonstrating a deep understanding of HTTP request construction and payload signing without relying on heavy external wrappers.

### Strict Separation of Concerns

* **`client.py`**
  Handles raw network communication, timestamp syncing, and cryptographic signing.

* **`orders.py`**
  Acts as the orchestration layer between user inputs and the Binance API.

* **`validators.py`**
  Isolates strict business-logic validation (e.g., Decimal conversions, side/type checking).

* **`cli.py`**
  Manages the user experience, argument parsing, and human-readable output.

### Precision Data Types

Financial quantities and prices are handled using Python's `decimal.Decimal` to prevent floating-point precision issues.

---

## 📂 Project Structure

```text
trading_bot/
│
├── bot/
│   ├── __init__.py
│   ├── client.py         # Binance API wrapper & HMAC signing
│   ├── exceptions.py     # Custom application-level errors
│   ├── logging_config.py # Dual-handler structured logging
│   ├── orders.py         # Order orchestration layer
│   └── validators.py     # Input sanitation and validation
│
├── cli.py                # Command-line entry point
├── requirements.txt      # Project dependencies
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/whytarunishere/binance_trading_bot.git
cd binance_trading_bot
```

### 2. Create and Activate a Virtual Environment

#### Windows

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory of the project and add your Binance Futures Testnet API credentials:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

> **Important:** Generate these keys specifically from **Binance Futures Testnet**, not the live Binance dashboard.

---

## 🚀 How to Run

The bot validates all inputs strictly. Ensure your quantity satisfies the minimum notional requirement (typically greater than **$50**) for the trading pair.

### Example 1: Place a MARKET BUY Order

```bash
python trading_bot/cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.01
```

### Example 2: Place a LIMIT SELL Order

```bash
python trading_bot/cli.py \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.05 \
  --price 85000
```

### View All Available Commands

```bash
python trading_bot/cli.py --help
```

---

## 📝 Logging System

The application uses a **dual-logger setup** configured in `logging_config.py`.

### Console Logging

Users receive clean, readable success/failure summaries without stack traces or unnecessary noise.

### File Logging (`logs/trading_bot.log`)

Developers get detailed lifecycle logs, including:

* JSON request payloads
* Binance API responses
* Order execution details
* Validation and exception tracking

Sensitive information such as **API keys** and **signatures** are strictly excluded from logs.

---

## 💡 Assumptions & Notes

### Testnet Only

This client is hardcoded to use:

```text
https://testnet.binancefuture.com
```

### USDT-M Futures

The bot assumes trading on **USDT-Margined perpetual futures pairs**, such as:

* `BTCUSDT`
* `ETHUSDT`

## 🔒 Security Best Practices

Before pushing your repository to GitHub:

### 1. Add `.env` to `.gitignore`

Never commit API credentials to a public repository.

Example:

```gitignore
.env
```

### 2. Include Required Log Files

If the assignment/prompt explicitly requests logs, ensure:

```text
logs/trading_bot.log
```

contains successful **Market** and **Limit order traces**.

---


>>>>>>> cd12f9f131cb9c8e6d6cabecf40086106ccd18a8
