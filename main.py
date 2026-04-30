#!/usr/bin/env python3
"""Orchestrator for the job alert system."""
import time
import logging
from typing import List

from config import CHECK_INTERVAL_SECONDS, DRY_RUN
from sources import fetch_all_jobs
from storage import SeenStorage
from filterer import job_matches
from notifier import send_notification, send_startup_notification
from config import SEEN_FILE

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")


def process_jobs(seen: SeenStorage, jobs: List[dict]) -> int:
    """Process a batch of jobs: filter, notify for new matches, and mark seen."""
    notified = 0
    for job in jobs:
        job_id = job.get("id")
        if job_id is None:
            continue
        try:
            key = f"{job.get('source','unknown')}:{job_id}"
            if seen.is_seen(key):
                continue
            if not job_matches(job):
                continue
            ok = (send_notification(job) if not DRY_RUN else True)
            if ok:
                if not DRY_RUN:
                    seen.mark_seen(key)
                    notified += 1
                    logging.info("Notified about job ID %s (DRY_RUN=%s)", job_id, DRY_RUN)
            else:
                logging.warning("Failed to notify for job ID %s", job_id)
        except Exception:
            logging.exception("Error processing job ID %s", job_id)
    return notified


def main() -> None:
    seen = SeenStorage(SEEN_FILE)
    logging.info("Job alert bot started. Watching for new matches every %d seconds. DRY_RUN=%s", CHECK_INTERVAL_SECONDS, DRY_RUN)
    # Send startup heartbeat to Telegram (non-blocking, best-effort)
    try:
        if send_startup_notification():
            logging.info("Startup notification sent to Telegram.")
        else:
            logging.debug("Startup notification not sent (token/target not configured).")
    except Exception:
        logging.exception("Failed to send startup notification")
    while True:
        try:
            jobs = fetch_all_jobs()
            if not isinstance(jobs, list):
                logging.warning("Unexpected jobs data structure received; skipping this cycle.")
                jobs = []
            notified_count = process_jobs(seen, jobs)
            if notified_count:
                logging.info("Processed %d new job(s) in this cycle.", notified_count)
        except Exception:
            logging.exception("Unhandled error in main loop")
        finally:
            try:
                seen.save()
            except Exception:
                logging.exception("Failed to save seen jobs file")
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
