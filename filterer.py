#!/usr/bin/env python3
"""Filtering helper: determine if a job matches the configured criteria."""
import re
import os
import logging
from typing import Any, Dict, Optional

from config import KEYWORDS, SKILLS, EXPERIENCE_MIN, EXPERIENCE_MAX

# Debug flag to log evaluation details for troubleshooting
DEBUG_FILTERS = os.getenv("DEBUG_FILTERS", "0").strip() in ("1", "true", "yes")


def _normalize_text(text: Any) -> str:
    if text is None:
        return ""
    return str(text).lower()


def _extract_experience(desc: str) -> Optional[int]:
    if not desc:
        return None
    # Look for patterns like '2 years', '1 year', '3+ years', etc.
    m = re.search(r"(\d+)\s*(?:\+)?\s*(?:years|year|yrs|yr)", desc, flags=re.IGNORECASE)
    if m:
        try:
            val = int(m.group(1))
            return val
        except ValueError:
            return None
    return None


def _text_for_search(job: Dict[str, Any]) -> str:
    parts = []
    title = job.get("position") or job.get("title") or job.get("role") or ""
    parts.append(str(title))
    desc = job.get("description") or ""
    if isinstance(desc, str):
        # Some descriptions are HTML; strip simple tags could be heavy; just include raw
        parts.append(desc)
    tags = job.get("tags") or []
    if isinstance(tags, list):
        parts.extend([str(t) for t in tags])
    return " ".join(parts)


def job_matches(job: Dict[str, Any]) -> bool:
    text = _text_for_search(job)
    # Keyword (role) match
    lowered = text.lower()
    keyword_match = any(kw.lower() in lowered for kw in KEYWORDS)
    if not keyword_match:
        if DEBUG_FILTERS:
            logging.info("Job ID %s rejected by keyword: %s (text=%s)", job.get("id"), KEYWORDS, text)
        return False

    # Experience filter (best-effort): require within range if explicit
    desc = job.get("description") or ""
    exp = _extract_experience(desc)
    if exp is not None:
        if exp < EXPERIENCE_MIN or exp > EXPERIENCE_MAX:
            if DEBUG_FILTERS:
                logging.info("Job ID %s rejected by experience: %s years (range %d-%d)", job.get("id"), exp, EXPERIENCE_MIN, EXPERIENCE_MAX)
            return False

    # Skill match: require at least one configured skill to appear somewhere in title/desc/tags
    skill_match = False
    for skill in SKILLS:
        if skill.lower() in lowered:
            skill_match = True
            break
    if not skill_match:
        # Check raw description and tags as fallback
        tags = job.get("tags") or []
        for t in tags:
            if str(t).lower() in lowered:
                skill_match = True
                break
    if not skill_match:
        if DEBUG_FILTERS:
            logging.info("Job ID %s rejected by skills: %s (needs one of %s)", job.get("id"), lowered, SKILLS)
        return False

    return True
