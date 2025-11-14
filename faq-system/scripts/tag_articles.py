#!/usr/bin/env python3
"""
Tag Internal Articles by Category
Creates tags for FAQ categories and applies them to internal articles in Intercom.
"""

import json
import os
import requests
import time
from typing import Dict, List, Optional
from collections import defaultdict

# Configuration
INTERCOM_ACCESS_TOKEN = os.environ.get("INTERCOM_ACCESS_TOKEN")
INTERCOM_API_BASE = "https://api.intercom.io"
RATE_LIMIT_DELAY = 0.5  # seconds between requests

# Category to tag name mapping
CATEGORY_TAGS = {
    "Exclusions": "exclusions",
    "Claims Requirements": "claims-requirements",
    "Eligibility": "eligibility",
    "Endorsements & Modifications": "endorsements",
    "Policy Definitions": "definitions",
    "Coverage Limits": "coverage-limits",
    "Common Questions": "common-questions",
    "Comparisons": "comparisons"
}


class IntercomTagger:
    def __init__(self, dry_run: bool = True):
        self.headers = {
            "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Intercom-Version": "Unstable"
        }
        self.dry_run = dry_run
        self.existing_tags = {}

    def fetch_all_tags(self) -> List[Dict]:
        """Fetch all existing tags from Intercom."""
        print("Fetching existing tags from Intercom...")

        response = requests.get(
            f"{INTERCOM_API_BASE}/tags",
            headers=self.headers
        )

        time.sleep(RATE_LIMIT_DELAY)

        if response.status_code == 200:
            data = response.json()
            tags = data.get("data", [])
            print(f"  Found {len(tags)} existing tags")

            # Store tags by name for quick lookup
            for tag in tags:
                self.existing_tags[tag.get("name")] = tag.get("id")

            return tags
        else:
            print(f"Error fetching tags: {response.status_code} - {response.text}")
            return []

    def create_tag(self, tag_name: str) -> Optional[str]:
        """Create a new tag in Intercom."""

        # Check if tag already exists
        if tag_name in self.existing_tags:
            print(f"  Tag '{tag_name}' already exists (ID: {self.existing_tags[tag_name]})")
            return self.existing_tags[tag_name]

        payload = {
            "name": tag_name
        }

        if self.dry_run:
            print(f"  [DRY RUN] Would create tag: {tag_name}")
            return f"dry_run_{tag_name}"

        response = requests.post(
            f"{INTERCOM_API_BASE}/tags",
            headers=self.headers,
            json=payload
        )

        time.sleep(RATE_LIMIT_DELAY)

        if response.status_code in [200, 201]:
            tag = response.json()
            tag_id = tag.get("id")
            self.existing_tags[tag_name] = tag_id
            print(f"  ✓ Created tag: {tag_name} (ID: {tag_id})")
            return tag_id
        else:
            print(f"  ✗ Error creating tag '{tag_name}': {response.status_code}")
            print(f"    Response: {response.text[:200]}")
            return None

    def create_all_category_tags(self):
        """Create tags for all FAQ categories."""
        print("\nCreating category tags...")
        print("-" * 70)

        created_tags = {}

        for category, tag_name in CATEGORY_TAGS.items():
            tag_id = self.create_tag(tag_name)
            if tag_id:
                created_tags[category] = tag_id

        print()
        return created_tags

    def fetch_all_internal_articles(self) -> List[Dict]:
        """Fetch all internal articles from Intercom."""
        print("Fetching all internal articles...")

        articles = []
        page = 1
        per_page = 50

        while True:
            response = requests.get(
                f"{INTERCOM_API_BASE}/internal_articles",
                headers=self.headers,
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

                if len(batch) < per_page:
                    break
            else:
                print(f"Error fetching articles: {response.status_code} - {response.text}")
                break

        return articles

    def tag_article(self, article_id: int, tag_name: str) -> bool:
        """Tag an internal article."""

        if self.dry_run:
            return True

        # Intercom uses tag endpoints to tag articles
        payload = {
            "name": tag_name
        }

        response = requests.post(
            f"{INTERCOM_API_BASE}/internal_articles/{article_id}/tags",
            headers=self.headers,
            json=payload
        )

        time.sleep(RATE_LIMIT_DELAY)

        if response.status_code in [200, 201]:
            return True
        else:
            print(f"\n  Error tagging article {article_id}: {response.status_code}")
            print(f"  Response: {response.text[:300]}")
            return False

    def categorize_articles_by_title(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize articles based on their titles."""
        categorized = defaultdict(list)

        # Keywords to identify categories
        category_keywords = {
            "Exclusions": ["exclude", "exclusion", "not covered", "does not cover"],
            "Claims Requirements": ["claim", "claims"],
            "Eligibility": ["eligibility", "eligible", "qualify", "requirement"],
            "Endorsements & Modifications": ["endorsement", "modification", "add-on", "optional"],
            "Policy Definitions": ["definition", "mean", "meaning", "defined"],
            "Coverage Limits": ["coverage limit", "maximum", "limit", "up to"],
            "Common Questions": ["common question", "faq", "frequently asked"],
            "Comparisons": ["comparison", "compare", "versus", "vs", "difference between"]
        }

        for article in articles:
            title = article.get("title", "").lower()
            body = (article.get("body", "") or "").lower()

            # Try to categorize based on title/body content
            matched = False
            for category, keywords in category_keywords.items():
                if any(keyword in title or keyword in body for keyword in keywords):
                    categorized[category].append(article)
                    matched = True
                    break

            if not matched:
                categorized["Unknown"].append(article)

        return dict(categorized)

    def tag_all_articles(self, articles: List[Dict], category_tags: Dict[str, str]):
        """Tag all articles based on their categories."""

        print("\nCategorizing articles...")
        categorized = self.categorize_articles_by_title(articles)

        print("\nArticles by category:")
        for category, arts in categorized.items():
            print(f"  {category}: {len(arts)} articles")
        print()

        if not self.dry_run:
            confirm = input(f"Tag {len(articles)} articles? (yes/no): ").strip().lower()
            if confirm not in ["yes", "y"]:
                print("Cancelled.")
                return
            print()

        print("Tagging articles...")
        print("-" * 70)

        success_count = 0
        failed_count = 0
        total = sum(len(arts) for arts in categorized.values())

        idx = 0
        for category, arts in categorized.items():
            if category == "Unknown":
                print(f"\nSkipping {len(arts)} uncategorized articles")
                continue

            tag_name = CATEGORY_TAGS.get(category)
            if not tag_name:
                print(f"\nWarning: No tag defined for category '{category}'")
                continue

            print(f"\nTagging {len(arts)} articles with '{tag_name}'...")

            for article in arts:
                idx += 1
                article_id = article.get("id")
                title = article.get("title", "Unknown")[:50]

                print(f"  [{idx}/{total}] {title}...", end=" ", flush=True)

                if self.dry_run:
                    print("✓ (DRY RUN)")
                    success_count += 1
                else:
                    if self.tag_article(article_id, tag_name):
                        print("✓")
                        success_count += 1
                    else:
                        print("✗")
                        failed_count += 1

        print()
        print("=" * 70)
        print("Tagging Summary")
        print("=" * 70)
        print(f"Articles tagged: {success_count}")
        print(f"Failed: {failed_count}")

        if self.dry_run:
            print()
            print("⚠️  This was a DRY RUN - no tags were actually applied.")
            print("To actually tag articles, run with --live flag")


def main():
    """Main process."""
    import sys

    if not INTERCOM_ACCESS_TOKEN:
        print("Error: INTERCOM_ACCESS_TOKEN not set")
        return

    dry_run = "--live" not in sys.argv

    print("=" * 70)
    print("Intercom Article Tagging")
    print("=" * 70)
    print()

    # Initialize tagger
    tagger = IntercomTagger(dry_run=dry_run)

    # Fetch existing tags
    tagger.fetch_all_tags()

    # Create category tags
    category_tags = tagger.create_all_category_tags()

    # Fetch articles
    articles = tagger.fetch_all_internal_articles()

    if not articles:
        print("No internal articles found.")
        return

    print()

    # Tag articles
    tagger.tag_all_articles(articles, category_tags)


if __name__ == "__main__":
    import sys

    if "--help" in sys.argv:
        print("Intercom Article Tagging Tool")
        print()
        print("Usage: python tag_articles.py [OPTIONS]")
        print()
        print("Options:")
        print("  --live    Actually create tags and tag articles (default is dry-run)")
        print("  --help    Show this help message")
        print()
        print("Examples:")
        print("  python tag_articles.py")
        print("    (Dry run - shows what would be tagged)")
        print()
        print("  python tag_articles.py --live")
        print("    (Actually create tags and tag articles)")
    else:
        main()
