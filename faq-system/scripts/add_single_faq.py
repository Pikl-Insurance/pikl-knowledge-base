#!/usr/bin/env python3
"""
Add a single FAQ to the internal FAQs collection.
"""

import json
import time
from pathlib import Path


def add_faq_to_collection(faq_data: dict, faqs_file: Path):
    """Add a single FAQ to the existing collection."""

    # Load existing FAQs
    with open(faqs_file, 'r') as f:
        data = json.load(f)

    # Add the new FAQ
    data['faqs'].append(faq_data)
    data['total_faqs'] = len(data['faqs'])

    # Save back
    with open(faqs_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✓ Added FAQ: {faq_data['question']}")
    print(f"  Total FAQs now: {data['total_faqs']}")

    return data['total_faqs']


def main():
    """Add the rent-to-rent holiday let FAQ."""

    # Define the new FAQ
    new_faq = {
        "id": "rent_to_rent_holiday_let_eligibility_topup",
        "category": "Common Questions",
        "question": "Can I get holiday let insurance if I'm renting the property and running it as a short-term let (rent-to-rent)?",
        "answer": """Unfortunately we cannot provide main buildings and contents insurance for the property as this is a rent-to-rent situation.

However, you can purchase the **top-up coverage** which covers the hosting element on our website www.pikl.com as long as:

1. You have existing buildings or contents insurance in place
2. Your insurer is aware of the hosting situation

This top-up includes:
• Public liability coverage
• Hosting-specific protection

**How to get a quote:**
1. Visit www.pikl.com
2. Select "Get a quote"
3. At step 3, choose "Top-up only"

If you have any questions about your specific situation, please get in touch with our team.""",
        "tags": [
            "rent-to-rent",
            "holiday let",
            "short-term let",
            "top-up coverage",
            "public liability",
            "eligibility",
            "hosting"
        ],
        "internal_only": true
    }

    # Path to FAQs file
    faqs_file = Path(__file__).parent.parent / "data" / "internal_faqs.json"

    if not faqs_file.exists():
        print(f"❌ FAQs file not found: {faqs_file}")
        return

    print("=" * 70)
    print("Adding New FAQ to Internal Knowledge Base")
    print("=" * 70)
    print()
    print(f"Question: {new_faq['question']}")
    print(f"Category: {new_faq['category']}")
    print(f"Tags: {', '.join(new_faq['tags'])}")
    print()

    # Add to collection
    total = add_faq_to_collection(new_faq, faqs_file)

    print()
    print("=" * 70)
    print("✓ FAQ Added Successfully!")
    print("=" * 70)
    print()
    print(f"Your knowledge base now contains {total} FAQs")
    print()
    print("Next steps:")
    print("  1. Review the FAQ in the data file")
    print("  2. Upload to Intercom using the import script")
    print("  3. Apply the 'common-questions' tag in Intercom")


if __name__ == "__main__":
    main()
