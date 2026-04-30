#!/usr/bin/env python3
"""Scraping module: fetch job listings from remote sources (currently RemoteOK)."""
import json
import logging
import urllib.request
from typing import List, Dict, Any

from config import REMOTEOK_API, REQUEST_TIMEOUT, USER_AGENT


def _fetch_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        raw = resp.read()
        encoding = resp.headers.get_content_charset() or "utf-8"
        return json.loads(raw.decode(encoding))


def fetch_jobs() -> List[Dict[str, Any]]:
    """Fetch and normalize jobs from RemoteOK API.
    Returns a list of job dictionaries with commonly used fields.
    """
    data = _fetch_json(REMOTEOK_API)
    jobs: List[Dict[str, Any]] = []
    if not isinstance(data, list):
        return jobs
    for item in data:
        if not isinstance(item, dict):
            continue
        if not item.get("id"):
            continue
        # RemoteOK sometimes includes a header object; skip non-job items
        if not isinstance(item.get("id"), int):
            continue
        # Basic sanity: must have a title/position or similar
        title = (item.get("position") or item.get("title") or item.get("role"))
        if not title:
            continue
        jobs.append(item)
    logging.info("RemoteOK: fetched %d potential jobs", len(jobs))
    return jobs
