#!/usr/bin/env python3
"""
Intercom Import with Enhanced FAQs
Imports enhanced, agent-friendly FAQs to Intercom as internal articles.
"""

import json
import os
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
INTERCOM_ACCESS_TOKEN = os.environ.get("INTERCOM_ACCESS_TOKEN")
ENHANCED_FAQ_FILE = Path(__file__).parent.parent / "data" / "internal_faqs_enhanced.json"
FAQ_DATA_FILE = Path(__file__).parent.parent / "data" / "internal_faqs.json"
PROGRESS_FILE = Path(__file__).parent.parent / "data" / "intercom_import_progress.json"
INTERCOM_API_BASE = "https://api.intercom.io"
AUTHOR_ID = 9277214

# Rate limiting
RATE_LIMIT_DELAY = 0.5  # seconds between requests


class EnhancedIntercomImporter:
    def __init__(self, use_enhanced: bool = True):
        self.headers = {
            "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Intercom-Version": "2.10"
        }
        self.use_enhanced = use_enhanced
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

        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"Error creating collection '{name}': {response.status_code} - {response.text}")
            return None

    def format_enhanced_article_body(self, faq: Dict) -> str:
        """Format article body with enhanced content for agents."""

        if not self.use_enhanced or 'enhanced' not in faq:
            # Fall back to original format
            return self.format_basic_article_body(faq)

        enhanced = faq['enhanced']
        body = f"## Quick Answer\n\n{enhanced.get('quick_answer', faq.get('answer', ''))}\n\n"

        # Customer Impact
        if enhanced.get('customer_impact'):
            body += f"## What This Means for Your Customer\n\n{enhanced['customer_impact']}\n\n"

        # Communication Examples
        if enhanced.get('communication_examples'):
            body += "## How to Communicate This\n\n"
            body += "*Use these example phrases when speaking with customers:*\n\n"
            for idx, example in enumerate(enhanced['communication_examples'], 1):
                body += f"**Example {idx}:**\n> {example}\n\n"

        # Common Follow-ups
        if enhanced.get('common_followups'):
            body += "## Common Follow-up Questions\n\n"
            for followup in enhanced['common_followups']:
                q = followup.get('question', '')
                a = followup.get('answer', '')
                body += f"**Q: {q}**\n{a}\n\n"

        # Important Notes
        if enhanced.get('important_notes'):
            body += "## Important Notes for Agents\n\n"
            for note in enhanced['important_notes']:
                body += f"• {note}\n"
            body += "\n"

        # Policy Details
        body += "---\n\n## Policy Details\n\n"
        if faq.get('insurer'):
            body += f"**Insurer:** {faq['insurer']}\n\n"
        if faq.get('policy_type'):
            body += f"**Policy Type:** {faq['policy_type']}\n\n"
        if faq.get('section_reference'):
            body += f"*Policy Reference: {faq['section_reference']}*\n\n"

        # Tags
        if faq.get('tags'):
            body += f"\n---\n\n*Tags: {', '.join(faq['tags'])}*"

        return body

    def format_basic_article_body(self, faq: Dict) -> str:
        """Format basic article body (fallback)."""
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

        return body

    def create_article(self, faq: Dict, collection_id: str, state: str = "published") -> Optional[Dict]:
        """Create an Intercom article from an FAQ."""

        # Truncate title if too long
        title = faq.get('question', 'Untitled')
        if len(title) > 200:
            title = title[:197] + "..."

        # Format body
        body = self.format_enhanced_article_body(faq)

        # Create description
        if self.use_enhanced and 'enhanced' in faq:
            description = faq['enhanced'].get('quick_answer', '')[:200]
        else:
            description = faq.get('answer', '')[:200]

        if len(description) > 200:
            description = description[:197] + "..."

        payload = {
            "title": title,
            "description": description,
            "body": body,
            "author_id": AUTHOR_ID,
            "state": state,
            "parent_id": collection_id,
            "parent_type": "collection",
            "translated_content": {
                "en": {
                    "title": title,
                    "description": description,
                    "body": body,
                    "author_id": AUTHOR_ID
                }
            }
        }

        response = requests.post(
            f"{INTERCOM_API_BASE}/articles",
            headers=self.headers,
            json=payload
        )

        time.sleep(RATE_LIMIT_DELAY)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"\nError creating article: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None

    def setup_collections(self) -> bool:
        """Set up the collection structure."""

        # Check if already set up
        if self.progress.get("main_collection_id"):
            print("Collections already set up (resuming previous import)")
            self.collection_map = self.progress.get("category_collections", {})
            return True

        print("Setting up collection structure...")

        # Create main collection (marked as internal)
        main_collection = self.create_collection(
            name="[INTERNAL] Policy Knowledge Base",
            description="⚠️ INTERNAL USE ONLY - Comprehensive policy information for agent use. Contains exclusions, claims requirements, eligibility criteria, endorsements, and policy definitions across all insurers."
        )

        if not main_collection:
            return False

        main_id = main_collection.get("id")
        self.progress["main_collection_id"] = main_id
        print(f"✓ Created main collection (ID: {main_id})")
        print(f"  ⚠️  IMPORTANT: Set this collection to 'Team Only' in Intercom settings!")

        # Create category sub-collections
        categories = {
            "Exclusions": "What is NOT covered - critical information for setting customer expectations",
            "Claims Requirements": "Documents, timeframes, process steps - everything agents need for claims guidance",
            "Eligibility": "Age limits, restrictions, requirements - help agents qualify customers accurately",
            "Endorsements & Modifications": "Available add-ons and modifications - for upselling and customization",
            "Policy Definitions": "Key terms explained - ensure agents use correct terminology with customers",
            "Coverage Limits": "Maximum payouts and sub-limits - manage customer expectations accurately",
            "Common Questions": "FAQ directly from policies - quick answers to frequent queries",
            "Comparisons": "Cross-insurer comparisons - help agents recommend the right policy"
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
        print(f"Format: {'Enhanced (agent-friendly)' if self.use_enhanced else 'Basic'}")
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


def test_import_enhanced():
    """Run a test import with enhanced FAQs."""

    if not INTERCOM_ACCESS_TOKEN:
        print("Error: INTERCOM_ACCESS_TOKEN not set")
        return

    print("=" * 70)
    print("Intercom Test Import - Enhanced Agent-Friendly FAQs")
    print("=" * 70)
    print()

    # Load FAQs (try enhanced first, fall back to basic)
    if ENHANCED_FAQ_FILE.exists():
        print("Loading enhanced FAQs...")
        with open(ENHANCED_FAQ_FILE, 'r') as f:
            data = json.load(f)
            faqs = data.get('faqs', [])
        use_enhanced = True
    else:
        print("Enhanced FAQs not found, using basic FAQs...")
        print("Run 'python enhance_faqs_for_agents.py 20' to create enhanced versions")
        with open(FAQ_DATA_FILE, 'r') as f:
            data = json.load(f)
            faqs = data.get('faqs', [])
        use_enhanced = False

    # Take sample
    sample_faqs = faqs[:20]
    print(f"✓ Loaded {len(sample_faqs)} sample FAQs\n")

    # Show breakdown
    categories = {}
    for faq in sample_faqs:
        cat = faq.get("category", "Other")
        categories[cat] = categories.get(cat, 0) + 1

    print("Sample breakdown by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    print()

    # Create test collection
    importer = EnhancedIntercomImporter(use_enhanced=use_enhanced)

    print("Creating test collection...")
    test_collection = importer.create_collection(
        name="[TEST] Enhanced Policy Knowledge",
        description="TEST IMPORT - Enhanced agent-friendly policy FAQs. These are sample articles for testing. ⚠️ Set to TEAM ONLY"
    )

    if not test_collection:
        print("Failed to create test collection.")
        return

    collection_id = test_collection.get("id")
    print(f"✓ Created test collection (ID: {collection_id})")
    print(f"  ⚠️  IMPORTANT: Set to 'Team Only' in Intercom!")
    print()

    # Import articles
    print(f"Importing {len(sample_faqs)} articles...")
    success_count = 0
    failed_count = 0

    for idx, faq in enumerate(sample_faqs, 1):
        print(f"  [{idx}/{len(sample_faqs)}] {faq.get('question', 'Unknown')[:60]}...", end=" ")

        article = importer.create_article(faq, collection_id, state="draft")

        if article:
            print("✓")
            success_count += 1
        else:
            print("✗")
            failed_count += 1

    print()
    print("=" * 70)
    print("Test Import Complete!")
    print("=" * 70)
    print(f"Success: {success_count} articles")
    print(f"Failed: {failed_count} articles")
    print()
    print("Next steps:")
    print("1. Check Intercom and set collection to 'Team Only' visibility")
    print("2. Review articles - note the enhanced agent-friendly format")
    print("3. Test how agents can use the content in customer communications")
    print(f"4. Collection URL: https://intercom.help/pikl/en/collections/{collection_id}")


if __name__ == "__main__":
    test_import_enhanced()
