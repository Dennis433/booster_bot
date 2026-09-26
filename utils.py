# utils.py

import requests
from config import DEXSCREENER_API

def get_token_info(mint_address: str) -> dict:
    """Fetch token price, volume and market cap from DEX Screener"""
    try:
        response = requests.get(f"{DEXSCREENER_API}{mint_address}", timeout=10)
        data = response.json()

        if not data.get("pairs"):
            return None

        # Get the most liquid pair
        pair = data["pairs"][0]

        return {
            "name": pair.get("baseToken", {}).get("name", "Unknown"),
            "symbol": pair.get("baseToken", {}).get("symbol", "???"),
            "price": pair.get("priceUsd", "0"),
            "market_cap": pair.get("marketCap", 0),
            "volume_24h": pair.get("volume", {}).get("h24", 0),
            "liquidity": pair.get("liquidity", {}).get("usd", 0),
            "dex": pair.get("dexId", "Unknown"),
            "pair_address": pair.get("pairAddress", ""),
            "price_change": pair.get("priceChange", {}).get("h24", 0),
            "txns_24h": pair.get("txns", {}).get("h24", {}),
        }

    except Exception as e:
        return {"error": str(e)}


def format_number(num) -> str:
    """Format large numbers cleanly"""
    try:
        num = float(num)
        if num >= 1_000_000:
            return f"${num / 1_000_000:.2f}M"
        elif num >= 1_000:
            return f"${num / 1_000:.2f}K"
        else:
            return f"${num:.4f}"
    except:
        return "N/A"


def format_token_info(info: dict) -> str:
    """Format token info into a readable Telegram message"""
    if not info or "error" in info:
        return "❌ Could not fetch token data. Check the mint address."

    # Price change emoji
    change = float(info.get("price_change", 0))
    change_emoji = "📈" if change >= 0 else "📉"
    change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"

    # Buys and sells
    txns = info.get("txns_24h", {})
    buys = txns.get("buys", 0)
    sells = txns.get("sells", 0)

    return (
        f"🪙 *{info['name']}* (${info['symbol']})\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💵 Price: `${float(info['price']):.8f}`\n"
        f"📊 Market Cap: `{format_number(info['market_cap'])}`\n"
        f"📈 24h Volume: `{format_number(info['volume_24h'])}`\n"
        f"💧 Liquidity: `{format_number(info['liquidity'])}`\n"
        f"{change_emoji} 24h Change: `{change_str}`\n"
        f"🟢 Buys: `{buys}` | 🔴 Sells: `{sells}`\n"
        f"🏦 DEX: `{info['dex'].upper()}`\n"
    )