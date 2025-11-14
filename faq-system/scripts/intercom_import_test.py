#!/usr/bin/env python3
"""
Intercom Test Import
Imports a small sample of FAQs to Intercom for testing purposes.
"""

import json
import os
import requests
from pathlib import Path
from typing import Dict, List

# Configuration
INTERCOM_ACCESS_TOKEN = os.environ.get("INTERCOM_ACCESS_TOKEN")
FAQ_DATA_FILE = Path(__file__).parent.parent / "data" / "internal_faqs.json"
INTERCOM_API_BASE = "https://api.intercom.io"

# Sample size
SAMPLE_SIZE = 20


def load_sample_faqs(sample_size: int = SAMPLE_SIZE) -> List[Dict]:
    """Load a sample of FAQs for testing."""
    with open(FAQ_DATA_FILE, "r") as f:
        data = json.loads(f.read())
        all_faqs = data.get("faqs", [])

    # Get a diverse sample across categories
    sample = []
    categories_seen = set()

    # Try to get at least one from each category
    for faq in all_faqs:
        category = faq.get("category", "Other")
        if category not in categories_seen:
            sample.append(faq)
            categories_seen.add(category)

        if len(sample) >= sample_size:
            break

    # Fill remaining with any FAQs
    if len(sample) < sample_size:
        for faq in all_faqs:
            if faq not in sample:
                sample.append(faq)
                if len(sample) >= sample_size:
                    break

    return sample


def create_collection(name: str, description: str, parent_id: str = None) -> Dict:
    """Create an Intercom collection (help center section)."""
    headers = {
        "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

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
        headers=headers,
        json=payload
    )

    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"Error creating collection '{name}': {response.status_code} - {response.text}")
        return None


def create_article(faq: Dict, collection_id: str) -> Dict:
    """Create an Intercom article from an FAQ."""
    headers = {
        "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Truncate title if too long (Intercom max is ~255 chars)
    title = faq.get('question', 'Untitled')
    if len(title) > 200:
        title = title[:197] + "..."

    # Build article body with metadata
    body = f"{faq.get('answer', 'No answer available.')}\n\n"

    # Add metadata
    if faq.get('insurer') or faq.get('policy_type'):
        body += "---\n\n**Policy Information:**\n"
        if faq.get('insurer'):
            body += f"- Insurer: {faq['insurer']}\n"
        if faq.get('policy_type'):
            body += f"- Policy Type: {faq['policy_type']}\n"
        body += "\n"

    if faq.get('section_reference'):
        body += f"*Reference: {faq['section_reference']}*\n\n"

    payload = {
        "title": title,
        "description": faq.get('answer', '')[:200] + "...",  # Short description
        "body": body,
        "author_id": 9277214,
        "state": "draft",  # Start as draft for review
        "parent_id": collection_id,
        "parent_type": "collection",
        "translated_content": {
            "en": {
                "title": title,
                "description": faq.get('answer', '')[:200] + "...",
                "body": body,
                "author_id": 9277214,
                "state": "draft"
            }
        }
    }

    response = requests.post(
        f"{INTERCOM_API_BASE}/articles",
        headers=headers,
        json=payload
    )

    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"Error creating article '{faq.get('question', 'Unknown')}': {response.status_code} - {response.text}")
        return None


def test_import():
    """Run a test import of sample FAQs."""

    if not INTERCOM_ACCESS_TOKEN:
        print("Error: INTERCOM_ACCESS_TOKEN not set")
        print("Please set it in your environment or .env file")
        return

    print("=" * 60)
    print("Intercom Test Import - Sample FAQs")
    print("=" * 60)
    print()

    # Load sample FAQs
    print(f"Loading {SAMPLE_SIZE} sample FAQs...")
    sample_faqs = load_sample_faqs(SAMPLE_SIZE)
    print(f"✓ Loaded {len(sample_faqs)} FAQs for testing\n")

    # Show sample breakdown
    categories = {}
    for faq in sample_faqs:
        cat = faq.get("category", "Other")
        categories[cat] = categories.get(cat, 0) + 1

    print("Sample breakdown by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    print()

    # Create test collection
    print("Creating test collection in Intercom...")
    test_collection = create_collection(
        name="[TEST] Internal Policy Knowledge",
        description="TEST IMPORT - Policy FAQs for internal team use. These are sample articles for testing."
    )

    if not test_collection:
        print("Failed to create test collection. Aborting.")
        return

    collection_id = test_collection.get("id")
    print(f"✓ Created test collection (ID: {collection_id})\n")

    # Import articles
    print(f"Importing {len(sample_faqs)} articles...")
    success_count = 0
    failed_count = 0

    for idx, faq in enumerate(sample_faqs, 1):
        print(f"  [{idx}/{len(sample_faqs)}] {faq.get('question', 'Unknown')[:60]}...", end=" ")

        article = create_article(faq, collection_id)

        if article:
            print("✓")
            success_count += 1
        else:
            print("✗")
            failed_count += 1

    print()
    print("=" * 60)
    print("Test Import Complete!")
    print("=" * 60)
    print(f"Success: {success_count} articles")
    print(f"Failed: {failed_count} articles")
    print()
    print("Next steps:")
    print("1. Check Intercom Help Center for the test collection")
    print("2. Review how articles look and search works")
    print("3. If satisfied, run the full import script")
    print("4. Delete test collection when done testing")


if __name__ == "__main__":
    test_import()
