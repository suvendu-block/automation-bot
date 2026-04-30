#!/usr/bin/env python3
"""Telegram notifier: send job alerts via Telegram Bot API."""
import json
import urllib.request
import urllib.parse
from html import escape as html_escape
from typing import Optional

from config import BOT_TOKEN, CHAT_ID, DRY_RUN
import logging
import datetime
import urllib.parse


def _send_request(url: str, data: Optional[bytes] = None) -> dict:
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read()
        encoding = resp.headers.get_content_charset() or "utf-8"
        return json.loads(raw.decode(encoding))


def _escape_html_for_telegram(s: str) -> str:
    return html_escape(s)


def build_message_html(job: dict) -> str:
    # Try to surface title, company, and a clickable link
    title = str(job.get("position") or job.get("title") or "")
    company = str(_extract_company(job))
    url = job.get("url") or job.get("link") or ""
    title_h = _escape_html_for_telegram(title)
    company_h = _escape_html_for_telegram(company)
    url_h = _escape_html_for_telegram(url)
    # HTML-formatted message with a clickable link
    if url:
        return (
            f"Job: <b>{title_h}</b>\n"
            f"Company: <i>{company_h}</i>\n"
            f"Link: <a href=\"{url_h}\">Apply</a>"
        )
    else:
        return (
            f"Job: <b>{title_h}</b>\n"
            f"Company: <i>{company_h}</i>\n"
            f"Link: Not provided"
        )


def _extract_company(job: dict) -> str:
    # Different structures may expose company differently
    comp = job.get("company")
    if isinstance(comp, dict):
        return comp.get("name") or comp.get("markup") or ""
    if isinstance(comp, str):
        return comp
    # Fallbacks
    return job.get("company_name") or ""


def send_notification(job: dict) -> bool:
    """Send a notification for a single job. Returns True on success."""
    if not BOT_TOKEN or not CHAT_ID:
        return False
    text = build_message_html(job)
    # Telegram API: sendMessage with HTML parse mode
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    try:
        response = _send_request(url, data=data)
        return response.get("ok", False) is True
    except Exception:
        return False

def send_startup_notification() -> bool:
    """Notify via Telegram that the bot is starting up/running."""
    if DRY_RUN:
        logging.info("DRY_RUN: startup notification skipped")
        return True
    if not BOT_TOKEN or not CHAT_ID:
        return False
    text = (
        f"Job Alert Bot is running. Start time: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        # Plain text startup notice; avoid complex formatting for reliability
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    try:
        resp = _send_request(url, data=data)
        return resp.get("ok", False) is True
    except Exception:
        return False
