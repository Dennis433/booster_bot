# wallet.py

from solders.keypair import Keypair
import base58

def generate_wallets(num: int) -> list:
    """Generate a list of fresh Solana wallets"""
    wallets = []
    for _ in range(num):
        keypair = Keypair()
        public_key = str(keypair.pubkey())
        private_key = base58.b58encode(bytes(keypair)).decode("utf-8")
        wallets.append({
            "public_key": public_key,
            "private_key": private_key,
            "keypair": keypair
        })
    return wallets


def display_wallets(wallets: list) -> str:
    """Format wallet list for Telegram display"""
    if not wallets:
        return "No wallets generated."

    msg = f"🔑 *Generated {len(wallets)} Wallets*\n"
    msg += "━━━━━━━━━━━━━━━\n"
    for i, w in enumerate(wallets, 1):
        msg += f"`Wallet {i}:` `{w['public_key']}`\n"
    return msg