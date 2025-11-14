#!/usr/bin/env python3
"""
FCA Compliance Report Generator
Creates compliance-focused reports from processed policy data for regulatory review.
"""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime


PROCESSED_POLICIES_DIR = Path(__file__).parent.parent.parent / "policy-wordings" / "processed"
COMPLIANCE_OUTPUT_DIR = Path(__file__).parent.parent / "data" / "compliance"


def load_all_policies() -> List[Dict]:
    """Load all processed policy JSON files."""
    policies = []
    for json_file in PROCESSED_POLICIES_DIR.glob("*.json"):
        with open(json_file, "r") as f:
            policies.append(json.loads(f.read()))
    return policies


def generate_fca_disclosure_report(policies: List[Dict]) -> str:
    """Generate report of FCA disclosures across all policies."""
    report = []
    report.append("=" * 80)
    report.append("FCA DISCLOSURE COMPLIANCE REPORT")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")

    for policy in policies:
        insurer = policy.get("insurer_name", "Unknown")
        policy_type = policy.get("policy_type", "Unknown")
        compliance = policy.get("regulatory_compliance", {})

        report.append(f"\n{insurer} - {policy_type}")
        report.append("-" * 80)

        # FCA Disclosures
        fca_disclosures = compliance.get("fca_disclosures", [])
        if fca_disclosures:
            report.append("\nFCA Required Disclosures:")
            for idx, disclosure in enumerate(fca_disclosures, 1):
                report.append(f"  {idx}. {disclosure}")
        else:
            report.append("\n⚠️  WARNING: No FCA disclosures found in policy document")

        # IPID Information
        ipid = compliance.get("ipid_key_info")
        if ipid:
            report.append(f"\nIPID Key Information: {ipid}")
        else:
            report.append("\n⚠️  WARNING: No IPID information found")

        # Fair Treatment Obligations
        fair_treatment = compliance.get("fair_treatment_obligations")
        if fair_treatment:
            report.append(f"\nFair Treatment Obligations: {fair_treatment}")

        # Complaints Process
        complaints = compliance.get("complaints_process")
        if complaints:
            report.append(f"\nComplaints Process: {complaints}")
        else:
            report.append("\n⚠️  WARNING: No complaints process documented (FCA requirement)")

        # Regulatory Warnings
        warnings = compliance.get("regulatory_warnings", [])
        if warnings:
            report.append("\nRegulatory Warnings:")
            for warning in warnings:
                report.append(f"  • {warning}")

        report.append("")

    return "\n".join(report)


def generate_exclusions_compliance_report(policies: List[Dict]) -> str:
    """Generate report focusing on exclusions that may have regulatory implications."""
    report = []
    report.append("=" * 80)
    report.append("EXCLUSIONS COMPLIANCE REVIEW")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")
    report.append("This report highlights exclusions that may require specific disclosure")
    report.append("or customer communication under FCA guidelines.")
    report.append("")

    # Track common high-risk exclusions
    high_risk_terms = [
        "pre-existing",
        "pandemic",
        "mental health",
        "terrorism",
        "pregnancy",
        "war",
        "alcohol",
        "drugs"
    ]

    for policy in policies:
        insurer = policy.get("insurer_name", "Unknown")
        policy_type = policy.get("policy_type", "Unknown")
        exclusions = policy.get("key_exclusions", [])

        report.append(f"\n{insurer} - {policy_type}")
        report.append("-" * 80)

        # Check for high-risk exclusions
        found_high_risk = []
        for term in high_risk_terms:
            matching = [e for e in exclusions if term.lower() in e.lower()]
            if matching:
                found_high_risk.append((term, matching))

        if found_high_risk:
            report.append("\nHigh-Impact Exclusions (Require Clear Disclosure):")
            for term, excl_list in found_high_risk:
                report.append(f"\n  {term.upper()}:")
                for excl in excl_list:
                    report.append(f"    • {excl}")
        else:
            report.append("\nNo high-impact exclusions identified.")

        # Total exclusion count
        report.append(f"\nTotal Exclusions: {len(exclusions)}")
        report.append("")

    return "\n".join(report)


def generate_eligibility_compliance_report(policies: List[Dict]) -> str:
    """Generate report on eligibility criteria that may have regulatory implications."""
    report = []
    report.append("=" * 80)
    report.append("ELIGIBILITY & DISCRIMINATION COMPLIANCE REVIEW")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")
    report.append("Review eligibility criteria for potential discrimination or fairness issues")
    report.append("under FCA fair treatment requirements.")
    report.append("")

    for policy in policies:
        insurer = policy.get("insurer_name", "Unknown")
        policy_type = policy.get("policy_type", "Unknown")
        eligibility = policy.get("eligibility_criteria", {})

        report.append(f"\n{insurer} - {policy_type}")
        report.append("-" * 80)

        if not eligibility:
            report.append("\n⚠️  WARNING: No eligibility criteria documented")
            continue

        # Age restrictions
        age_limits = eligibility.get("age_limits")
        if age_limits:
            report.append(f"\nAge Restrictions: {age_limits}")
            report.append("  → Ensure age restrictions are actuarially justified and clearly disclosed")

        # Medical restrictions
        medical = eligibility.get("medical_restrictions")
        if medical:
            report.append(f"\nMedical Restrictions: {medical}")
            report.append("  → Verify compliance with Equality Act and FCA guidance on health conditions")

        # Occupational restrictions
        occupation = eligibility.get("occupational_restrictions")
        if occupation:
            report.append(f"\nOccupational Restrictions: {occupation}")
            report.append("  → Ensure occupational restrictions are risk-based and justified")

        # Residency requirements
        residency = eligibility.get("residency_requirements")
        if residency:
            report.append(f"\nResidency Requirements: {residency}")

        report.append("")

    return "\n".join(report)


def generate_claims_process_compliance_report(policies: List[Dict]) -> str:
    """Generate report on claims processes for regulatory compliance."""
    report = []
    report.append("=" * 80)
    report.append("CLAIMS HANDLING COMPLIANCE REVIEW")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")
    report.append("Review claims processes for FCA fair treatment and timely handling requirements.")
    report.append("")

    for policy in policies:
        insurer = policy.get("insurer_name", "Unknown")
        policy_type = policy.get("policy_type", "Unknown")
        claims = policy.get("claims_requirements", {})

        report.append(f"\n{insurer} - {policy_type}")
        report.append("-" * 80)

        if not claims:
            report.append("\n⚠️  WARNING: No claims process documented")
            continue

        # Notification timeframe
        timeframe = claims.get("notification_timeframe")
        if timeframe:
            report.append(f"\nNotification Timeframe: {timeframe}")
            # Check if timeframe is reasonable
            if any(word in timeframe.lower() for word in ["immediately", "24 hours", "48 hours"]):
                report.append("  → ⚠️  Short timeframe - ensure customers are clearly informed")
        else:
            report.append("\n⚠️  No notification timeframe specified")

        # Required documents
        docs = claims.get("required_documents", [])
        if docs:
            report.append(f"\nRequired Documents ({len(docs)} items):")
            for doc in docs:
                report.append(f"  • {doc}")
            if len(docs) > 5:
                report.append("  → ⚠️  Many documents required - ensure process isn't overly burdensome")
        else:
            report.append("\n⚠️  No document requirements specified")

        # Process steps
        steps = claims.get("process_steps", [])
        if steps:
            report.append(f"\nClaims Process ({len(steps)} steps):")
            for idx, step in enumerate(steps, 1):
                report.append(f"  {idx}. {step}")
        else:
            report.append("\n⚠️  No process steps documented")

        report.append("")

    return "\n".join(report)


def generate_compliance_summary(policies: List[Dict]) -> str:
    """Generate executive summary of compliance status."""
    report = []
    report.append("=" * 80)
    report.append("REGULATORY COMPLIANCE SUMMARY")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")

    total_policies = len(policies)
    policies_with_fca = 0
    policies_with_complaints = 0
    policies_with_eligibility = 0
    policies_with_claims = 0

    for policy in policies:
        compliance = policy.get("regulatory_compliance", {})
        if compliance.get("fca_disclosures"):
            policies_with_fca += 1
        if compliance.get("complaints_process"):
            policies_with_complaints += 1
        if policy.get("eligibility_criteria"):
            policies_with_eligibility += 1
        if policy.get("claims_requirements"):
            policies_with_claims += 1

    report.append(f"Total Policies Reviewed: {total_policies}")
    report.append("")
    report.append("COMPLIANCE COVERAGE:")
    report.append(f"  FCA Disclosures:      {policies_with_fca}/{total_policies} ({policies_with_fca/total_policies*100:.0f}%)")
    report.append(f"  Complaints Process:   {policies_with_complaints}/{total_policies} ({policies_with_complaints/total_policies*100:.0f}%)")
    report.append(f"  Eligibility Criteria: {policies_with_eligibility}/{total_policies} ({policies_with_eligibility/total_policies*100:.0f}%)")
    report.append(f"  Claims Process:       {policies_with_claims}/{total_policies} ({policies_with_claims/total_policies*100:.0f}%)")
    report.append("")

    # Recommendations
    report.append("RECOMMENDATIONS:")
    if policies_with_fca < total_policies:
        report.append("  ⚠️  Not all policies have documented FCA disclosures")
    if policies_with_complaints < total_policies:
        report.append("  ⚠️  Not all policies have documented complaints processes (FCA requirement)")
    if policies_with_eligibility < total_policies:
        report.append("  ⚠️  Some policies lack eligibility criteria documentation")
    if policies_with_claims < total_policies:
        report.append("  ⚠️  Some policies lack claims process documentation")

    if policies_with_fca == total_policies and policies_with_complaints == total_policies:
        report.append("  ✓ All policies have core FCA compliance documentation")

    report.append("")
    report.append("NEXT STEPS:")
    report.append("  1. Review detailed reports for each compliance area")
    report.append("  2. Address any warnings or missing information")
    report.append("  3. Ensure all customer-facing materials reflect policy terms accurately")
    report.append("  4. Regular review schedule for policy updates and regulatory changes")

    return "\n".join(report)


def generate_all_compliance_reports():
    """Generate all compliance reports."""
    print("=" * 60)
    print("Generating Compliance Reports")
    print("=" * 60)
    print()

    # Load policies
    policies = load_all_policies()

    if not policies:
        print(f"No processed policies found in {PROCESSED_POLICIES_DIR}")
        print("Please run parse_policies.py first.")
        return

    print(f"Loaded {len(policies)} policy document(s)\n")

    # Ensure output directory exists
    COMPLIANCE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate reports
    reports = {
        "compliance_summary.txt": generate_compliance_summary(policies),
        "fca_disclosures.txt": generate_fca_disclosure_report(policies),
        "exclusions_compliance.txt": generate_exclusions_compliance_report(policies),
        "eligibility_compliance.txt": generate_eligibility_compliance_report(policies),
        "claims_compliance.txt": generate_claims_process_compliance_report(policies)
    }

    # Save reports
    for filename, content in reports.items():
        output_file = COMPLIANCE_OUTPUT_DIR / filename
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Generated: {filename}")

    print(f"\n{'=' * 60}")
    print("Compliance reports saved to:")
    print(f"  {COMPLIANCE_OUTPUT_DIR}")
    print("=" * 60)
    print("\nREVIEW PRIORITY:")
    print("  1. compliance_summary.txt - Start here for overview")
    print("  2. fca_disclosures.txt - Core regulatory requirements")
    print("  3. exclusions_compliance.txt - Customer communication focus")
    print("  4. eligibility_compliance.txt - Fair treatment review")
    print("  5. claims_compliance.txt - Process fairness review")


if __name__ == "__main__":
    generate_all_compliance_reports()
