#!/usr/bin/env python3
"""
Move Internal Articles to Folder
Moves all internal articles to a specified folder in Intercom.
"""

import json
import os
import requests
import time
from typing import Dict, List, Optional

# Configuration
INTERCOM_ACCESS_TOKEN = os.environ.get("INTERCOM_ACCESS_TOKEN")
INTERCOM_API_BASE = "https://api.intercom.io"
TARGET_FOLDER_ID = 2703344  # Internal FAQs folder
RATE_LIMIT_DELAY = 0.5  # seconds between requests


def fetch_all_internal_articles() -> List[Dict]:
    """Fetch all internal articles from Intercom."""
    headers = {
        "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Intercom-Version": "Unstable"
    }

    print("Fetching all internal articles...")
    articles = []
    page = 1
    per_page = 50

    while True:
        response = requests.get(
            f"{INTERCOM_API_BASE}/internal_articles",
            headers=headers,
            params={"page": page, "per_page": per_page}
        )

        time.sleep(RATE_LIMIT_DELAY)

        if response.status_code == 200:
            data = response.json()
            batch = data.get("data", [])

            if not batch:
                break

            articles.extend(batch)
            print(f"  Fetched page {page}: {len(batch)} articles (total: {len(articles)})")
            page += 1

            # Check if there are more pages
            if len(batch) < per_page:
                break
        else:
            print(f"Error fetching articles: {response.status_code} - {response.text}")
            break

    return articles


def update_article_folder(article: Dict, folder_id: int) -> bool:
    """Update an internal article's folder."""
    headers = {
        "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Intercom-Version": "Unstable"
    }

    article_id = article.get("id")

    # Include all required fields for internal article update
    payload = {
        "title": article.get("title"),
        "body": article.get("body"),
        "author_id": article.get("author_id"),
        "owner_id": article.get("owner_id"),
        "state": article.get("state", "published"),
        "folder_id": folder_id
    }

    # Add description if present
    if article.get("description"):
        payload["description"] = article.get("description")

    response = requests.put(
        f"{INTERCOM_API_BASE}/internal_articles/{article_id}",
        headers=headers,
        json=payload
    )

    time.sleep(RATE_LIMIT_DELAY)

    if response.status_code in [200, 201]:
        return True
    else:
        print(f"\n  Error updating article {article_id}: {response.status_code}")
        print(f"  Response: {response.text[:300]}")
        return False


def move_articles_to_folder(articles: List[Dict], folder_id: int, dry_run: bool = True):
    """Move articles to the specified folder."""

    print(f"\nTarget folder ID: {folder_id}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will move articles!)'}")
    print()

    # Filter articles that are not already in the target folder
    articles_to_move = []
    already_in_folder = []

    for article in articles:
        current_folder = article.get("folder_id")
        if current_folder == folder_id:
            already_in_folder.append(article)
        else:
            articles_to_move.append(article)

    print(f"Total articles: {len(articles)}")
    print(f"Already in target folder: {len(already_in_folder)}")
    print(f"Articles to move: {len(articles_to_move)}")
    print()

    if not articles_to_move:
        print("✓ All articles are already in the target folder!")
        return

    if not dry_run:
        confirm = input(f"Move {len(articles_to_move)} articles to folder {folder_id}? (yes/no): ").strip().lower()
        if confirm not in ["yes", "y"]:
            print("Cancelled.")
            return
        print()

    success_count = 0
    failed_count = 0

    print(f"Moving {len(articles_to_move)} articles...")
    print()

    for idx, article in enumerate(articles_to_move, 1):
        article_id = article.get("id")
        title = article.get("title", "Untitled")[:60]
        current_folder = article.get("folder_id", "None")

        print(f"[{idx}/{len(articles_to_move)}] {title}...", end=" ", flush=True)
        print(f"(folder: {current_folder} → {folder_id})...", end=" ", flush=True)

        if dry_run:
            print("✓ (DRY RUN)")
            success_count += 1
        else:
            if update_article_folder(article, folder_id):
                print("✓")
                success_count += 1
            else:
                print("✗")
                failed_count += 1

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Articles moved: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Already in folder: {len(already_in_folder)}")

    if dry_run:
        print()
        print("⚠️  This was a DRY RUN - no articles were actually moved.")
        print("To actually move articles, run with --live flag")


def main():
    """Main process."""
    import sys

    if not INTERCOM_ACCESS_TOKEN:
        print("Error: INTERCOM_ACCESS_TOKEN not set")
        return

    dry_run = "--live" not in sys.argv

    print("=" * 70)
    print("Move Internal Articles to Folder")
    print("=" * 70)
    print()

    # Fetch all internal articles
    articles = fetch_all_internal_articles()

    if not articles:
        print("No internal articles found.")
        return

    print()

    # Move articles
    move_articles_to_folder(articles, TARGET_FOLDER_ID, dry_run=dry_run)


if __name__ == "__main__":
    import sys

    if "--help" in sys.argv:
        print("Move Internal Articles to Folder")
        print()
        print("Usage: python move_to_folder.py [OPTIONS]")
        print()
        print("Options:")
        print("  --live    Actually move articles (default is dry-run)")
        print("  --help    Show this help message")
        print()
        print("Examples:")
        print("  python move_to_folder.py")
        print("    (Dry run - shows what would be moved)")
        print()
        print("  python move_to_folder.py --live")
        print("    (Actually move articles to folder)")
    else:
        main()
