#!/usr/bin/env python3
"""Utility to check Telegram env vars without exposing tokens."""
import os

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "8686676143:AAEM_piD90rEQy0UOZhoPikrY3qQpDJdxYY")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "8251929942")
    print("BOT_TOKEN_SET:", bool(token))
    print("CHAT_ID_SET:", bool(chat_id))
    print("CHAT_ID_value:", chat_id if chat_id else "<not set>")

if __name__ == "__main__":
    main()
