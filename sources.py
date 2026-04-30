#!/usr/bin/env python3
"""Multi-source job fetchers: RemoteOK API and WeWorkRemotely RSS feed."""
import json
import urllib.request
import urllib.parse
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

from scraper import fetch_jobs as _fetch_remoteok

def fetch_remoteok_jobs() -> List[Dict[str, Any]]:
    jobs: List[Dict[str, Any]] = []
    try:
        items = _fetch_remoteok()
        for it in items:
            if not isinstance(it, dict):
                continue
            if not it.get("id"):
                continue
            j = {
                "id": it.get("id"),
                "title": it.get("position") or it.get("title"),
                "url": it.get("url"),
                "description": it.get("description") or "",
                "company": it.get("company") or "",
                "source": "remoteok",
            }
            jobs.append(j)
    except Exception:
        logging.exception("Failed to fetch RemoteOK jobs")
    return jobs

def _fetch_weworkremotely_rss(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "JobAlertBot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read()
        return ET.fromstring(raw)

def fetch_weworkremotely_jobs() -> List[Dict[str, Any]]:
    jobs: List[Dict[str, Any]] = []
    # Common RSS feed for programming jobs
    url = "https://weworkremotely.com/categories/remote-programming/jobs.rss"
    try:
        root = _fetch_weworkremotely_rss(url)
        for item in root.findall('./channel/item'):
            guid = item.findtext('guid')
            title = item.findtext('title')
            link = item.findtext('link')
            description = item.findtext('description') or ''
            if not title and not link:
                continue
            job = {
                "id": (guid or link or title),
                "title": title,
                "url": link,
                "description": description,
                "company": "We Work Remotely",
                "source": "weworkremotely",
            }
            jobs.append(job)
    except Exception:
        logging.exception("Failed to fetch We Work Remotely jobs")
    return jobs

def fetch_all_jobs() -> List[Dict[str, Any]]:
    remote = fetch_remoteok_jobs()
    wework = fetch_weworkremotely_jobs()
    remotive = fetch_remotive_jobs()
    all_jobs: List[Dict[str, Any]] = []
    all_jobs.extend(remote)
    all_jobs.extend(wework)
    all_jobs.extend(remotive)
    logging.info("Sources: %d RemoteOK + %d WeWorkRemotely + %d Remotive jobs", len(remote), len(wework), len(remotive))
    return all_jobs

def fetch_remotive_jobs() -> List[Dict[str, Any]]:
    """Fetch jobs from Remotive API (if available)."""
    jobs: List[Dict[str, Any]] = []
    url = "https://remotive.io/api/remote-jobs"
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read().decode())
        for item in data.get("jobs", []) if isinstance(data, dict) else []:
            j = {
                "id": item.get("id"),
                "title": item.get("title"),
                "url": item.get("url"),
                "description": item.get("description"),
                "company": item.get("company_name"),
                "source": "remotive",
            }
            if j["id"] is not None:
                jobs.append(j)
    except Exception:
        logging.exception("Failed to fetch Remotive jobs")
    return jobs
