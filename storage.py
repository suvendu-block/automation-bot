#!/usr/bin/env python3
"""Seen storage for jobs to avoid duplicates across restarts."""
import json
import os
from typing import Set


class SeenStorage:
    def __init__(self, path: str):
        self.path = path
        self.seen: Set[str] = set()
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.path):
            self.seen = set()
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                ids = data.get("seen", []) if isinstance(data, dict) else []
                self.seen = set(str(i) for i in ids)
        except Exception:
            # If the file is corrupted, start fresh but log softly in caller
            self.seen = set()

    def is_seen(self, key: str) -> bool:
        return str(key) in self.seen

    def mark_seen(self, key: str) -> None:
        self.seen.add(str(key))

    def save(self) -> None:
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({"seen": list(self.seen)}, f, indent=2)
        except Exception:
            # Silently ignore storage write issues; we'll retry in next cycle
            pass
