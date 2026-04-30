#!/usr/bin/env python3
"""Configuration for the Job Alert Bot."""

# Telegram Bot configuration (read from environment for safety)
# The bot must have access to the target chat (private chat or channel).
import os
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8686676143:AAEM_piD90rEQy0UOZhoPikrY3qQpDJdxYY")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8251929942")  # as string to preserve sign

# Job criteria
KEYWORDS = ["Frontend Developer", "React Developer"]  # Roles to match (case-insensitive)
SKILLS = ["React", "JavaScript", "HTML", "CSS" , "nextjs"]  # Skills to look for in the listing
EXPERIENCE_MIN = 1  # years
EXPERIENCE_MAX = 3  # years



# Data storage
SEEN_FILE = "seen_jobs.json"  # Persist seen job IDs across restarts



# Scraping / runtime
REMOTEOK_API = "https://remoteok.com/api"
CHECK_INTERVAL_SECONDS = 600  # 10 minutes
USER_AGENT = "JobAlertBot/1.0 (+https://example.com)"



# Optional: throttle per-website requests if you add more sources
REQUEST_TIMEOUT = 20

# Dry-run mode: if set (non-empty and not '0'), the bot will skip actual Telegram sends
import os as _os
DRY_RUN = _os.getenv("DRY_RUN", "0").strip() not in ("", "0", "false", "no")
