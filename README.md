# Job Alert Bot

Production-quality Python script set that monitors RemoteOK for frontend/React roles, filters by experience and skills, and sends Telegram notifications for new matches.

What you need to provide:
- BOT_TOKEN and CHAT_ID in config.py
- Ensure Python 3.8+ and network access

How it works:
- Scrapes RemoteOK API for job postings
- Filters by role keywords, experience range, and skill match
- Sends formatted Telegram messages with title, company, and link
- Persists seen job IDs to seen_jobs.json to avoid duplicates across restarts

Run: python main.py

Startup notification
- When the bot starts, it will attempt to send a startup heartbeat message to Telegram indicating the bot is running.

Environment-based configuration
- To set tokens securely, export environment variables before running:
- Windows PowerShell:
  $env:TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
  $env:TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
- Command Prompt (cmd):
  set TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
  set TELEGRAM_CHAT_ID=YOUR_CHAT_ID
- Then run: python main.py

You can also verify the environment variables with:
- python env_check.py
