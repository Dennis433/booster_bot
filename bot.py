# bot.py

import asyncio
import os
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters, ConversationHandler
)
from config import TELEGRAM_TOKEN, PAYMENT_WALLET
from utils import get_token_info, format_token_info
from booster import simulate_boost

# States
CHOOSING, GET_TOKEN, GET_WALLETS, GET_SPEED, CONFIRM_BOOST, AWAIT_PAYMENT = range(6)

# ── Volume Packages ───────────────────────────────────────
VOLUME_PACKAGES_SOL = {
    "vpkg_25k":   ("$25k",   "1.06 SOL",   10),
    "vpkg_50k":   ("$50k",   "1.61 SOL",   20),
    "vpkg_100k":  ("$100k",  "2.87 SOL",   30),
    "vpkg_200k":  ("$200k",  "5.36 SOL",   40),
    "vpkg_400k":  ("$400k",  "10.31 SOL",  60),
    "vpkg_800k":  ("$800k",  "19.96 SOL",  80),
    "vpkg_1_6m":  ("$1.6M",  "38.96 SOL",  100),
    "vpkg_3_2m":  ("$3.2M",  "73.89 SOL",  150),
    "vpkg_6_4m":  ("$6.4M",  "143.31 SOL", 200),
    "vpkg_12_8m": ("$12.8M", "277.28 SOL", 250),
}

VOLUME_PACKAGES_P4C = {
    "vpkg_25k_p4c":   ("$25k",   "0.265M P4C",  10),
    "vpkg_50k_p4c":   ("$50k",   "0.402M P4C",  20),
    "vpkg_100k_p4c":  ("$100k",  "0.717M P4C",  30),
    "vpkg_200k_p4c":  ("$200k",  "1.34M P4C",   40),
    "vpkg_400k_p4c":  ("$400k",  "2.57M P4C",   60),
    "vpkg_800k_p4c":  ("$800k",  "4.99M P4C",   80),
    "vpkg_1_6m_p4c":  ("$1.6M",  "9.74M P4C",   100),
    "vpkg_3_2m_p4c":  ("$3.2M",  "18.47M P4C",  150),
    "vpkg_6_4m_p4c":  ("$6.4M",  "35.82M P4C",  200),
    "vpkg_12_8m_p4c": ("$12.8M", "69.32M P4C",  250),
}

# ── MCap Packages ─────────────────────────────────────────
MCAP_PACKAGES = {
    "mpkg_1m":   ("1M MCap",   "49.9",  20),
    "mpkg_5m":   ("5M MCap",   "89.9",  40),
    "mpkg_10m":  ("10M MCap",  "131.9", 80),
    "mpkg_50m":  ("50M MCap",  "179.9", 120),
    "mpkg_100m": ("100M MCap", "229.9", 150),
}

MCAP_PACKAGES_P4C = {
    "mpkg_1m_p4c":   ("1M MCap",   "4.9M",  20),
    "mpkg_5m_p4c":   ("5M MCap",   "8.9M",  40),
    "mpkg_10m_p4c":  ("10M MCap",  "13.9M", 80),
    "mpkg_50m_p4c":  ("50M MCap",  "20.9M", 120),
    "mpkg_100m_p4c": ("100M MCap", "22.9M", 150),
}


# ── /start ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📈 Volume Boost", callback_data="volume"),
            InlineKeyboardButton("📊 MCap Boost", callback_data="mcap"),
        ],
        [
            InlineKeyboardButton("💰 My Balance", callback_data="balance"),
            InlineKeyboardButton("ℹ️ How It Works", callback_data="how"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⚡ *Welcome to G4S Bot!*\n\n"
        "🚀 The most powerful Solana volume & market cap booster.\n\n"
        "⭐ *Choose your boost:*\n"
        "• 📈 *Volume Boost* — Increase trading volume\n"
        "• 📊 *MCap Boost* — Push your chart upward\n\n"
        "⛓️ *Supported Chain:* Solana only\n"
        "💳 *Payment:* SOL & P4C token\n\n"
        "🔥 *Let's push your project into the trendings!*",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return CHOOSING


# ── Button Handler ───────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "how":
        await query.message.reply_text(
            "ℹ️ *How G4S Bot Works*\n\n"
            "1️⃣ Choose your boost type\n"
            "2️⃣ Select your budget package\n"
            "3️⃣ Choose your speed\n"
            "4️⃣ Enter your Solana token CA\n"
            "5️⃣ Send payment\n"
            "6️⃣ Click *I Have Sent Payment*\n"
            "7️⃣ Boost starts immediately\n\n"
            "📊 Track progress live in this chat!",
            parse_mode="Markdown"
        )
        return CHOOSING

    if data == "balance":
        await query.message.reply_text(
            "💰 *Your Balance*\n\n"
            "• SOL: `0.00 SOL`\n"
            "• P4C: `0.00 P4C`\n\n"
            "➕ Deposit SOL or P4C to get started.",
            parse_mode="Markdown"
        )
        return CHOOSING

    if data == "back":
        keyboard = [
            [
                InlineKeyboardButton("📈 Volume Boost", callback_data="volume"),
                InlineKeyboardButton("📊 MCap Boost", callback_data="mcap"),
            ],
            [
                InlineKeyboardButton("💰 My Balance", callback_data="balance"),
                InlineKeyboardButton("ℹ️ How It Works", callback_data="how"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "⚡ *Welcome to G4S Bot!*\n\n"
            "🚀 The most powerful Solana volume & market cap booster.\n\n"
            "⭐ *Choose your boost:*\n"
            "• 📈 *Volume Boost* — Increase trading volume\n"
            "• 📊 *MCap Boost* — Push your chart upward\n\n"
            "⛓️ *Supported Chain:* Solana only\n"
            "💳 *Payment:* SOL & P4C token\n\n"
            "🔥 *Let's push your project into the trendings!*",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return CHOOSING

    # ── Volume Boost Menu ──
    if data == "volume":
        context.user_data["boost_type"] = "volume"
        keyboard = [
            [
                InlineKeyboardButton("$25k | 1.06 SOL", callback_data="vpkg_25k"),
                InlineKeyboardButton("$25k | 0.265M P4C", callback_data="vpkg_25k_p4c"),
            ],
            [
                InlineKeyboardButton("$50k | 1.61 SOL", callback_data="vpkg_50k"),
                InlineKeyboardButton("$50k | 0.402M P4C", callback_data="vpkg_50k_p4c"),
            ],
            [
                InlineKeyboardButton("$100k | 2.87 SOL", callback_data="vpkg_100k"),
                InlineKeyboardButton("$100k | 0.717M P4C", callback_data="vpkg_100k_p4c"),
            ],
            [
                InlineKeyboardButton("$200k | 5.36 SOL", callback_data="vpkg_200k"),
                InlineKeyboardButton("$200k | 1.34M P4C", callback_data="vpkg_200k_p4c"),
            ],
            [
                InlineKeyboardButton("🎁 $400k | 10.31 SOL", callback_data="vpkg_400k"),
                InlineKeyboardButton("🎁 $400k | 2.57M P4C", callback_data="vpkg_400k_p4c"),
            ],
            [
                InlineKeyboardButton("🎁 $800k | 19.96 SOL", callback_data="vpkg_800k"),
                InlineKeyboardButton("🎁 $800k | 4.99M P4C", callback_data="vpkg_800k_p4c"),
            ],
            [
                InlineKeyboardButton("🎁 $1.6M | 38.96 SOL", callback_data="vpkg_1_6m"),
                InlineKeyboardButton("🎁 $1.6M | 9.74M P4C", callback_data="vpkg_1_6m_p4c"),
            ],
            [
                InlineKeyboardButton("🎁 $3.2M | 73.89 SOL", callback_data="vpkg_3_2m"),
                InlineKeyboardButton("🎁 $3.2M | 18.47M P4C", callback_data="vpkg_3_2m_p4c"),
            ],
            [
                InlineKeyboardButton("🎁 $6.4M | 143.31 SOL", callback_data="vpkg_6_4m"),
                InlineKeyboardButton("🎁 $6.4M | 35.82M P4C", callback_data="vpkg_6_4m_p4c"),
            ],
            [
                InlineKeyboardButton("🎁 $12.8M | 277.28 SOL", callback_data="vpkg_12_8m"),
                InlineKeyboardButton("🎁 $12.8M | 69.32M P4C", callback_data="vpkg_12_8m_p4c"),
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "⭐ *G4S Bot — Solana Volume Boost*\n\n"
            "🎁 *Bonus Included:*\n"
            "  + FREE Trending Ticket for packages $400k+\n\n"
            "🔥 *Important:*\n"
            "✅ ALL COSTS INCLUDED — NO HIDDEN FEES\n"
            "✅ Always adjusted to current SOL prices\n"
            "✅ Best price guarantee across all volume providers\n"
            "✅ Pause, resume or withdraw unused budget anytime\n\n"
            "⚙️ Calculations based on Raydium's 0.25% swap fee.\n"
            "_Results may vary depending on your pool setup._\n\n"
            "💰 *Select your package:*\n"
            "_Left = SOL | Right = P4C_",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return GET_WALLETS

    # ── MCap Boost Menu ──
    if data == "mcap":
        context.user_data["boost_type"] = "mcap"
        keyboard = [
            [
                InlineKeyboardButton("🚀 1M | 49.9 SOL", callback_data="mpkg_1m"),
                InlineKeyboardButton("🚀 1M | 4.9M P4C", callback_data="mpkg_1m_p4c"),
            ],
            [
                InlineKeyboardButton("🚀 5M | 89.9 SOL", callback_data="mpkg_5m"),
                InlineKeyboardButton("🚀 5M | 8.9M P4C", callback_data="mpkg_5m_p4c"),
            ],
            [
                InlineKeyboardButton("🚀 10M | 131.9 SOL", callback_data="mpkg_10m"),
                InlineKeyboardButton("🚀 10M | 13.9M P4C", callback_data="mpkg_10m_p4c"),
            ],
            [
                InlineKeyboardButton("🚀 50M | 179.9 SOL", callback_data="mpkg_50m"),
                InlineKeyboardButton("🚀 50M | 20.9M P4C", callback_data="mpkg_50m_p4c"),
            ],
            [
                InlineKeyboardButton("🚀 100M | 229.9 SOL", callback_data="mpkg_100m"),
                InlineKeyboardButton("🚀 100M | 22.9M P4C", callback_data="mpkg_100m_p4c"),
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "⭐ *G4S Bot — Solana MCap Boost*\n\n"
            "🔥 *Important:*\n"
            "✅ ALL COSTS INCLUDED — NO HIDDEN FEES\n"
            "✅ Always adjusted to current SOL prices\n"
            "✅ Best price guarantee across all MCap providers\n"
            "✅ Pause, resume or withdraw unused budget anytime\n\n"
            "⚙️ Calculations based on Raydium's 0.25% swap fee.\n"
            "_Results may vary depending on your pool setup._\n\n"
            "💰 *Select your MCap target:*\n"
            "_Left = SOL | Right = P4C_",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return GET_WALLETS

    # ── Volume SOL Package → Speed ──
    if data in VOLUME_PACKAGES_SOL:
        pkg = VOLUME_PACKAGES_SOL[data]
        context.user_data["package"] = pkg
        context.user_data["num_wallets"] = pkg[2]
        context.user_data["payment_method"] = "SOL"
        context.user_data["payment_amount"] = pkg[1]
        return await show_speed_menu(query, pkg)

    # ── Volume P4C Package → Speed ──
    if data in VOLUME_PACKAGES_P4C:
        pkg = VOLUME_PACKAGES_P4C[data]
        context.user_data["package"] = pkg
        context.user_data["num_wallets"] = pkg[2]
        context.user_data["payment_method"] = "P4C"
        context.user_data["payment_amount"] = pkg[1]
        return await show_speed_menu(query, pkg)

    # ── MCap SOL Package → CA ──
    if data in MCAP_PACKAGES:
        pkg = MCAP_PACKAGES[data]
        context.user_data["package"] = pkg
        context.user_data["num_wallets"] = pkg[2]
        context.user_data["payment_method"] = "SOL"
        context.user_data["payment_amount"] = f"{pkg[1]} SOL"
        await query.message.reply_text(
            f"✅ *MCap Target:* {pkg[0]}\n"
            f"💰 *Payment:* {pkg[1]} SOL\n\n"
            f"📋 Now enter your *Solana token CA*:\n\n"
            f"_Example: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v_",
            parse_mode="Markdown"
        )
        return GET_TOKEN

    # ── MCap P4C Package → CA ──
    if data in MCAP_PACKAGES_P4C:
        pkg = MCAP_PACKAGES_P4C[data]
        context.user_data["package"] = pkg
        context.user_data["num_wallets"] = pkg[2]
        context.user_data["payment_method"] = "P4C"
        context.user_data["payment_amount"] = f"{pkg[1]} P4C"
        await query.message.reply_text(
            f"✅ *MCap Target:* {pkg[0]}\n"
            f"💰 *Payment:* {pkg[1]} P4C\n\n"
            f"📋 Now enter your *Solana token CA*:\n\n"
            f"_Example: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v_",
            parse_mode="Markdown"
        )
        return GET_TOKEN


# ── Show Speed Menu ──────────────────────────────────────
async def show_speed_menu(query, pkg):
    keyboard = [
        [InlineKeyboardButton("⚡ 1 hour (Turbo Mode)", callback_data="spd_1h")],
        [
            InlineKeyboardButton("3 hours", callback_data="spd_3h"),
            InlineKeyboardButton("6 hours", callback_data="spd_6h"),
        ],
        [
            InlineKeyboardButton("12 hours", callback_data="spd_12h"),
            InlineKeyboardButton("24 hours", callback_data="spd_24h"),
        ],
        [
            InlineKeyboardButton("3 days", callback_data="spd_3d"),
            InlineKeyboardButton("7 days", callback_data="spd_7d"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="volume")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(
        f"⚡ *Choose Your Speed*\n\n"
        f"✅ You have selected a volume of *{pkg[0]}*\n\n"
        f"➡️ Now choose how fast the volume should be\n"
        f"delivered to match your activity goals.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return GET_SPEED


# ── Speed Selected ───────────────────────────────────────
async def speed_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    speeds = {
        "spd_1h":  "⚡ 1 hour (Turbo Mode)",
        "spd_3h":  "3 hours",
        "spd_6h":  "6 hours",
        "spd_12h": "12 hours",
        "spd_24h": "24 hours",
        "spd_3d":  "3 days",
        "spd_7d":  "7 days",
    }

    if data == "volume":
        return await button_handler(update, context)

    speed_label = speeds.get(data, "24 hours")
    context.user_data["speed"] = speed_label

    await query.message.reply_text(
        f"✅ *Speed Selected:* {speed_label}\n\n"
        f"📋 Now enter your *Solana token CA*:\n\n"
        f"_Example: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v_",
        parse_mode="Markdown"
    )
    return GET_TOKEN


# ── Token Address Input ──────────────────────────────────
async def get_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mint = update.message.text.strip()
    context.user_data["mint"] = mint
    boost_type = context.user_data.get("boost_type", "volume")
    num_wallets = context.user_data.get("num_wallets", 10)
    pkg = context.user_data.get("package", ("$25k", "1.06 SOL", 10))
    speed = context.user_data.get("speed", "")
    payment_amount = context.user_data.get("payment_amount", pkg[1])

    searching_msg = await update.message.reply_text(
        "🔍 *Searching for token...*",
        parse_mode="Markdown"
    )

    info = get_token_info(mint)

    if not info or "error" in info:
        await searching_msg.delete()
        await update.message.reply_text(
            "❌ *Token not found!*\n\n"
            "Please check the CA and try again.\n"
            "_Make sure it's a valid Solana token address._",
            parse_mode="Markdown"
        )
        return GET_TOKEN

    await searching_msg.delete()

    boost_label = "📈 Volume Boost" if boost_type == "volume" else "📊 MCap Boost"
    speed_line = f"⚡ *Speed:* {speed}\n" if boost_type == "volume" and speed else ""

    keyboard = [
        [InlineKeyboardButton("✅ Confirm Boost", callback_data="confirm")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"✅ *Token Found!*\n\n"
        f"{format_token_info(info)}"
        f"━━━━━━━━━━━━━━━\n"
        f"⚡ *Boost Type:* {boost_label}\n"
        f"💰 *Package:* {pkg[0]} | {payment_amount}\n"
        f"{speed_line}"
        f"🔑 *Wallets:* {num_wallets}\n\n"
        f"✅ *Confirm to proceed to payment?*",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return CONFIRM_BOOST


# ── Confirm → Show Payment Details ───────────────────────
async def confirm_boost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "cancel":
        await query.message.reply_text(
            "❌ Boost cancelled. Use /start to begin again."
        )
        return CHOOSING

    pkg = context.user_data.get("package", ("$25k", "1.06 SOL", 10))
    payment_method = context.user_data.get("payment_method", "SOL")
    payment_amount = context.user_data.get("payment_amount", pkg[1])
    speed = context.user_data.get("speed", "")
    boost_type = context.user_data.get("boost_type", "volume")
    speed_line = f"⚡ *Speed:* {speed}\n" if boost_type == "volume" and speed else ""

    keyboard = [
        [InlineKeyboardButton("✅ I Have Sent Payment", callback_data="payment_sent")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        f"💳 *Payment Details*\n\n"
        f"💰 *Amount:* `{payment_amount}`\n"
        f"🏦 *Method:* {payment_method}\n"
        f"{speed_line}\n"
        f"📤 *Send to address below:*\n"
        f"👇 _Tap the address to copy_",
        parse_mode="Markdown"
    )

    await query.message.reply_text(
        f"`{PAYMENT_WALLET}`",
        parse_mode="Markdown"
    )

    await query.message.reply_text(
        f"━━━━━━━━━━━━━━━\n"
        f"⚠️ _Send exact amount to avoid delays_\n\n"
        f"✅ Once sent, click the button below:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return AWAIT_PAYMENT


# ── Payment Sent → Start Boost ───────────────────────────
async def payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "cancel_payment":
        await query.message.reply_text(
            "❌ Boost cancelled. Use /start to begin again."
        )
        return CHOOSING

    if data == "payment_sent":
        mint = context.user_data.get("mint")
        num_wallets = context.user_data.get("num_wallets", 10)
        pkg = context.user_data.get("package", ("$25k", "1.06 SOL", 10))
        payment_amount = context.user_data.get("payment_amount", pkg[1])
        payment_method = context.user_data.get("payment_method", "SOL")
        speed = context.user_data.get("speed", "")
        boost_type = context.user_data.get("boost_type", "volume")
        speed_line = f"⚡ *Speed:* {speed}\n" if boost_type == "volume" and speed else ""

        await query.message.reply_text(
            f"🎉 *Payment Confirmed — Boost Starting!*\n\n"
            f"💰 *Amount:* `{payment_amount}`\n"
            f"🏦 *Method:* {payment_method}\n"
            f"{speed_line}"
            f"🔑 *Wallets:* {num_wallets}\n\n"
            f"🚀 *Initializing boost engine...*",
            parse_mode="Markdown"
        )

        await simulate_boost(mint, query, num_wallets)
        return CHOOSING


# ── Cancel Command ───────────────────────────────────────
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Cancelled. Use /start to begin again."
    )
    return CHOOSING



# ── Health Check Server ──────────────────────────────────
async def health_check(request):
    return web.Response(text="OK")

async def run_health_server():
    server = web.Application()
    server.router.add_get("/", health_check)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"✅ Health server running on port {port}")


# ── Main ─────────────────────────────────────────────────
async def main():
    # Start dummy HTTP server so Render detects an open port
    await run_health_server()

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING:      [CallbackQueryHandler(button_handler)],
            GET_WALLETS:   [
                CallbackQueryHandler(button_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_token)
            ],
            GET_SPEED:     [CallbackQueryHandler(speed_handler)],
            GET_TOKEN:     [MessageHandler(filters.TEXT & ~filters.COMMAND, get_token)],
            CONFIRM_BOOST: [CallbackQueryHandler(confirm_boost)],
            AWAIT_PAYMENT: [CallbackQueryHandler(payment_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("🚀 G4S Bot is running...")

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Run forever until interrupted
    await asyncio.Event().wait()

    # Graceful shutdown
    await app.updater.stop()
    await app.stop()
    await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
