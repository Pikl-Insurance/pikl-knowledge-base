#!/usr/bin/env python3
"""
Intercom Full Import
Imports all FAQs to Intercom with proper collection structure.
"""

import json
import os
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
INTERCOM_ACCESS_TOKEN = os.environ.get("INTERCOM_ACCESS_TOKEN")
FAQ_DATA_FILE = Path(__file__).parent.parent / "data" / "internal_faqs.json"
PROGRESS_FILE = Path(__file__).parent.parent / "data" / "intercom_import_progress.json"
INTERCOM_API_BASE = "https://api.intercom.io"

# Rate limiting
RATE_LIMIT_DELAY = 0.5  # seconds between requests


class IntercomImporter:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Intercom-Version": "2.10"
        }
        self.collection_map = {}
        self.progress = self.load_progress()

    def load_progress(self) -> Dict:
        """Load import progress if resuming."""
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        return {
            "main_collection_id": None,
            "category_collections": {},
            "imported_articles": [],
            "failed_articles": []
        }

    def save_progress(self):
        """Save import progress."""
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROGRESS_FILE, "w") as f:
            json.dump(self.progress, f, indent=2)

    def create_collection(self, name: str, description: str, parent_id: Optional[str] = None) -> Optional[Dict]:
        """Create an Intercom collection."""
        payload = {
            "name": name,
            "description": description,
            "translated_content": {
                "en": {
                    "name": name,
                    "description": description
                }
            }
        }

        if parent_id:
            payload["parent_id"] = parent_id

        response = requests.post(
            f"{INTERCOM_API_BASE}/help_center/collections",
            headers=self.headers,
            json=payload
        )

        time.sleep(RATE_LIMIT_DELAY)

        if response.status_code == 201:
            return response.json()
        else:
            print(f"Error creating collection '{name}': {response.status_code} - {response.text}")
            return None

    def create_article(self, faq: Dict, collection_id: str, state: str = "published") -> Optional[Dict]:
        """Create an Intercom article from an FAQ."""

        # Truncate title if too long (Intercom max is ~255 chars)
        title = faq.get('question', 'Untitled')
        if len(title) > 200:
            title = title[:197] + "..."

        # Build article body with metadata
        body = f"{faq.get('answer', 'No answer available.')}\n\n"

        # Add metadata section
        if faq.get('insurer') or faq.get('policy_type'):
            body += "---\n\n"
            body += "### Policy Details\n\n"
            if faq.get('insurer'):
                body += f"**Insurer:** {faq['insurer']}\n\n"
            if faq.get('policy_type'):
                body += f"**Policy Type:** {faq['policy_type']}\n\n"

        if faq.get('section_reference'):
            body += f"*Policy Reference: {faq['section_reference']}*\n\n"

        # Add tags as keywords
        if faq.get('tags'):
            body += f"\n---\n\n*Tags: {', '.join(faq['tags'])}*"

        payload = {
            "title": title,
            "description": faq.get('answer', '')[:200] + "..." if len(faq.get('answer', '')) > 200 else faq.get('answer', ''),
            "body": body,
            "author_id": 9277214,
            "state": state,
            "parent_id": collection_id,
            "parent_type": "collection",
            "translated_content": {
                "en": {
                    "title": title,
                    "description": faq.get('answer', '')[:200] + "..." if len(faq.get('answer', '')) > 200 else faq.get('answer', ''),
                    "body": body,
                    "author_id": 9277214
                }
            }
        }

        response = requests.post(
            f"{INTERCOM_API_BASE}/articles",
            headers=self.headers,
            json=payload
        )

        time.sleep(RATE_LIMIT_DELAY)

        if response.status_code == 201:
            return response.json()
        else:
            print(f"\nError creating article: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None

    def setup_collections(self) -> bool:
        """Set up the collection structure."""

        # Check if already set up
        if self.progress.get("main_collection_id"):
            print("Collections already set up (resuming previous import)")
            self.collection_map = self.progress.get("category_collections", {})
            return True

        print("Setting up collection structure...")

        # Create main collection
        main_collection = self.create_collection(
            name="Internal: Policy Knowledge Base",
            description="Comprehensive policy information for internal team use only. Contains exclusions, claims requirements, eligibility criteria, endorsements, and policy definitions across all insurers."
        )

        if not main_collection:
            return False

        main_id = main_collection.get("id")
        self.progress["main_collection_id"] = main_id
        print(f"✓ Created main collection (ID: {main_id})")

        # Create category sub-collections
        categories = {
            "Exclusions": "What is NOT covered under each policy - the most common agent questions",
            "Claims Requirements": "Required documents, timeframes, process steps, and evidence needed for claims",
            "Eligibility": "Age limits, medical restrictions, occupational restrictions, and residency requirements",
            "Endorsements & Modifications": "Available policy add-ons and modifications with their coverage impacts",
            "Policy Definitions": "Key insurance terms and their specific meanings for each insurer",
            "Coverage Limits": "Maximum payout amounts, sub-limits, and benefit schedules",
            "Common Questions": "Frequently asked questions extracted from each policy document",
            "Comparisons": "Cross-insurer policy comparisons for key features"
        }

        for category, description in categories.items():
            print(f"  Creating '{category}' sub-collection...", end=" ")

            sub_collection = self.create_collection(
                name=category,
                description=description,
                parent_id=main_id
            )

            if sub_collection:
                self.collection_map[category] = sub_collection.get("id")
                print("✓")
            else:
                print("✗")
                return False

        self.progress["category_collections"] = self.collection_map
        self.save_progress()
        print()
        return True

    def import_faqs(self, faqs: List[Dict], publish: bool = False):
        """Import all FAQs to Intercom."""

        imported_ids = set(self.progress.get("imported_articles", []))
        total = len(faqs)
        success_count = len(imported_ids)
        failed_count = len(self.progress.get("failed_articles", []))

        state = "published" if publish else "draft"

        print(f"Importing {total} FAQs...")
        if imported_ids:
            print(f"Resuming from article {success_count + 1}")
        print()

        for idx, faq in enumerate(faqs, 1):
            faq_id = faq.get("id")

            # Skip if already imported
            if faq_id in imported_ids:
                continue

            category = faq.get("category", "Common Questions")
            collection_id = self.collection_map.get(category)

            if not collection_id:
                print(f"\nWarning: No collection for category '{category}', using Common Questions")
                collection_id = self.collection_map.get("Common Questions")

            # Progress indicator
            question = faq.get('question', 'Unknown')[:50]
            print(f"[{idx}/{total}] {question}...", end=" ", flush=True)

            # Create article
            article = self.create_article(faq, collection_id, state=state)

            if article:
                print("✓")
                success_count += 1
                self.progress["imported_articles"].append(faq_id)

                # Save progress every 10 articles
                if success_count % 10 == 0:
                    self.save_progress()
            else:
                print("✗")
                failed_count += 1
                self.progress["failed_articles"].append({
                    "id": faq_id,
                    "question": faq.get("question", "Unknown")
                })

            # Save progress every 50 articles
            if idx % 50 == 0:
                self.save_progress()
                print(f"\n  Progress saved ({success_count} imported, {failed_count} failed)\n")

        # Final save
        self.save_progress()
        print()
        return success_count, failed_count


def full_import():
    """Run the full import process."""

    if not INTERCOM_ACCESS_TOKEN:
        print("Error: INTERCOM_ACCESS_TOKEN not set")
        print("Please set it in your environment or .env file")
        return

    print("=" * 70)
    print("Intercom Full Import - All Policy FAQs")
    print("=" * 70)
    print()

    # Load FAQs
    print("Loading FAQs...")
    with open(FAQ_DATA_FILE, "r") as f:
        data = json.load(f)
        faqs = data.get("faqs", [])

    print(f"✓ Loaded {len(faqs)} FAQs\n")

    # Show breakdown
    categories = {}
    for faq in faqs:
        cat = faq.get("category", "Other")
        categories[cat] = categories.get(cat, 0) + 1

    print("FAQs by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    print()

    # Ask for confirmation
    print("This will import all FAQs to Intercom.")
    print("Articles will be created as DRAFTS for review before publishing.")
    print()

    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ["yes", "y"]:
        print("Import cancelled.")
        return

    # Initialize importer
    importer = IntercomImporter()

    # Set up collections
    if not importer.setup_collections():
        print("Failed to set up collections. Aborting.")
        return

    print()
    print("=" * 70)
    print("Starting import...")
    print("=" * 70)
    print()

    # Import FAQs
    success, failed = importer.import_faqs(faqs, publish=False)

    print()
    print("=" * 70)
    print("Import Complete!")
    print("=" * 70)
    print(f"Successfully imported: {success} articles")
    print(f"Failed: {failed} articles")
    print()

    if failed > 0:
        print("Failed articles saved to progress file:")
        print(f"  {PROGRESS_FILE}")
        print()

    print("Next steps:")
    print("1. Go to Intercom Help Center")
    print("2. Find 'Internal: Policy Knowledge Base' collection")
    print("3. Review draft articles")
    print("4. Publish articles when ready")
    print("5. Set collection to 'Team Only' visibility")
    print()
    print("To clean up progress and start fresh:")
    print(f"  rm {PROGRESS_FILE}")


if __name__ == "__main__":
    full_import()
