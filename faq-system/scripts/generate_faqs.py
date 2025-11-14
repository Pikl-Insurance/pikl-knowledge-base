#!/usr/bin/env python3
"""
FAQ Generator
Generates comprehensive FAQ entries from processed policy data for internal team use.
"""

import json
import os
from pathlib import Path
from typing import List, Dict
import anthropic

# Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PROCESSED_POLICIES_DIR = Path(__file__).parent.parent.parent / "policy-wordings" / "processed"
FAQ_OUTPUT_DIR = Path(__file__).parent.parent / "data"


def load_all_policies() -> List[Dict]:
    """Load all processed policy JSON files."""
    policies = []
    for json_file in PROCESSED_POLICIES_DIR.glob("*.json"):
        with open(json_file, "r") as f:
            policies.append(json.loads(f.read()))
    return policies


def generate_exclusion_faqs(policies: List[Dict]) -> List[Dict]:
    """
    Generate FAQ entries specifically about exclusions across all insurers.
    This is the most requested type of question internally.
    """
    faqs = []

    # Group exclusions by insurer
    for policy in policies:
        insurer = policy.get("insurer_name", "Unknown")
        policy_type = policy.get("policy_type", "Unknown")
        exclusions = policy.get("key_exclusions", [])

        # Create general exclusion overview FAQ
        faqs.append({
            "id": f"exclusion_overview_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
            "category": "Exclusions",
            "insurer": insurer,
            "policy_type": policy_type,
            "question": f"What does {insurer} {policy_type} insurance exclude?",
            "answer": f"The following are NOT covered under {insurer}'s {policy_type} policy:\n\n" +
                     "\n".join([f"• {excl}" for excl in exclusions]),
            "tags": ["exclusions", insurer.lower(), policy_type.lower()],
            "internal_only": True
        })

        # Create specific exclusion FAQs for common items
        common_exclusion_types = [
            "pre-existing conditions",
            "pregnancy",
            "mental health",
            "alcohol",
            "drugs",
            "extreme sports",
            "terrorism",
            "pandemics",
            "war",
            "valuables",
            "electronics"
        ]

        for excl_type in common_exclusion_types:
            matching_exclusions = [e for e in exclusions if excl_type.lower() in e.lower()]
            if matching_exclusions:
                faqs.append({
                    "id": f"exclusion_{excl_type.replace(' ', '_')}_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
                    "category": "Exclusions",
                    "insurer": insurer,
                    "policy_type": policy_type,
                    "question": f"Does {insurer} {policy_type} insurance exclude {excl_type}?",
                    "answer": f"Yes, {insurer}'s {policy_type} policy excludes:\n\n" +
                             "\n".join([f"• {e}" for e in matching_exclusions]),
                    "tags": ["exclusions", excl_type.replace(" ", "-"), insurer.lower(), policy_type.lower()],
                    "internal_only": True
                })

    return faqs


def generate_coverage_limit_faqs(policies: List[Dict]) -> List[Dict]:
    """Generate FAQs about coverage limits."""
    faqs = []

    for policy in policies:
        insurer = policy.get("insurer_name", "Unknown")
        policy_type = policy.get("policy_type", "Unknown")
        limits = policy.get("coverage_limits", {})

        if limits:
            for category, limit_info in limits.items():
                faqs.append({
                    "id": f"limit_{category.lower().replace(' ', '_')}_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
                    "category": "Coverage Limits",
                    "insurer": insurer,
                    "policy_type": policy_type,
                    "question": f"What is the coverage limit for {category} under {insurer} {policy_type}?",
                    "answer": limit_info,
                    "tags": ["limits", category.lower().replace(" ", "-"), insurer.lower(), policy_type.lower()],
                    "internal_only": True
                })

    return faqs


def generate_comparison_faqs(policies: List[Dict]) -> List[Dict]:
    """Generate comparison FAQs across insurers for the same policy type."""
    faqs = []

    # Group by policy type
    policies_by_type = {}
    for policy in policies:
        ptype = policy.get("policy_type", "Unknown")
        if ptype not in policies_by_type:
            policies_by_type[ptype] = []
        policies_by_type[ptype].append(policy)

    # Generate comparisons for each policy type
    for policy_type, type_policies in policies_by_type.items():
        if len(type_policies) < 2:
            continue  # Need at least 2 insurers to compare

        # Compare exclusions
        exclusion_comparison = {}
        for policy in type_policies:
            insurer = policy.get("insurer_name", "Unknown")
            exclusions = policy.get("key_exclusions", [])
            exclusion_comparison[insurer] = exclusions

        comparison_text = f"Here's how {policy_type} exclusions compare across insurers:\n\n"
        for insurer, exclusions in exclusion_comparison.items():
            comparison_text += f"**{insurer}:**\n"
            comparison_text += "\n".join([f"• {e}" for e in exclusions[:5]])  # Top 5
            comparison_text += f"\n({len(exclusions)} total exclusions)\n\n"

        faqs.append({
            "id": f"comparison_exclusions_{policy_type.lower().replace(' ', '_')}",
            "category": "Comparisons",
            "policy_type": policy_type,
            "question": f"How do {policy_type} exclusions compare across different insurers?",
            "answer": comparison_text,
            "tags": ["comparison", "exclusions", policy_type.lower()],
            "internal_only": True
        })

    return faqs


def generate_endorsement_faqs(policies: List[Dict]) -> List[Dict]:
    """Generate FAQs about available endorsements and policy modifications."""
    faqs = []

    for policy in policies:
        insurer = policy.get("insurer_name", "Unknown")
        policy_type = policy.get("policy_type", "Unknown")
        endorsements = policy.get("endorsements", [])

        if not endorsements:
            continue

        # Overview of available endorsements
        endorsement_list = "\n\n".join([
            f"**{e.get('name', 'Unknown')}**\n{e.get('description', 'No description')}\n" +
            (f"Cost impact: {e.get('cost_impact', 'Not specified')}\n" if e.get('cost_impact') else "") +
            (f"Coverage impact: {e.get('coverage_impact', 'Not specified')}" if e.get('coverage_impact') else "")
            for e in endorsements
        ])

        faqs.append({
            "id": f"endorsements_overview_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
            "category": "Endorsements & Modifications",
            "insurer": insurer,
            "policy_type": policy_type,
            "question": f"What endorsements are available for {insurer} {policy_type} insurance?",
            "answer": f"The following endorsements can be added to {insurer}'s {policy_type} policy:\n\n{endorsement_list}",
            "tags": ["endorsements", "modifications", insurer.lower(), policy_type.lower()],
            "internal_only": True
        })

        # Individual endorsement FAQs
        for endorsement in endorsements:
            name = endorsement.get("name", "Unknown")
            faqs.append({
                "id": f"endorsement_{name.lower().replace(' ', '_')}_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
                "category": "Endorsements & Modifications",
                "insurer": insurer,
                "policy_type": policy_type,
                "question": f"What does the '{name}' endorsement do for {insurer} {policy_type}?",
                "answer": f"{endorsement.get('description', 'No description available.')}\n\n" +
                         (f"**Cost Impact:** {endorsement.get('cost_impact', 'Not specified')}\n" if endorsement.get('cost_impact') else "") +
                         (f"**Coverage Impact:** {endorsement.get('coverage_impact', 'Not specified')}" if endorsement.get('coverage_impact') else ""),
                "tags": ["endorsements", name.lower().replace(" ", "-"), insurer.lower(), policy_type.lower()],
                "internal_only": True
            })

    return faqs


def generate_claims_faqs(policies: List[Dict]) -> List[Dict]:
    """Generate FAQs about claims requirements and process."""
    faqs = []

    for policy in policies:
        insurer = policy.get("insurer_name", "Unknown")
        policy_type = policy.get("policy_type", "Unknown")
        claims = policy.get("claims_requirements", {})

        if not claims:
            continue

        # Documents required FAQ
        if claims.get("required_documents"):
            docs_list = "\n".join([f"• {doc}" for doc in claims["required_documents"]])
            faqs.append({
                "id": f"claims_documents_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
                "category": "Claims Requirements",
                "insurer": insurer,
                "policy_type": policy_type,
                "question": f"What documents are needed to file a claim with {insurer} {policy_type}?",
                "answer": f"To file a claim with {insurer}'s {policy_type} policy, you need:\n\n{docs_list}",
                "tags": ["claims", "documents", insurer.lower(), policy_type.lower()],
                "internal_only": True
            })

        # Timeframe FAQ
        if claims.get("notification_timeframe"):
            faqs.append({
                "id": f"claims_timeframe_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
                "category": "Claims Requirements",
                "insurer": insurer,
                "policy_type": policy_type,
                "question": f"How quickly must I report a claim to {insurer} {policy_type}?",
                "answer": claims["notification_timeframe"],
                "tags": ["claims", "timeframe", "deadline", insurer.lower(), policy_type.lower()],
                "internal_only": True
            })

        # Process steps FAQ
        if claims.get("process_steps"):
            steps_list = "\n".join([f"{i+1}. {step}" for i, step in enumerate(claims["process_steps"])])
            faqs.append({
                "id": f"claims_process_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
                "category": "Claims Requirements",
                "insurer": insurer,
                "policy_type": policy_type,
                "question": f"What is the claims process for {insurer} {policy_type}?",
                "answer": f"Follow these steps to file a claim:\n\n{steps_list}",
                "tags": ["claims", "process", insurer.lower(), policy_type.lower()],
                "internal_only": True
            })

        # Evidence requirements FAQ
        if claims.get("evidence_requirements"):
            faqs.append({
                "id": f"claims_evidence_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
                "category": "Claims Requirements",
                "insurer": insurer,
                "policy_type": policy_type,
                "question": f"What evidence is needed for {insurer} {policy_type} claims?",
                "answer": claims["evidence_requirements"],
                "tags": ["claims", "evidence", "proof", insurer.lower(), policy_type.lower()],
                "internal_only": True
            })

    return faqs


def generate_eligibility_faqs(policies: List[Dict]) -> List[Dict]:
    """Generate FAQs about eligibility criteria."""
    faqs = []

    for policy in policies:
        insurer = policy.get("insurer_name", "Unknown")
        policy_type = policy.get("policy_type", "Unknown")
        eligibility = policy.get("eligibility_criteria", {})

        if not eligibility:
            continue

        # Age limits FAQ
        if eligibility.get("age_limits"):
            faqs.append({
                "id": f"eligibility_age_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
                "category": "Eligibility",
                "insurer": insurer,
                "policy_type": policy_type,
                "question": f"What are the age requirements for {insurer} {policy_type}?",
                "answer": eligibility["age_limits"],
                "tags": ["eligibility", "age", insurer.lower(), policy_type.lower()],
                "internal_only": True
            })

        # Medical restrictions FAQ
        if eligibility.get("medical_restrictions"):
            faqs.append({
                "id": f"eligibility_medical_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
                "category": "Eligibility",
                "insurer": insurer,
                "policy_type": policy_type,
                "question": f"What medical restrictions apply to {insurer} {policy_type}?",
                "answer": eligibility["medical_restrictions"],
                "tags": ["eligibility", "medical", "health", insurer.lower(), policy_type.lower()],
                "internal_only": True
            })

        # Occupational restrictions FAQ
        if eligibility.get("occupational_restrictions"):
            faqs.append({
                "id": f"eligibility_occupation_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
                "category": "Eligibility",
                "insurer": insurer,
                "policy_type": policy_type,
                "question": f"Are there occupational restrictions for {insurer} {policy_type}?",
                "answer": eligibility["occupational_restrictions"],
                "tags": ["eligibility", "occupation", "profession", insurer.lower(), policy_type.lower()],
                "internal_only": True
            })

        # Residency requirements FAQ
        if eligibility.get("residency_requirements"):
            faqs.append({
                "id": f"eligibility_residency_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
                "category": "Eligibility",
                "insurer": insurer,
                "policy_type": policy_type,
                "question": f"What are the residency requirements for {insurer} {policy_type}?",
                "answer": eligibility["residency_requirements"],
                "tags": ["eligibility", "residency", insurer.lower(), policy_type.lower()],
                "internal_only": True
            })

    return faqs


def generate_definitions_faqs(policies: List[Dict]) -> List[Dict]:
    """Generate FAQs about policy term definitions."""
    faqs = []

    for policy in policies:
        insurer = policy.get("insurer_name", "Unknown")
        policy_type = policy.get("policy_type", "Unknown")
        definitions = policy.get("policy_definitions", {})

        if not definitions:
            continue

        # Individual definition FAQs
        for term, definition in definitions.items():
            faqs.append({
                "id": f"definition_{term.lower().replace(' ', '_')}_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}",
                "category": "Policy Definitions",
                "insurer": insurer,
                "policy_type": policy_type,
                "question": f"How does {insurer} {policy_type} define '{term}'?",
                "answer": definition,
                "tags": ["definitions", term.lower().replace(" ", "-"), insurer.lower(), policy_type.lower()],
                "internal_only": True
            })

    return faqs


def generate_all_faqs():
    """Generate all FAQ entries and save to JSON file."""

    if not ANTHROPIC_API_KEY:
        print("Warning: ANTHROPIC_API_KEY not set. Proceeding with basic FAQ generation.")

    # Ensure directories exist
    FAQ_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load processed policies
    policies = load_all_policies()

    if not policies:
        print(f"No processed policies found in {PROCESSED_POLICIES_DIR}")
        print("Please run parse_policies.py first.")
        return

    print(f"Loaded {len(policies)} processed policy document(s)\n")
    print("Generating FAQs...")

    # Generate different types of FAQs
    all_faqs = []

    print("  - Generating exclusion FAQs...")
    all_faqs.extend(generate_exclusion_faqs(policies))

    print("  - Generating coverage limit FAQs...")
    all_faqs.extend(generate_coverage_limit_faqs(policies))

    print("  - Generating comparison FAQs...")
    all_faqs.extend(generate_comparison_faqs(policies))

    print("  - Generating endorsement FAQs...")
    all_faqs.extend(generate_endorsement_faqs(policies))

    print("  - Generating claims requirement FAQs...")
    all_faqs.extend(generate_claims_faqs(policies))

    print("  - Generating eligibility FAQs...")
    all_faqs.extend(generate_eligibility_faqs(policies))

    print("  - Generating policy definition FAQs...")
    all_faqs.extend(generate_definitions_faqs(policies))

    # Add policy-specific common questions
    print("  - Adding policy-specific questions...")
    for policy in policies:
        insurer = policy.get("insurer_name", "Unknown")
        policy_type = policy.get("policy_type", "Unknown")
        common_qs = policy.get("common_questions", [])

        for idx, q_item in enumerate(common_qs):
            all_faqs.append({
                "id": f"common_{insurer.lower().replace(' ', '_')}_{policy_type.lower().replace(' ', '_')}_{idx}",
                "category": "Common Questions",
                "insurer": insurer,
                "policy_type": policy_type,
                "question": q_item.get("question", ""),
                "answer": q_item.get("answer", ""),
                "section_reference": q_item.get("section_reference", ""),
                "tags": ["common", insurer.lower(), policy_type.lower()],
                "internal_only": True
            })

    # Save all FAQs
    output_file = FAQ_OUTPUT_DIR / "internal_faqs.json"
    with open(output_file, "w") as f:
        json.dump({
            "generated_date": str(Path().stat().st_mtime if Path().exists() else ""),
            "total_faqs": len(all_faqs),
            "faqs": all_faqs
        }, f, indent=2)

    print(f"\n✓ Generated {len(all_faqs)} FAQ entries")
    print(f"✓ Saved to: {output_file}")

    # Generate summary by category
    categories = {}
    for faq in all_faqs:
        cat = faq.get("category", "Other")
        categories[cat] = categories.get(cat, 0) + 1

    print("\nFAQ Breakdown by Category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    generate_all_faqs()
