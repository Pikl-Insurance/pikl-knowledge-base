#!/usr/bin/env python3
"""
FAQ Coverage Analysis
Analyzes how well the generated FAQs cover the policy information.
"""

import json
from pathlib import Path
from typing import List, Dict
from collections import defaultdict


PROCESSED_POLICIES_DIR = Path(__file__).parent.parent.parent / "policy-wordings" / "processed"
FAQ_DATA_FILE = Path(__file__).parent.parent / "data" / "internal_faqs.json"


def load_all_policies() -> List[Dict]:
    """Load all processed policy JSON files."""
    policies = []
    for json_file in PROCESSED_POLICIES_DIR.glob("*.json"):
        with open(json_file, "r") as f:
            policies.append(json.loads(f.read()))
    return policies


def load_faqs() -> List[Dict]:
    """Load generated FAQs."""
    if not FAQ_DATA_FILE.exists():
        return []

    with open(FAQ_DATA_FILE, "r") as f:
        data = json.load(f)
        return data.get("faqs", [])


def analyze_coverage(policies: List[Dict], faqs: List[Dict]) -> Dict:
    """Analyze FAQ coverage of policy information."""

    # Track coverage by category
    coverage = {
        "exclusions": {"has_data": 0, "has_faqs": 0},
        "claims_requirements": {"has_data": 0, "has_faqs": 0},
        "eligibility": {"has_data": 0, "has_faqs": 0},
        "endorsements": {"has_data": 0, "has_faqs": 0},
        "definitions": {"has_data": 0, "has_faqs": 0},
        "coverage_limits": {"has_data": 0, "has_faqs": 0},
        "common_questions": {"has_data": 0, "has_faqs": 0},
        "comparisons": {"has_data": 0, "has_faqs": 0}
    }

    # Track FAQs by category
    faqs_by_category = defaultdict(list)
    for faq in faqs:
        category = faq.get("category", "Other")
        faqs_by_category[category].append(faq)

    # Track FAQs by insurer and policy type
    faqs_by_insurer = defaultdict(list)
    for faq in faqs:
        insurer = faq.get("insurer", "Unknown")
        faqs_by_insurer[insurer].append(faq)

    # Analyze each policy
    for policy in policies:
        insurer = policy.get("insurer_name", "Unknown")

        # Check exclusions
        if policy.get("key_exclusions"):
            coverage["exclusions"]["has_data"] += 1
            if any(faq.get("insurer") == insurer and "Exclusions" in faq.get("category", "")
                   for faq in faqs):
                coverage["exclusions"]["has_faqs"] += 1

        # Check claims requirements
        if policy.get("claims_requirements"):
            coverage["claims_requirements"]["has_data"] += 1
            if any(faq.get("insurer") == insurer and "Claims Requirements" in faq.get("category", "")
                   for faq in faqs):
                coverage["claims_requirements"]["has_faqs"] += 1

        # Check eligibility
        if policy.get("eligibility_criteria"):
            coverage["eligibility"]["has_data"] += 1
            if any(faq.get("insurer") == insurer and "Eligibility" in faq.get("category", "")
                   for faq in faqs):
                coverage["eligibility"]["has_faqs"] += 1

        # Check endorsements
        if policy.get("endorsements"):
            coverage["endorsements"]["has_data"] += 1
            if any(faq.get("insurer") == insurer and "Endorsements" in faq.get("category", "")
                   for faq in faqs):
                coverage["endorsements"]["has_faqs"] += 1

        # Check definitions
        if policy.get("key_definitions"):
            coverage["definitions"]["has_data"] += 1
            if any(faq.get("insurer") == insurer and "Definitions" in faq.get("category", "")
                   for faq in faqs):
                coverage["definitions"]["has_faqs"] += 1

        # Check coverage limits
        if policy.get("coverage_limits"):
            coverage["coverage_limits"]["has_data"] += 1
            if any(faq.get("insurer") == insurer and "Coverage Limits" in faq.get("category", "")
                   for faq in faqs):
                coverage["coverage_limits"]["has_faqs"] += 1

    return {
        "coverage": coverage,
        "faqs_by_category": dict(faqs_by_category),
        "faqs_by_insurer": dict(faqs_by_insurer)
    }


def print_coverage_report(policies: List[Dict], faqs: List[Dict]):
    """Print comprehensive coverage analysis."""

    analysis = analyze_coverage(policies, faqs)
    coverage = analysis["coverage"]
    faqs_by_category = analysis["faqs_by_category"]
    faqs_by_insurer = analysis["faqs_by_insurer"]

    print("=" * 80)
    print("FAQ COVERAGE ANALYSIS")
    print("=" * 80)
    print()

    # Overall statistics
    print("OVERALL STATISTICS")
    print("-" * 80)
    print(f"Total Policies: {len(policies)}")
    print(f"Total FAQs Generated: {len(faqs)}")
    print()

    # Insurers covered
    insurers = set(p.get("insurer_name") for p in policies if p.get("insurer_name"))
    insurers_with_faqs = set(faqs_by_insurer.keys())
    print(f"Insurers in Policies: {len(insurers)}")
    print(f"Insurers with FAQs: {len(insurers_with_faqs)}")
    print()

    # Coverage by category
    print("COVERAGE BY CATEGORY")
    print("-" * 80)
    print(f"{'Category':<30} {'Policies':<12} {'FAQs':<12} {'Coverage':<12}")
    print("-" * 80)

    total_data_points = 0
    total_covered = 0

    for category, data in coverage.items():
        has_data = data["has_data"]
        has_faqs = data["has_faqs"]

        if has_data > 0:
            coverage_pct = (has_faqs / has_data) * 100
            total_data_points += has_data
            total_covered += has_faqs
        else:
            coverage_pct = 0

        category_display = category.replace("_", " ").title()
        print(f"{category_display:<30} {has_data:<12} {has_faqs:<12} {coverage_pct:>6.1f}%")

    print("-" * 80)
    if total_data_points > 0:
        overall_coverage = (total_covered / total_data_points) * 100
        print(f"{'OVERALL COVERAGE':<30} {total_data_points:<12} {total_covered:<12} {overall_coverage:>6.1f}%")
    print()

    # FAQ breakdown by category
    print("FAQ BREAKDOWN BY CATEGORY")
    print("-" * 80)
    for category in sorted(faqs_by_category.keys()):
        count = len(faqs_by_category[category])
        pct = (count / len(faqs)) * 100
        print(f"{category:<40} {count:>6} ({pct:>5.1f}%)")
    print()

    # FAQ breakdown by insurer
    print("FAQ BREAKDOWN BY INSURER")
    print("-" * 80)
    for insurer in sorted(faqs_by_insurer.keys()):
        count = len(faqs_by_insurer[insurer])
        pct = (count / len(faqs)) * 100
        print(f"{insurer:<50} {count:>6} ({pct:>5.1f}%)")
    print()

    # Recommendations
    print("RECOMMENDATIONS")
    print("-" * 80)

    low_coverage_categories = []
    for category, data in coverage.items():
        if data["has_data"] > 0:
            coverage_pct = (data["has_faqs"] / data["has_data"]) * 100
            if coverage_pct < 80:
                low_coverage_categories.append((category, coverage_pct))

    if low_coverage_categories:
        print("⚠️  The following categories have low coverage (<80%):")
        for category, pct in sorted(low_coverage_categories, key=lambda x: x[1]):
            category_display = category.replace("_", " ").title()
            print(f"  • {category_display}: {pct:.1f}%")
        print()
        print("Consider generating additional FAQs for these categories.")
    else:
        print("✓ All categories have good coverage (≥80%)")

    print()

    # Missing insurers
    missing_insurers = insurers - insurers_with_faqs
    if missing_insurers:
        print("⚠️  The following insurers have no FAQs generated:")
        for insurer in sorted(missing_insurers):
            print(f"  • {insurer}")
        print()

    print("=" * 80)
    print()


def main():
    """Main entry point."""
    print()
    print("Loading policies and FAQs...")

    policies = load_all_policies()
    if not policies:
        print(f"❌ No processed policies found in {PROCESSED_POLICIES_DIR}")
        print("Please run parse_policies.py first.")
        return

    faqs = load_faqs()
    if not faqs:
        print(f"❌ No FAQs found in {FAQ_DATA_FILE}")
        print("Please run generate_faqs.py first.")
        return

    print(f"✓ Loaded {len(policies)} policies")
    print(f"✓ Loaded {len(faqs)} FAQs")
    print()

    print_coverage_report(policies, faqs)


if __name__ == "__main__":
    main()
