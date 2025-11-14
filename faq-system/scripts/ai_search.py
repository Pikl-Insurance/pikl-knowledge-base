#!/usr/bin/env python3
"""
AI-Powered Policy Search
Uses Claude with RAG (Retrieval Augmented Generation) to answer agent questions
by searching through processed policy data.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
import anthropic


# Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PROCESSED_POLICIES_DIR = Path(__file__).parent.parent.parent / "policy-wordings" / "processed"
FAQ_DATA_FILE = Path(__file__).parent.parent / "data" / "internal_faqs.json"


def load_knowledge_base() -> Dict:
    """Load all processed policies and FAQs into memory for RAG."""
    knowledge_base = {
        "policies": [],
        "faqs": []
    }

    # Load processed policies
    for json_file in PROCESSED_POLICIES_DIR.glob("*.json"):
        with open(json_file, "r") as f:
            knowledge_base["policies"].append(json.loads(f.read()))

    # Load FAQs if available
    if FAQ_DATA_FILE.exists():
        with open(FAQ_DATA_FILE, "r") as f:
            faq_data = json.loads(f.read())
            knowledge_base["faqs"] = faq_data.get("faqs", [])

    return knowledge_base


def search_policies(question: str, insurer: Optional[str] = None, policy_type: Optional[str] = None) -> str:
    """
    Search through policy documents to answer a question using Claude AI.

    Args:
        question: The question to answer
        insurer: Optional filter by insurer name
        policy_type: Optional filter by policy type (e.g., "Travel", "Home")

    Returns:
        AI-generated answer with sources
    """
    if not ANTHROPIC_API_KEY:
        return "Error: ANTHROPIC_API_KEY environment variable not set"

    # Load knowledge base
    kb = load_knowledge_base()

    if not kb["policies"]:
        return "Error: No processed policies found. Please run parse_policies.py first."

    # Filter policies if needed
    relevant_policies = kb["policies"]
    if insurer:
        relevant_policies = [p for p in relevant_policies if insurer.lower() in p.get("insurer_name", "").lower()]
    if policy_type:
        relevant_policies = [p for p in relevant_policies if policy_type.lower() in p.get("policy_type", "").lower()]

    if not relevant_policies:
        return f"No policies found matching filters: insurer={insurer}, policy_type={policy_type}"

    # Filter FAQs if needed
    relevant_faqs = kb["faqs"]
    if insurer:
        relevant_faqs = [f for f in relevant_faqs if insurer.lower() in f.get("insurer", "").lower()]
    if policy_type:
        relevant_faqs = [f for f in relevant_faqs if policy_type.lower() in f.get("policy_type", "").lower()]

    # Build context for Claude
    context = "# Insurance Policy Knowledge Base\n\n"

    context += "## Processed Policies\n\n"
    for policy in relevant_policies:
        context += f"### {policy.get('insurer_name')} - {policy.get('policy_type')}\n\n"
        context += f"**Coverage Summary:** {policy.get('coverage_summary', 'N/A')}\n\n"

        if policy.get('key_inclusions'):
            context += "**Key Inclusions:**\n"
            for incl in policy['key_inclusions']:
                context += f"- {incl}\n"
            context += "\n"

        if policy.get('key_exclusions'):
            context += "**Key Exclusions:**\n"
            for excl in policy['key_exclusions']:
                context += f"- {excl}\n"
            context += "\n"

        if policy.get('coverage_limits'):
            context += "**Coverage Limits:**\n"
            for category, limit in policy['coverage_limits'].items():
                context += f"- {category}: {limit}\n"
            context += "\n"

        if policy.get('special_conditions'):
            context += "**Special Conditions:**\n"
            for cond in policy['special_conditions']:
                context += f"- {cond}\n"
            context += "\n"

        if policy.get('age_restrictions'):
            context += f"**Age Restrictions:** {policy['age_restrictions']}\n\n"

        if policy.get('pre_existing_conditions'):
            context += f"**Pre-existing Conditions:** {policy['pre_existing_conditions']}\n\n"

        context += "---\n\n"

    # Add relevant FAQs
    if relevant_faqs:
        context += "## Existing FAQs\n\n"
        for faq in relevant_faqs[:20]:  # Limit to top 20 most relevant
            context += f"**Q:** {faq.get('question')}\n"
            context += f"**A:** {faq.get('answer')}\n\n"

    # Query Claude
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""You are an expert insurance policy assistant helping internal agents at Pikl answer questions about insurance policies.

Using the policy knowledge base provided below, answer the following question accurately and concisely:

QUESTION: {question}

KNOWLEDGE BASE:
{context}

Instructions:
- Provide a clear, direct answer based ONLY on the information in the knowledge base
- If the question asks about exclusions, list them clearly
- If comparing insurers, present information in a structured way
- Always cite which insurer/policy you're referencing
- If the information is not in the knowledge base, say so clearly
- Be specific about policy types when relevant (e.g., Travel vs Home insurance)
- For yes/no questions, start with YES or NO, then explain

Answer:"""

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def interactive_search():
    """Run an interactive search session."""
    print("=" * 60)
    print("Pikl Internal Policy Search (AI-Powered)")
    print("=" * 60)
    print()

    kb = load_knowledge_base()
    print(f"Loaded: {len(kb['policies'])} policies, {len(kb['faqs'])} FAQs\n")

    print("Available Insurers:")
    insurers = set(p.get("insurer_name") for p in kb["policies"])
    for insurer in sorted(insurers):
        print(f"  - {insurer}")

    print("\nAvailable Policy Types:")
    policy_types = set(p.get("policy_type") for p in kb["policies"])
    for ptype in sorted(policy_types):
        print(f"  - {ptype}")

    print("\n" + "=" * 60)
    print("Ask questions like:")
    print("  - Does AXA travel insurance exclude pre-existing conditions?")
    print("  - What are the coverage limits for Zurich home insurance?")
    print("  - Compare pregnancy exclusions across all travel insurers")
    print("  - What does Aviva exclude for mental health claims?")
    print("\nType 'quit' to exit\n")
    print("=" * 60)

    while True:
        question = input("\n\nYour question: ").strip()

        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if not question:
            continue

        print("\nSearching policies...\n")
        answer = search_policies(question)
        print("ANSWER:")
        print("-" * 60)
        print(answer)
        print("-" * 60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Command-line question
        question = " ".join(sys.argv[1:])
        print(f"Question: {question}\n")
        answer = search_policies(question)
        print(answer)
    else:
        # Interactive mode
        interactive_search()
