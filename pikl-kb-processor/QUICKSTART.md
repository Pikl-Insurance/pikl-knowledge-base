# Quick Start Guide

Get up and running in 5 minutes!

## 1. Setup (2 minutes)

```bash
cd pikl-kb-processor
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create necessary directories
- Generate .env file

## 2. Configure API Keys (1 minute)

Edit `.env` and add your keys:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
INTERCOM_ACCESS_TOKEN=dG9rxxxxx
```

### Getting API Keys

**Anthropic (Claude)**:
1. Go to https://console.anthropic.com/
2. Create account or sign in
3. Go to API Keys
4. Create a new key

**Intercom**:
1. Go to your Intercom workspace
2. Settings > Developers > Developer Hub
3. Create app or use existing
4. Add "Read articles" permission
5. Copy access token

## 3. Test Connection (30 seconds)

```bash
source venv/bin/activate
python cli.py test-intercom
```

You should see: ✓ Intercom API connection successful

## 4. Fetch Your Knowledge Base (1 minute)

```bash
python cli.py fetch-kb
```

This downloads all your Intercom help articles.

## 5. Process Your Data

### Option A: Test with Example (30 seconds)

```bash
python cli.py process \
  --kb-articles ./data/kb_articles.json \
  --transcripts ./examples \
  --output ./reports_test \
  --no-generate-faqs
```

Quick test to verify everything works.

### Option B: Full Processing

First, prepare your data:
- Put transcript JSON/CSV files in `data/transcripts/`
- Put EML email files in `data/emails/`

Then run:

```bash
python cli.py process \
  --kb-articles ./data/kb_articles.json \
  --transcripts ./data/transcripts \
  --emails ./data/emails \
  --output ./reports
```

This will:
- Extract questions from transcripts/emails
- Match them to your KB
- Identify gaps
- Generate FAQ candidates

Processing time: ~5-10 minutes per 100 calls

## 6. Review Results

Open `reports/report.md` to see:
- Summary statistics
- High-priority knowledge gaps
- Generated FAQ candidates
- Recommendations

Also check:
- `reports/knowledge_gaps.csv` - All gaps in spreadsheet format
- `reports/faq_candidates.csv` - FAQs ready for review

## Common Commands

```bash
# Test Intercom connection
python cli.py test-intercom

# Fetch KB articles
python cli.py fetch-kb --output ./data/kb_articles.json

# Process everything
python cli.py process \
  --kb-articles ./data/kb_articles.json \
  --transcripts ./data/transcripts \
  --emails ./data/emails

# Just identify gaps (faster, no FAQ generation)
python cli.py process \
  --kb-articles ./data/kb_articles.json \
  --transcripts ./data/transcripts \
  --no-generate-faqs

# Generate FAQs from existing gaps
python cli.py generate-faqs-only \
  --gaps ./reports/knowledge_gaps.csv \
  --limit 10

# Publish FAQs to Intercom as drafts
python cli.py publish-to-intercom \
  --faqs ./reports/faq_candidates.json \
  --limit 5

# Publish FAQs to Intercom immediately (published)
python cli.py publish-to-intercom \
  --faqs ./reports/faq_candidates.json \
  --publish

# Help
python cli.py --help
```

## Troubleshooting

**"Command not found"**: Did you activate the virtual environment?
```bash
source venv/bin/activate
```

**"API key not set"**: Check your `.env` file has the correct keys

**"No transcript files found"**: Verify your files are in the right directory and have correct extensions (.json, .jsonl, .csv)

**"Failed to parse LLM response"**: Usually temporary. The tool will skip and continue. Check your API quota if it happens frequently.

## Next Steps

1. ✅ Process a small sample first (10-20 files)
2. ✅ Review the quality of extracted questions and FAQs
3. ✅ Adjust similarity threshold in `.env` if needed
4. ✅ Process your full dataset
5. ✅ Review and approve FAQ candidates
6. ✅ Publish to your Intercom KB

## Full Documentation

- **[README.md](README.md)**: Full project documentation
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)**: Comprehensive usage guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**: Technical overview

## Support

Having issues? Check:
1. API keys are correct in `.env`
2. Virtual environment is activated
3. All dependencies installed (`pip install -r requirements.txt`)
4. File formats match expected structure
5. You have API quota remaining

Still stuck? Review the error message carefully - it usually tells you exactly what's wrong!
