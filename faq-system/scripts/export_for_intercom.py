#!/usr/bin/env python3
"""
Intercom FAQ Exporter
Exports generated FAQs in a format suitable for importing into Intercom as internal team articles.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict


FAQ_DATA_FILE = Path(__file__).parent.parent / "data" / "internal_faqs.json"
EXPORT_DIR = Path(__file__).parent.parent / "data" / "exports"


def load_faqs() -> List[Dict]:
    """Load FAQs from JSON file."""
    if not FAQ_DATA_FILE.exists():
        print(f"Error: FAQ file not found at {FAQ_DATA_FILE}")
        print("Please run generate_faqs.py first.")
        return []

    with open(FAQ_DATA_FILE, "r") as f:
        data = json.loads(f.read())
        return data.get("faqs", [])


def export_to_csv(faqs: List[Dict]):
    """
    Export FAQs to CSV format for Intercom import.

    Intercom CSV format typically requires:
    - Title (question)
    - Body (answer)
    - URL slug (optional)
    - Author email (optional)
    - Collection (category)
    - Tags
    """
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = EXPORT_DIR / "intercom_faqs.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "Title",
            "Body",
            "Category",
            "Tags",
            "Insurer",
            "Policy Type",
            "Internal Only"
        ])

        # Data rows
        for faq in faqs:
            writer.writerow([
                faq.get("question", ""),
                faq.get("answer", "").replace("\n", " | "),  # Replace newlines for CSV
                faq.get("category", ""),
                ", ".join(faq.get("tags", [])),
                faq.get("insurer", ""),
                faq.get("policy_type", ""),
                "Yes" if faq.get("internal_only", True) else "No"
            ])

    print(f"✓ Exported {len(faqs)} FAQs to CSV: {output_file}")
    return output_file


def export_to_markdown(faqs: List[Dict]):
    """Export FAQs to Markdown format for easy reading and manual import."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Group by category
    faqs_by_category = {}
    for faq in faqs:
        cat = faq.get("category", "Other")
        if cat not in faqs_by_category:
            faqs_by_category[cat] = []
        faqs_by_category[cat].append(faq)

    output_file = EXPORT_DIR / "intercom_faqs.md"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Pikl Internal Knowledge Base - Policy FAQs\n\n")
        f.write("*For Internal Team Use Only*\n\n")
        f.write("---\n\n")

        for category in sorted(faqs_by_category.keys()):
            f.write(f"## {category}\n\n")

            for faq in faqs_by_category[category]:
                # Title
                f.write(f"### {faq.get('question', 'Untitled')}\n\n")

                # Metadata
                if faq.get("insurer") or faq.get("policy_type"):
                    f.write("**Policy Details:**\n")
                    if faq.get("insurer"):
                        f.write(f"- Insurer: {faq['insurer']}\n")
                    if faq.get("policy_type"):
                        f.write(f"- Policy Type: {faq['policy_type']}\n")
                    f.write("\n")

                # Answer
                f.write(f"{faq.get('answer', 'No answer available.')}\n\n")

                # Section reference if available
                if faq.get("section_reference"):
                    f.write(f"*Reference: {faq['section_reference']}*\n\n")

                # Tags
                if faq.get("tags"):
                    f.write(f"**Tags:** {', '.join(faq['tags'])}\n\n")

                f.write("---\n\n")

    print(f"✓ Exported FAQs to Markdown: {output_file}")
    return output_file


def export_to_json_structured(faqs: List[Dict]):
    """Export FAQs in a structured JSON format suitable for API import."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = EXPORT_DIR / "intercom_faqs_structured.json"

    # Group by insurer and policy type for easier navigation
    structured = {
        "metadata": {
            "total_faqs": len(faqs),
            "export_format": "intercom_compatible",
            "internal_only": True
        },
        "categories": {}
    }

    for faq in faqs:
        category = faq.get("category", "Other")
        if category not in structured["categories"]:
            structured["categories"][category] = {
                "name": category,
                "articles": []
            }

        article = {
            "title": faq.get("question", ""),
            "body": faq.get("answer", ""),
            "internal": faq.get("internal_only", True),
            "metadata": {
                "insurer": faq.get("insurer"),
                "policy_type": faq.get("policy_type"),
                "tags": faq.get("tags", []),
                "section_reference": faq.get("section_reference")
            }
        }

        structured["categories"][category]["articles"].append(article)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2)

    print(f"✓ Exported FAQs to structured JSON: {output_file}")
    return output_file


def export_by_insurer(faqs: List[Dict]):
    """Export separate files for each insurer."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    insurer_dir = EXPORT_DIR / "by_insurer"
    insurer_dir.mkdir(exist_ok=True)

    # Group by insurer
    faqs_by_insurer = {}
    for faq in faqs:
        insurer = faq.get("insurer", "General")
        if insurer not in faqs_by_insurer:
            faqs_by_insurer[insurer] = []
        faqs_by_insurer[insurer].append(faq)

    for insurer, insurer_faqs in faqs_by_insurer.items():
        filename = insurer_dir / f"{insurer.lower().replace(' ', '_')}_faqs.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({
                "insurer": insurer,
                "total_faqs": len(insurer_faqs),
                "faqs": insurer_faqs
            }, f, indent=2)
        print(f"  ✓ {insurer}: {len(insurer_faqs)} FAQs")


def generate_summary_report(faqs: List[Dict]):
    """Generate a summary report of the FAQ data."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = EXPORT_DIR / "faq_summary.txt"

    # Gather statistics
    total_faqs = len(faqs)
    categories = {}
    insurers = {}
    policy_types = {}

    for faq in faqs:
        # Categories
        cat = faq.get("category", "Other")
        categories[cat] = categories.get(cat, 0) + 1

        # Insurers
        ins = faq.get("insurer", "General")
        insurers[ins] = insurers.get(ins, 0) + 1

        # Policy types
        ptype = faq.get("policy_type", "General")
        policy_types[ptype] = policy_types.get(ptype, 0) + 1

    with open(output_file, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("Pikl Internal FAQ System - Summary Report\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Total FAQs Generated: {total_faqs}\n\n")

        f.write("FAQs by Category:\n")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {cat}: {count}\n")

        f.write("\nFAQs by Insurer:\n")
        for ins, count in sorted(insurers.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {ins}: {count}\n")

        f.write("\nFAQs by Policy Type:\n")
        for ptype, count in sorted(policy_types.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {ptype}: {count}\n")

    print(f"✓ Generated summary report: {output_file}")


def export_all():
    """Run all export formats."""
    print("Loading FAQs...")
    faqs = load_faqs()

    if not faqs:
        return

    print(f"\nExporting {len(faqs)} FAQs in multiple formats...\n")

    # Export in various formats
    export_to_csv(faqs)
    export_to_markdown(faqs)
    export_to_json_structured(faqs)

    print("\nExporting by insurer...")
    export_by_insurer(faqs)

    print("\nGenerating summary report...")
    generate_summary_report(faqs)

    print("\n" + "=" * 60)
    print("Export complete!")
    print(f"All files saved to: {EXPORT_DIR}")
    print("=" * 60)
    print("\nFor Intercom import:")
    print("1. Use intercom_faqs.csv for bulk import via CSV")
    print("2. Use intercom_faqs.md for manual copy-paste")
    print("3. Use intercom_faqs_structured.json for API import")
    print("\nAll articles should be marked as 'Internal Only' in Intercom")


if __name__ == "__main__":
    export_all()
