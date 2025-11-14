#!/usr/bin/env python3
"""
Enhance FAQs for Agent Use
Adds customer context, communication guidance, and practical examples to FAQs.
"""

import json
import os
from pathlib import Path
from anthropic import Anthropic

# Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
FAQ_DATA_FILE = Path(__file__).parent.parent / "data" / "internal_faqs.json"
ENHANCED_FAQ_FILE = Path(__file__).parent.parent / "data" / "internal_faqs_enhanced.json"

client = Anthropic(api_key=ANTHROPIC_API_KEY)

ENHANCEMENT_PROMPT = """You are enhancing internal knowledge base articles for insurance agents. Your goal is to transform technical policy information into agent-friendly content that can be directly used in customer communications.

For the given FAQ, create an enhanced version with these sections:

1. **Quick Answer**: A concise, direct answer (2-3 sentences)

2. **What This Means for Your Customer**: Explain the practical implications in plain language. What does this actually mean for them? How does it affect their coverage?

3. **How to Communicate This**: Provide 2-3 example phrases or scripts agents can use when explaining this to customers. Make it natural, empathetic, and clear.

4. **Common Follow-up Questions**: List 2-3 questions customers typically ask about this topic, with brief answers.

5. **Important Notes**: Any critical details agents should remember (e.g., exceptions, time limits, documentation requirements).

Format your response as JSON with these keys: quick_answer, customer_impact, communication_examples (array), common_followups (array of objects with question and answer keys), important_notes (array).

Original FAQ:
Question: {{question}}
Answer: {{answer}}
Insurer: {{insurer}}
Policy Type: {{policy_type}}
Category: {{category}}
"""


def enhance_faq(faq: dict) -> dict:
    """Use Claude to enhance an FAQ with agent-friendly context."""

    prompt = ENHANCEMENT_PROMPT.replace('{{question}}', faq.get('question', ''))
    prompt = prompt.replace('{{answer}}', faq.get('answer', ''))
    prompt = prompt.replace('{{insurer}}', faq.get('insurer', ''))
    prompt = prompt.replace('{{policy_type}}', faq.get('policy_type', ''))
    prompt = prompt.replace('{{category}}', faq.get('category', ''))

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse Claude's response
        response_text = message.content[0].text

        # Extract JSON from response (Claude might wrap it in markdown)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        enhanced_data = json.loads(response_text)

        # Add enhanced data to FAQ
        faq['enhanced'] = {
            'quick_answer': enhanced_data.get('quick_answer', ''),
            'customer_impact': enhanced_data.get('customer_impact', ''),
            'communication_examples': enhanced_data.get('communication_examples', []),
            'common_followups': enhanced_data.get('common_followups', []),
            'important_notes': enhanced_data.get('important_notes', [])
        }

        return faq

    except Exception as e:
        print(f"Error enhancing FAQ: {e}")
        return faq


def enhance_all_faqs(sample_size: int = None):
    """Enhance FAQs with agent-friendly context."""

    print("=" * 70)
    print("Enhancing FAQs for Agent Use")
    print("=" * 70)
    print()

    # Load existing FAQs
    print("Loading FAQs...")
    with open(FAQ_DATA_FILE, 'r') as f:
        data = json.load(f)
        faqs = data.get('faqs', [])

    print(f"✓ Loaded {len(faqs)} FAQs")
    print()

    # If sample size specified, only process a sample
    if sample_size:
        faqs = faqs[:sample_size]
        print(f"Processing sample of {sample_size} FAQs...")
    else:
        print(f"Processing all {len(faqs)} FAQs...")
        confirm = input("This will use significant API credits. Continue? (yes/no): ")
        if confirm.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return

    print()

    # Enhance each FAQ
    enhanced_faqs = []
    for idx, faq in enumerate(faqs, 1):
        print(f"[{idx}/{len(faqs)}] Enhancing: {faq.get('question', 'Unknown')[:60]}...", end=" ")

        enhanced_faq = enhance_faq(faq)
        enhanced_faqs.append(enhanced_faq)

        if 'enhanced' in enhanced_faq:
            print("✓")
        else:
            print("✗")

        # Save progress every 10 FAQs
        if idx % 10 == 0:
            save_enhanced_faqs(enhanced_faqs, data)
            print(f"  Progress saved ({idx} enhanced)\n")

    # Final save
    save_enhanced_faqs(enhanced_faqs, data)

    print()
    print("=" * 70)
    print("Enhancement Complete!")
    print("=" * 70)
    print(f"Enhanced FAQs saved to: {ENHANCED_FAQ_FILE}")


def save_enhanced_faqs(faqs: list, original_data: dict):
    """Save enhanced FAQs to file."""
    output_data = {
        "generated_date": original_data.get("generated_date"),
        "enhanced_date": str(Path(__file__).stat().st_mtime),
        "total_faqs": len(faqs),
        "faqs": faqs
    }

    ENHANCED_FAQ_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ENHANCED_FAQ_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)


if __name__ == "__main__":
    import sys

    # Check if sample size provided
    sample_size = None
    if len(sys.argv) > 1:
        try:
            sample_size = int(sys.argv[1])
        except ValueError:
            print("Usage: python enhance_faqs_for_agents.py [sample_size]")
            sys.exit(1)

    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    enhance_all_faqs(sample_size)
