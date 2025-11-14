#!/usr/bin/env python3
"""
Import All Enhanced FAQs to Intercom Internal Folder
Imports all enhanced FAQs from internal_faqs_enhanced.json to specified folder.
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
INTERCOM_API_BASE = "https://api.intercom.io"
AUTHOR_ID = 9277214
RATE_LIMIT_DELAY = 0.5


def markdown_to_html(markdown_text: str) -> str:
    """Convert Markdown to HTML compatible with Intercom."""
    html = markdown2.markdown(markdown_text, extras=["break-on-newline", "fenced-code-blocks"])
    html = html.replace('<p>', '<p class="no-margin">')
    return html


def format_enhanced_article_html(faq: Dict) -> str:
    """Format article body with enhanced content as HTML."""

    if 'enhanced' not in faq:
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

    return markdown_to_html(markdown_body)


def format_basic_article_html(faq: Dict) -> str:
    """Format basic article body as HTML (fallback)."""
    markdown_body = f"{faq.get('answer', 'No answer available.')}\n\n"

    if faq.get('insurer') or faq.get('policy_type'):
        markdown_body += "---\n\n### Policy Details\n\n"
        if faq.get('insurer'):
            markdown_body += f"**Insurer:** {faq['insurer']}\n\n"
        if faq.get('policy_type'):
            markdown_body += f"**Policy Type:** {faq['policy_type']}\n\n"

    if faq.get('section_reference'):
        markdown_body += f"*Policy Reference: {faq['section_reference']}*\n\n"

    if faq.get('tags'):
        markdown_body += f"\n---\n\n*Tags: {', '.join(faq['tags'])}*"

    return markdown_to_html(markdown_body)


def create_internal_article(faq: Dict, folder_id: int, state: str = "published") -> Optional[Dict]:
    """Create an internal article."""

    headers = {
        "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Intercom-Version": "Unstable"
    }

    title = faq.get('question', 'Untitled')
    if len(title) > 200:
        title = title[:197] + "..."

    if 'enhanced' in faq:
        body_html = format_enhanced_article_html(faq)
        description = faq['enhanced'].get('quick_answer', '')[:200]
    else:
        body_html = format_basic_article_html(faq)
        description = faq.get('answer', '')[:200]

    if len(description) > 200:
        description = description[:197] + "..."

    payload = {
        "title": title,
        "description": description,
        "body": body_html,
        "author_id": AUTHOR_ID,
        "owner_id": AUTHOR_ID,
        "state": state,
        "folder_id": folder_id,
        "translated_content": {
            "en": {
                "title": title,
                "description": description,
                "body": body_html,
                "author_id": AUTHOR_ID
            }
        }
    }

    response = requests.post(
        f"{INTERCOM_API_BASE}/internal_articles",
        headers=headers,
        json=payload
    )

    time.sleep(RATE_LIMIT_DELAY)

    if response.status_code in [200, 201]:
        return response.json()
    else:
        return None


def import_all_enhanced(folder_id: int):
    """Import all enhanced FAQs."""

    if not INTERCOM_ACCESS_TOKEN:
        print("Error: INTERCOM_ACCESS_TOKEN not set")
        return

    if not ENHANCED_FAQ_FILE.exists():
        print(f"Error: Enhanced FAQ file not found: {ENHANCED_FAQ_FILE}")
        return

    print("=" * 70)
    print("Import All Enhanced FAQs to Intercom")
    print("=" * 70)
    print()

    # Load enhanced FAQs
    with open(ENHANCED_FAQ_FILE, 'r') as f:
        data = json.load(f)
        faqs = data.get('faqs', [])

    print(f"✓ Loaded {len(faqs)} enhanced FAQs")
    print(f"✓ Target folder ID: {folder_id}")
    print()

    # Import
    print(f"Importing {len(faqs)} articles...")
    success_count = 0
    failed_count = 0

    for idx, faq in enumerate(faqs, 1):
        question = faq.get('question', 'Unknown')[:60]
        print(f"  [{idx}/{len(faqs)}] {question}...", end=" ", flush=True)

        article = create_internal_article(faq, folder_id=folder_id, state="published")

        if article:
            print(f"✓")
            success_count += 1
        else:
            print(f"✗")
            failed_count += 1

        # Progress update every 20 articles
        if idx % 20 == 0:
            print(f"\n  Progress: {success_count} imported, {failed_count} failed\n")

    print()
    print("=" * 70)
    print("Import Complete!")
    print("=" * 70)
    print(f"Success: {success_count} articles")
    print(f"Failed: {failed_count} articles")
    print()
    print(f"View in Intercom: https://app.intercom.com/a/apps/irjtf4l5/knowledge-hub/folder/{folder_id}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python import_all_enhanced.py <folder_id>")
        print("Example: python import_all_enhanced.py 2703344")
        sys.exit(1)

    try:
        folder_id = int(sys.argv[1])
    except ValueError:
        print(f"Invalid folder_id: {sys.argv[1]}")
        sys.exit(1)

    import_all_enhanced(folder_id)
