# Policy Wordings Directory

This directory contains insurance policy wordings from various insurers used by Pikl.

## Structure

- `raw/` - Original policy PDF files from insurers
- `processed/` - Extracted and structured policy data

## How to Add Policy Documents

1. Place PDF files in the `raw/` directory
2. Name files using the format: `[InsurerId]_[PolicyType]_[Version].pdf`
   - Example: `AXA_Travel_v2.1.pdf`
   - Example: `Zurich_Home_2024.pdf`

## Processing

Once documents are added, run the processing script to extract structured data:
```bash
python faq-system/scripts/parse_policies.py
```

This will extract key information and store it in `processed/` for FAQ generation.
