#!/usr/bin/env python3
"""
Intercom Internal Article Import (FIXED)
Creates TRUE internal articles using the /internal_articles endpoint with HTML formatting.
"""

import json
import os
import requests
import time
import markdown2
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
INTERCOM_ACCESS_TOKEN = os.environ.get("INTERCOM_ACCESS_TOKEN")
ENHANCED_FAQ_FILE = Path(__file__).parent.parent / "data" / "internal_faqs_enhanced.json"
FAQ_DATA_FILE = Path(__file__).parent.parent / "data" / "internal_faqs.json"
INTERCOM_API_BASE = "https://api.intercom.io"
AUTHOR_ID = 9277214

# Rate limiting
RATE_LIMIT_DELAY = 0.5


def markdown_to_html(markdown_text: str) -> str:
    """Convert Markdown to HTML compatible with Intercom."""
    # Convert markdown to HTML
    html = markdown2.markdown(markdown_text, extras=["break-on-newline", "fenced-code-blocks"])

    # Wrap paragraphs in Intercom's preferred format
    # Intercom uses <p class="no-margin"> for paragraphs
    html = html.replace('<p>', '<p class="no-margin">')

    return html


def format_enhanced_article_html(faq: Dict) -> str:
    """Format article body with enhanced content as HTML."""

    if 'enhanced' not in faq:
        # Fall back to basic format
        return format_basic_article_html(faq)

    enhanced = faq['enhanced']
    markdown_body = ""

    # Quick Answer
    markdown_body += f"## Quick Answer\n\n{enhanced.get('quick_answer', faq.get('answer', ''))}\n\n"

    # Customer Impact
    if enhanced.get('customer_impact'):
        markdown_body += f"## What This Means for Your Customer\n\n{enhanced['customer_impact']}\n\n"

    # Communication Examples
    if enhanced.get('communication_examples'):
        markdown_body += "## How to Communicate This\n\n"
        markdown_body += "*Use these example phrases when speaking with customers:*\n\n"
        for idx, example in enumerate(enhanced['communication_examples'], 1):
            markdown_body += f"**Example {idx}:**\n> {example}\n\n"

    # Common Follow-ups
    if enhanced.get('common_followups'):
        markdown_body += "## Common Follow-up Questions\n\n"
        for followup in enhanced['common_followups']:
            q = followup.get('question', '')
            a = followup.get('answer', '')
            markdown_body += f"**Q: {q}**\n\n{a}\n\n"

    # Important Notes
    if enhanced.get('important_notes'):
        markdown_body += "## Important Notes for Agents\n\n"
        for note in enhanced['important_notes']:
            markdown_body += f"• {note}\n\n"

    # Policy Details
    markdown_body += "---\n\n## Policy Details\n\n"
    if faq.get('insurer'):
        markdown_body += f"**Insurer:** {faq['insurer']}\n\n"
    if faq.get('policy_type'):
        markdown_body += f"**Policy Type:** {faq['policy_type']}\n\n"
    if faq.get('section_reference'):
        markdown_body += f"*Policy Reference: {faq['section_reference']}*\n\n"

    # Tags
    if faq.get('tags'):
        markdown_body += f"\n---\n\n*Tags: {', '.join(faq['tags'])}*"

    # Convert to HTML
    return markdown_to_html(markdown_body)


def format_basic_article_html(faq: Dict) -> str:
    """Format basic article body as HTML (fallback)."""
    markdown_body = f"{faq.get('answer', 'No answer available.')}\n\n"

    # Add metadata
    if faq.get('insurer') or faq.get('policy_type'):
        markdown_body += "---\n\n### Policy Details\n\n"
        if faq.get('insurer'):
            markdown_body += f"**Insurer:** {faq['insurer']}\n\n"
        if faq.get('policy_type'):
            markdown_body += f"**Policy Type:** {faq['policy_type']}\n\n"

    if faq.get('section_reference'):
        markdown_body += f"*Policy Reference: {faq['section_reference']}*\n\n"

    # Tags
    if faq.get('tags'):
        markdown_body += f"\n---\n\n*Tags: {', '.join(faq['tags'])}*"

    return markdown_to_html(markdown_body)


def create_internal_article(faq: Dict, folder_id: Optional[int] = None, state: str = "published") -> Optional[Dict]:
    """Create an internal article using the /internal_articles endpoint."""

    headers = {
        "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Intercom-Version": "Unstable"  # Required for internal articles
    }

    # Truncate title if too long
    title = faq.get('question', 'Untitled')
    if len(title) > 200:
        title = title[:197] + "..."

    # Format body as HTML
    if 'enhanced' in faq:
        body_html = format_enhanced_article_html(faq)
        description = faq['enhanced'].get('quick_answer', '')[:200]
    else:
        body_html = format_basic_article_html(faq)
        description = faq.get('answer', '')[:200]

    if len(description) > 200:
        description = description[:197] + "..."

    # Internal articles payload
    payload = {
        "title": title,
        "description": description,
        "body": body_html,
        "author_id": AUTHOR_ID,
        "owner_id": AUTHOR_ID,  # Internal articles require owner_id
        "state": state,
        "translated_content": {
            "en": {
                "title": title,
                "description": description,
                "body": body_html,
                "author_id": AUTHOR_ID
            }
        }
    }

    # Add folder if specified
    if folder_id:
        payload["folder_id"] = folder_id

    response = requests.post(
        f"{INTERCOM_API_BASE}/internal_articles",  # Internal articles endpoint
        headers=headers,
        json=payload
    )

    time.sleep(RATE_LIMIT_DELAY)

    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"\nError creating internal article: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return None


def test_internal_import(folder_id: Optional[int] = None, sample_size: int = 5):
    """Test import of internal articles with proper formatting."""

    if not INTERCOM_ACCESS_TOKEN:
        print("Error: INTERCOM_ACCESS_TOKEN not set")
        return

    print("=" * 70)
    print("Intercom INTERNAL Article Import - Fixed Version")
    print("=" * 70)
    print()
    print("✓ Using /internal_articles endpoint (not /articles)")
    print("✓ Converting Markdown to HTML")
    print("✓ Using Unstable API version")
    if folder_id:
        print(f"✓ Adding to folder ID: {folder_id}")
    print()

    # Load FAQs (try enhanced first, fall back to basic)
    if ENHANCED_FAQ_FILE.exists():
        print("Loading enhanced FAQs...")
        with open(ENHANCED_FAQ_FILE, 'r') as f:
            data = json.load(f)
            faqs = data.get('faqs', [])
        use_enhanced = True
    else:
        print("Loading basic FAQs...")
        with open(FAQ_DATA_FILE, 'r') as f:
            data = json.load(f)
            faqs = data.get('faqs', [])
        use_enhanced = False

    # Take sample for testing
    sample_faqs = faqs[:sample_size]
    print(f"✓ Loaded {len(sample_faqs)} sample FAQs")
    print(f"✓ Format: {'Enhanced (agent-friendly)' if use_enhanced else 'Basic'}")
    print()

    # Import articles
    print(f"Creating {len(sample_faqs)} INTERNAL articles...")
    success_count = 0
    failed_count = 0

    for idx, faq in enumerate(sample_faqs, 1):
        question = faq.get('question', 'Unknown')[:60]
        print(f"  [{idx}/{len(sample_faqs)}] {question}...", end=" ", flush=True)

        article = create_internal_article(faq, folder_id=folder_id, state="published")

        if article:
            print(f"✓ (ID: {article.get('id')})")
            success_count += 1
        else:
            print("✗")
            failed_count += 1

    print()
    print("=" * 70)
    print("Test Import Complete!")
    print("=" * 70)
    print(f"Success: {success_count} internal articles")
    print(f"Failed: {failed_count} articles")
    print()

    if success_count > 0:
        print("✓ Articles created as INTERNAL (team-only)")
        print("✓ Formatting should now display correctly (HTML)")
        if folder_id:
            print(f"✓ Articles added to folder: {folder_id}")
        print()
        print("Next steps:")
        print("1. Check Intercom folder - articles should appear there")
        print("2. Verify formatting looks correct (headers, bullets, etc.)")
        print("3. If good, proceed with more articles or full import")


if __name__ == "__main__":
    import sys

    # Check for folder ID argument
    folder_id = None
    sample_size = 5

    if len(sys.argv) > 1:
        try:
            folder_id = int(sys.argv[1])
        except ValueError:
            print(f"Invalid folder_id: {sys.argv[1]}")
            print("Usage: python intercom_import_internal.py [folder_id] [sample_size]")
            sys.exit(1)

    if len(sys.argv) > 2:
        try:
            sample_size = int(sys.argv[2])
        except ValueError:
            print(f"Invalid sample_size: {sys.argv[2]}")
            sys.exit(1)

    test_internal_import(folder_id=folder_id, sample_size=sample_size)
