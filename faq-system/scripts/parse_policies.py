#!/usr/bin/env python3
"""
Policy Wording Parser
Extracts structured information from insurance policy PDF documents using Claude AI.
"""

import os
import json
import anthropic
from pathlib import Path
import base64
from typing import Dict, List, Optional

# Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
RAW_POLICIES_DIR = Path(__file__).parent.parent.parent / "policy-wordings" / "raw"
PROCESSED_POLICIES_DIR = Path(__file__).parent.parent.parent / "policy-wordings" / "processed"


def extract_policy_info(pdf_path: Path) -> Dict:
    """
    Extract structured information from a policy PDF using Claude.

    Args:
        pdf_path: Path to the policy PDF file

    Returns:
        Dictionary containing structured policy information
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Read PDF as base64
    with open(pdf_path, "rb") as f:
        pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

    # Prompt Claude to extract structured information
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=16000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": """Analyze this insurance policy document and extract the following information in JSON format:

{
  "insurer_name": "Name of the insurance company",
  "policy_type": "Type of insurance (e.g., Travel, Home, Motor, etc.)",
  "policy_version": "Version or effective date",
  "coverage_summary": "Brief summary of what this policy covers",
  "key_inclusions": [
    "List of main things covered"
  ],
  "key_exclusions": [
    "List of main exclusions - things NOT covered"
  ],
  "coverage_limits": {
    "category": "limit amount and description"
  },
  "sub_limits": {
    "category": "specific per-item or per-event limits within main coverage"
  },
  "special_conditions": [
    "Any important conditions or requirements"
  ],
  "excess_deductible": "Information about excess/deductible amounts",
  "geographical_coverage": "Where the policy is valid",
  "age_restrictions": "Any age-related restrictions or requirements",
  "pre_existing_conditions": "Policy on pre-existing conditions (if applicable)",
  "cancellation_policy": "Cancellation terms",
  "endorsements": [
    {
      "name": "Name of endorsement/modification",
      "description": "What it adds, removes, or modifies",
      "cost_impact": "How it affects premium (if mentioned)",
      "coverage_impact": "How it changes coverage or exclusions"
    }
  ],
  "claims_requirements": {
    "notification_timeframe": "How quickly must claims be reported",
    "required_documents": [
      "List of documents needed to file a claim"
    ],
    "process_steps": [
      "Step-by-step claims process"
    ],
    "evidence_requirements": "What evidence/proof is needed (police reports, receipts, etc.)",
    "claims_contact": "How to contact for claims"
  },
  "eligibility_criteria": {
    "age_limits": "Age requirements or restrictions",
    "medical_restrictions": "Medical conditions that affect eligibility",
    "occupational_restrictions": "Jobs or professions that are restricted",
    "residency_requirements": "Where customer must be resident",
    "other_restrictions": [
      "Any other eligibility restrictions"
    ]
  },
  "policy_definitions": {
    "term": "definition - Include important terms that often cause confusion, such as: immediate family, pre-existing condition, extreme sports, valuables, etc."
  },
  "time_sensitive_requirements": {
    "waiting_periods": "Time before coverage starts",
    "notification_deadlines": "Deadlines for notifying insurer of events",
    "claims_deadlines": "Time limits for filing claims",
    "cooling_off_period": "Period to cancel without penalty"
  },
  "regulatory_compliance": {
    "fca_disclosures": [
      "FCA-required disclosures or statements"
    ],
    "ipid_key_info": "Key information from IPID (Insurance Product Information Document)",
    "fair_treatment_obligations": "Customer fair treatment requirements",
    "complaints_process": "How customers can complain (FCA requirement)",
    "regulatory_warnings": [
      "Required regulatory warnings or notices"
    ]
  },
  "common_questions": [
    {
      "question": "Common question about this policy",
      "answer": "Answer based on the policy document",
      "section_reference": "Which section of the policy this comes from"
    }
  ]
}

Be thorough and extract ALL relevant information in these categories:
- EXCLUSIONS are critical - list every exclusion mentioned
- ENDORSEMENTS - all available modifications to the base policy
- CLAIMS REQUIREMENTS - complete documentation and process details
- ELIGIBILITY - all restrictions on who can get this policy
- DEFINITIONS - key terms that agents need to understand
- REGULATORY - all FCA compliance and regulatory requirements

Focus on information that would help agents answer customer questions accurately and comply with regulations."""
                    }
                ],
            }
        ],
    )

    # Parse the JSON response
    response_text = message.content[0].text

    # Extract JSON from response (handle markdown code blocks)
    if "```json" in response_text:
        json_str = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        json_str = response_text.split("```")[1].split("```")[0].strip()
    else:
        json_str = response_text.strip()

    return json.loads(json_str)


def process_all_policies():
    """Process all PDF files in the raw policies directory."""

    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return

    # Ensure directories exist
    RAW_POLICIES_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_POLICIES_DIR.mkdir(parents=True, exist_ok=True)

    # Find all PDF files
    pdf_files = list(RAW_POLICIES_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {RAW_POLICIES_DIR}")
        print("Please add policy PDF files to the directory and try again.")
        return

    print(f"Found {len(pdf_files)} policy document(s) to process\n")

    for pdf_path in pdf_files:
        # Check if already processed
        output_file = PROCESSED_POLICIES_DIR / f"{pdf_path.stem}.json"
        if output_file.exists():
            print(f"Skipping (already processed): {pdf_path.name}")
            continue

        print(f"Processing: {pdf_path.name}...")

        try:
            # Extract policy information
            policy_data = extract_policy_info(pdf_path)

            # Add metadata
            policy_data["source_file"] = pdf_path.name
            policy_data["processed_date"] = str(Path(pdf_path).stat().st_mtime)

            # Save to processed directory
            output_file = PROCESSED_POLICIES_DIR / f"{pdf_path.stem}.json"
            with open(output_file, "w") as f:
                json.dump(policy_data, f, indent=2)

            print(f"  ✓ Saved to: {output_file.name}")
            print(f"  ✓ Exclusions: {len(policy_data.get('key_exclusions', []))}")
            print(f"  ✓ Endorsements: {len(policy_data.get('endorsements', []))}")
            print(f"  ✓ Policy definitions: {len(policy_data.get('policy_definitions', {}))}")
            print(f"  ✓ Common questions: {len(policy_data.get('common_questions', []))}")

            # Show claims and eligibility info
            if policy_data.get('claims_requirements'):
                docs = len(policy_data['claims_requirements'].get('required_documents', []))
                print(f"  ✓ Claims documents required: {docs}")

            if policy_data.get('regulatory_compliance'):
                fca = len(policy_data['regulatory_compliance'].get('fca_disclosures', []))
                if fca > 0:
                    print(f"  ✓ FCA disclosures: {fca}")

            print()

        except Exception as e:
            print(f"  ✗ Error processing {pdf_path.name}: {str(e)}\n")
            continue

    print("Processing complete!")
    print(f"Processed files saved to: {PROCESSED_POLICIES_DIR}")


if __name__ == "__main__":
    process_all_policies()
