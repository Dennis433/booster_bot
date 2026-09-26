# booster.py

import asyncio
import random
from config import SOLANA_RPC, NUM_WALLETS, TRADE_AMOUNT, DELAY_BETWEEN_TRADES
from wallet import generate_wallets
from utils import get_token_info, format_number

async def simulate_boost(mint_address: str, update, num_wallets: int = NUM_WALLETS):
    """Simulate volume and market cap boosting"""

    await update.message.reply_text("🔄 Fetching token info...")

    # Get initial token info
    info = get_token_info(mint_address)
    if not info or "error" in info:
        await update.message.reply_text("❌ Invalid token address or not found on DEX Screener.")
        return

    await update.message.reply_text(
        f"🪙 Token: *{info['name']}* (${info['symbol']})\n"
        f"📊 Starting Market Cap: `{format_number(info['market_cap'])}`\n"
        f"📈 Starting Volume: `{format_number(info['volume_24h'])}`\n"
        f"⚙️ Generating {num_wallets} wallets...",
        parse_mode="Markdown"
    )

    # Generate wallets
    wallets = generate_wallets(num_wallets)
    await asyncio.sleep(1)

    await update.message.reply_text(f"✅ {num_wallets} wallets generated!\n🚀 Starting boost...")

    # Simulate trades
    total_volume = float(info['volume_24h'])
    simulated_price = float(info['price'])
    trade_log = []

    for i, wallet in enumerate(wallets):
        await asyncio.sleep(DELAY_BETWEEN_TRADES)

        # Simulate buy
        trade_amount = round(random.uniform(0.005, TRADE_AMOUNT), 4)
        price_change = round(random.uniform(0.001, 0.005), 6)
        simulated_price += price_change
        total_volume += trade_amount * simulated_price

        trade_log.append(
            f"✅ Wallet {i+1} | Buy `{trade_amount} SOL` @ `${simulated_price:.6f}`"
        )

        # Send update every 3 trades
        if (i + 1) % 3 == 0 or i == num_wallets - 1:
            progress = "\n".join(trade_log[-3:])
            await update.message.reply_text(
                f"📊 *Boost Progress*\n"
                f"━━━━━━━━━━━━━━━\n"
                f"{progress}\n\n"
                f"📈 Simulated Volume: `{format_number(total_volume)}`\n"
                f"💵 Simulated Price: `${simulated_price:.6f}`",
                parse_mode="Markdown"
            )

    # Final summary
    estimated_mcap = simulated_price * float(info['market_cap']) / float(info['price'])
    await update.message.reply_text(
        f"🏁 *Boost Complete!*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🪙 Token: *{info['name']}*\n"
        f"💵 Final Price: `${simulated_price:.6f}`\n"
        f"📈 Total Volume: `{format_number(total_volume)}`\n"
        f"📊 Est. Market Cap: `{format_number(estimated_mcap)}`\n"
        f"🔑 Wallets Used: `{num_wallets}`",
        parse_mode="Markdown"
    )