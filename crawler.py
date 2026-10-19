import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone

import requests

from article_parser import parse_article

MANIFEST_FILE = "manifest.json"
ARTICLES_DIR = "data/articles"
REPORTS_DIR = "reports"

DELAY_SECONDS = 1        # polite pause between articles
MAX_RETRIES = 3          # tries per article inside one run
MAX_FAILED_RUNS = 3      # stop retrying an article after this many failed runs
MIN_BODY_CHARS = 100     # quality check: shorter articles are rejected
CHECKPOINT_EVERY = 10    # save progress after this many articles


def load_manifest():
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest):
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def parse_with_retries(url):
    """Returns (record, status, message). status is 'ok', 'gone' or 'failed'."""
    error = "unknown error"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return parse_article(url), "ok", None
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response is not None else None
            if code in (404, 410):
                return None, "gone", f"HTTP {code}"
            if code == 429 or (code is not None and code >= 500):
                error = f"HTTP {code}"          # temporary, so retry
            else:
                return None, "failed", f"HTTP {code}"   # permanent, no retry
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            error = type(e).__name__             # temporary, so retry
        except ValueError as e:
            return None, "failed", f"parse error: {e}"

        if attempt < MAX_RETRIES:
            wait = 2 ** attempt                  # exponential backoff: 2s, 4s
            print(f"      retrying in {wait}s ({error})")
            time.sleep(wait)

    return None, "failed", error


def quality_problem(record):
    """Return the reason an article is rejected, or None if it is fine."""
    if not record["title"]:
        return "no_title"
    if len(record["body_text"]) < MIN_BODY_CHARS:
        return "body_too_short"
    return None


def save_article(record):
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    path = os.path.join(ARTICLES_DIR, f"{record['article_id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)


def save_report(counts, failures, started, total_waiting):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report = {
        "started_at": started.isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "counts": dict(counts),
        "still_waiting_after_run": total_waiting,
        "failures": failures,
    }
    name = started.strftime("run_%Y%m%d_%H%M%S.json")
    with open(os.path.join(REPORTS_DIR, name), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return name


def main(limit):
    started = datetime.now(timezone.utc)
    manifest = load_manifest()

    # Only work that is not finished yet
    todo = [
        url for url, info in manifest.items()
        if info["status"] in ("new", "changed")
        or (info["status"] == "failed" and info["attempts"] < MAX_FAILED_RUNS)
    ]
    batch = todo[:limit]
    print(f"Waiting to process: {len(todo)} | This run: {len(batch)}\n")

    counts = Counter()
    failures = []

    try:
        for number, url in enumerate(batch, start=1):
            info = manifest[url]
            record, status, message = parse_with_retries(url)

            if status == "gone":
                info["status"] = "removed"
                info["last_error"] = message
                counts["removed"] += 1
                print(f"{number:3}/{len(batch)} REMOVED   {url[-50:]}")

            elif status == "failed":
                info["status"] = "failed"
                info["attempts"] += 1
                info["last_error"] = message
                counts["failed"] += 1
                failures.append({"url": url, "error": message})
                print(f"{number:3}/{len(batch)} FAILED    {url[-50:]} | {message}")

            else:
                problem = quality_problem(record)
                if problem:
                    info["status"] = "rejected"
                    info["last_error"] = problem
                    counts["rejected"] += 1
                    print(f"{number:3}/{len(batch)} REJECTED  {url[-50:]} | {problem}")
                else:
                    old_hash = info.get("content_hash")
                    if old_hash == record["content_hash"]:
                        outcome = "unchanged_content"   # no duplicate work
                    else:
                        save_article(record)
                        outcome = "added" if old_hash is None else "updated"
                    counts[outcome] += 1
                    info["content_hash"] = record["content_hash"]
                    info["status"] = "done"
                    info["attempts"] = 0
                    info["last_error"] = None
                    info["processed_at"] = datetime.now(timezone.utc).isoformat()
                    print(
                        f"{number:3}/{len(batch)} {outcome.upper():9} "
                        f"images={len(record['images'])}  {record['title'][:45]}"
                    )

            if number % CHECKPOINT_EVERY == 0:
                save_manifest(manifest)               # checkpoint

            time.sleep(DELAY_SECONDS)

    except KeyboardInterrupt:
        print("\nStopped by you (Ctrl+C). Saving progress...")

    finally:
        save_manifest(manifest)
        waiting = sum(
            1 for info in manifest.values()
            if info["status"] in ("new", "changed")
            or (info["status"] == "failed" and info["attempts"] < MAX_FAILED_RUNS)
        )
        report_name = save_report(counts, failures, started, waiting)
        print("\n--- Run summary ---")
        print(dict(counts))
        print("Still waiting:", waiting)
        print("Report saved:", f"reports/{report_name}")


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    main(limit)