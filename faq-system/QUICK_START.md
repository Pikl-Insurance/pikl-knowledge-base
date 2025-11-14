# Quick Start Guide

Get your internal FAQ system running in 5 minutes.

## Prerequisites

- Python 3.7 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))
- Policy PDF documents

## Setup (One-Time)

```bash
# 1. Install dependencies
cd faq-system
pip install -r requirements.txt

# 2. Set your API key
export ANTHROPIC_API_KEY='your-api-key-here'

# 3. Add your policy PDFs
# Copy PDF files to: policy-wordings/raw/
```

## Three Simple Steps

### 1. Parse Your Policies

```bash
cd scripts
python parse_policies.py
```

This reads your PDFs and extracts all the important information using Claude AI.

### 2. Generate FAQs

```bash
python generate_faqs.py
```

This creates hundreds of pre-written FAQs based on your policies.

### 3. Search or Export

**Option A: Search with AI**
```bash
python ai_search.py
# Then ask questions like: "Does AXA exclude pre-existing conditions?"
```

**Option B: Export to Intercom**
```bash
python export_for_intercom.py
# Then import the CSV/JSON files into Intercom
```

## Done!

You now have:
- ✓ Structured policy data
- ✓ Hundreds of pre-generated FAQs
- ✓ AI-powered search capability
- ✓ Intercom-ready exports

## Need Help?

See the full [README.md](README.md) for detailed documentation.

## Example Workflow

```bash
# Complete workflow
cd faq-system/scripts

# Step 1: Process policies
python parse_policies.py

# Step 2: Generate FAQs
python generate_faqs.py

# Step 3: Try a search
python ai_search.py "What does Zurich travel insurance exclude?"

# Step 4: Export for Intercom
python export_for_intercom.py
```

## Common Questions

**Q: How many policies can I process?**
A: As many as you want! Each policy takes about 30-60 seconds to process.

**Q: Do I need to re-run everything when I add new policies?**
A: Yes, run steps 1-2 again. The system will process only new/updated files.

**Q: Can I use this without Intercom?**
A: Yes! Use the AI search tool directly, or integrate the JSON exports with your own system.

**Q: How accurate is the information?**
A: Claude extracts information very accurately, but always spot-check critical details against source documents.
