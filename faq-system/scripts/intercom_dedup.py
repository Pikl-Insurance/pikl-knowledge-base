#!/usr/bin/env python3
"""
Intercom De-duplication Tool
Identifies and removes duplicate articles from Intercom based on article titles.
"""

import json
import os
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

# Configuration
INTERCOM_ACCESS_TOKEN = os.environ.get("INTERCOM_ACCESS_TOKEN")
INTERCOM_API_BASE = "https://api.intercom.io"
RATE_LIMIT_DELAY = 0.5  # seconds between requests

# Backup file for deleted articles
BACKUP_FILE = Path(__file__).parent.parent / "data" / "deleted_duplicates_backup.json"


class IntercomDeduplicator:
    def __init__(self, dry_run: bool = True):
        self.headers = {
            "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Intercom-Version": "2.10"
        }
        self.unstable_headers = {
            **self.headers,
            "Intercom-Version": "Unstable"
        }
        self.dry_run = dry_run
        self.deleted_articles = []

    def fetch_all_articles(self) -> List[Dict]:
        """Fetch all articles from Intercom (regular articles)."""
        print("Fetching all regular articles from Intercom...")

        articles = []
        page = 1
        per_page = 50

        while True:
            response = requests.get(
                f"{INTERCOM_API_BASE}/articles",
                headers=self.headers,
                params={"page": page, "per_page": per_page}
            )

            time.sleep(RATE_LIMIT_DELAY)

            if response.status_code == 200:
                data = response.json()
                batch = data.get("data", [])

                if not batch:
                    break

                # Tag articles as regular articles
                for article in batch:
                    article["_is_internal"] = False

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

    def fetch_all_internal_articles(self) -> List[Dict]:
        """Fetch all internal articles from Intercom."""
        print("Fetching all internal articles from Intercom...")

        articles = []
        page = 1
        per_page = 50

        while True:
            response = requests.get(
                f"{INTERCOM_API_BASE}/internal_articles",
                headers=self.unstable_headers,
                params={"page": page, "per_page": per_page}
            )

            time.sleep(RATE_LIMIT_DELAY)

            if response.status_code == 200:
                data = response.json()
                batch = data.get("data", [])

                if not batch:
                    break

                # Tag articles as internal articles
                for article in batch:
                    article["_is_internal"] = True

                articles.extend(batch)
                print(f"  Fetched page {page}: {len(batch)} internal articles (total: {len(articles)})")
                page += 1

                # Check if there are more pages
                if len(batch) < per_page:
                    break
            else:
                print(f"Error fetching internal articles: {response.status_code} - {response.text}")
                break

        return articles

    def identify_duplicates(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Group articles by title to identify duplicates."""
        print("\nAnalyzing articles for duplicates...")

        grouped = defaultdict(list)

        for article in articles:
            title = article.get("title", "").strip()
            if title:
                grouped[title].append(article)

        # Filter to only duplicates (more than 1 article with same title)
        duplicates = {title: arts for title, arts in grouped.items() if len(arts) > 1}

        return duplicates

    def delete_article(self, article_id: str, is_internal: bool = False) -> bool:
        """Delete an article from Intercom."""
        endpoint = f"{INTERCOM_API_BASE}/{'internal_articles' if is_internal else 'articles'}/{article_id}"
        headers = self.unstable_headers if is_internal else self.headers

        response = requests.delete(endpoint, headers=headers)
        time.sleep(RATE_LIMIT_DELAY)

        if response.status_code in [200, 204]:
            return True
        else:
            print(f"\n  Error deleting article {article_id}: {response.status_code} - {response.text[:200]}")
            return False

    def deduplicate(self, duplicates: Dict[str, List[Dict]], keep_strategy: str = "newest"):
        """
        Remove duplicate articles.

        keep_strategy:
        - "newest": Keep the most recently updated article
        - "oldest": Keep the oldest article
        - "first": Keep the first article in the list
        """
        print("\nDe-duplication Strategy:")
        print(f"  Keep: {keep_strategy}")
        print(f"  Mode: {'DRY RUN (no deletions)' if self.dry_run else 'LIVE (will delete!)'}")
        print()

        total_duplicates = sum(len(arts) - 1 for arts in duplicates.values())
        print(f"Found {len(duplicates)} duplicate titles with {total_duplicates} articles to remove")
        print()

        if not self.dry_run:
            confirm = input("⚠️  This will PERMANENTLY DELETE articles. Continue? (yes/no): ").strip().lower()
            if confirm not in ["yes", "y"]:
                print("Cancelled.")
                return
            print()

        deleted_count = 0
        failed_count = 0

        for title, articles in duplicates.items():
            # Sort articles based on strategy
            if keep_strategy == "newest":
                # Sort by updated_at descending
                articles_sorted = sorted(
                    articles,
                    key=lambda x: x.get("updated_at", 0),
                    reverse=True
                )
            elif keep_strategy == "oldest":
                # Sort by created_at ascending
                articles_sorted = sorted(
                    articles,
                    key=lambda x: x.get("created_at", 0)
                )
            else:  # first
                articles_sorted = articles

            # Keep the first one, delete the rest
            keep_article = articles_sorted[0]
            to_delete = articles_sorted[1:]

            print(f"Title: {title[:70]}")
            print(f"  Found {len(articles)} copies")
            print(f"  Keeping: ID {keep_article.get('id')} (created: {keep_article.get('created_at', 'unknown')})")

            for article in to_delete:
                article_id = article.get("id")
                is_internal = article.get("_is_internal", False)
                article_type = "internal_article" if is_internal else "article"

                print(f"  Deleting: ID {article_id} ({'internal' if is_internal else 'regular'}) (created: {article.get('created_at', 'unknown')})...", end=" ")

                if self.dry_run:
                    print("✓ (DRY RUN)")
                    deleted_count += 1
                    self.deleted_articles.append({
                        "id": article_id,
                        "title": title,
                        "type": article_type,
                        "created_at": article.get("created_at"),
                        "updated_at": article.get("updated_at")
                    })
                else:
                    if self.delete_article(article_id, is_internal):
                        print("✓")
                        deleted_count += 1
                        self.deleted_articles.append({
                            "id": article_id,
                            "title": title,
                            "type": article_type,
                            "created_at": article.get("created_at"),
                            "updated_at": article.get("updated_at")
                        })
                    else:
                        print("✗")
                        failed_count += 1

            print()

        # Save backup
        self.save_backup()

        print("=" * 70)
        print("De-duplication Summary")
        print("=" * 70)
        print(f"Total duplicate titles: {len(duplicates)}")
        print(f"Articles removed: {deleted_count}")
        print(f"Failed deletions: {failed_count}")
        print(f"Backup saved to: {BACKUP_FILE}")

        if self.dry_run:
            print()
            print("⚠️  This was a DRY RUN - no articles were actually deleted.")
            print("To actually delete duplicates, run with --live flag")

    def save_backup(self):
        """Save backup of deleted articles."""
        BACKUP_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(BACKUP_FILE, "w") as f:
            json.dump({
                "deleted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "dry_run": self.dry_run,
                "articles": self.deleted_articles
            }, f, indent=2)


def main():
    """Main de-duplication process."""
    import sys

    if not INTERCOM_ACCESS_TOKEN:
        print("Error: INTERCOM_ACCESS_TOKEN not set")
        print("Please set it in your environment")
        return

    # Parse arguments
    dry_run = "--live" not in sys.argv
    keep_strategy = "newest"  # default

    if "--keep-oldest" in sys.argv:
        keep_strategy = "oldest"
    elif "--keep-first" in sys.argv:
        keep_strategy = "first"

    print("=" * 70)
    print("Intercom Article De-duplication Tool")
    print("=" * 70)
    print()

    # Initialize deduplicator
    dedup = IntercomDeduplicator(dry_run=dry_run)

    # Fetch all articles
    regular_articles = dedup.fetch_all_articles()
    internal_articles = dedup.fetch_all_internal_articles()

    all_articles = regular_articles + internal_articles

    print()
    print(f"Total articles found: {len(all_articles)}")
    print(f"  Regular articles: {len(regular_articles)}")
    print(f"  Internal articles: {len(internal_articles)}")
    print()

    # Identify duplicates
    duplicates = dedup.identify_duplicates(all_articles)

    if not duplicates:
        print("✓ No duplicates found! Your Intercom is clean.")
        return

    # Show duplicate summary
    print("=" * 70)
    print("Duplicate Articles Found")
    print("=" * 70)

    for title, articles in list(duplicates.items())[:10]:  # Show first 10
        print(f"\n'{title[:60]}'")
        print(f"  {len(articles)} copies")
        for art in articles:
            print(f"    - ID: {art.get('id')}, Created: {art.get('created_at', 'unknown')}")

    if len(duplicates) > 10:
        print(f"\n... and {len(duplicates) - 10} more duplicate titles")

    print()

    # Perform de-duplication
    dedup.deduplicate(duplicates, keep_strategy=keep_strategy)


if __name__ == "__main__":
    import sys

    if "--help" in sys.argv:
        print("Intercom De-duplication Tool")
        print()
        print("Usage: python intercom_dedup.py [OPTIONS]")
        print()
        print("Options:")
        print("  --live           Actually delete duplicates (default is dry-run)")
        print("  --keep-newest    Keep the most recently updated article (default)")
        print("  --keep-oldest    Keep the oldest article")
        print("  --keep-first     Keep the first article found")
        print("  --help           Show this help message")
        print()
        print("Examples:")
        print("  python intercom_dedup.py")
        print("    (Dry run - shows what would be deleted)")
        print()
        print("  python intercom_dedup.py --live")
        print("    (Actually delete duplicates, keeping newest)")
        print()
        print("  python intercom_dedup.py --live --keep-oldest")
        print("    (Delete duplicates, keeping oldest articles)")
    else:
        main()
