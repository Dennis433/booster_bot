# config.py
import os

# Telegram Bot Token — set in Render environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

# Solana RPC endpoint
SOLANA_RPC = "https://api.mainnet-beta.solana.com"

# Payment wallet address — set in Render environment variables
PAYMENT_WALLET = os.environ.get("PAYMENT_WALLET", "")

# Boost settings
NUM_WALLETS = 10
TRADE_AMOUNT = 0.01
DELAY_BETWEEN_TRADES = 2

# DEX Screener API
DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/tokens/"
