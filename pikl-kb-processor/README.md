# Pikl KB Processor

A powerful tool for processing customer call transcripts and emails to enhance your knowledge base using AI-powered analysis. Available in both **CLI** and **Web UI** interfaces.

## What It Does

This tool analyzes customer interactions (calls and emails) to:
- **Extract questions** customers are asking using Claude AI
- **Match questions** to your existing Intercom KB articles using semantic similarity
- **Identify knowledge gaps** where your KB doesn't adequately cover customer questions
- **Generate FAQ candidates** with AI to fill those gaps
- **Publish directly to Intercom** - automatically create help articles (NEW!)
- **Provide actionable reports** with priorities and recommendations

## Why Use This?

- 📊 **Data-Driven KB Development**: Let actual customer questions guide your content strategy
- 🎯 **Prioritization**: Focus on high-impact gaps first using AI-calculated priority scores
- ⚡ **Automation**: Process hundreds of calls/emails in minutes instead of manual review
- 📈 **Measurable Coverage**: Track what % of customer questions your KB answers well
- 💡 **Smart Recommendations**: Get AI-generated FAQ drafts ready for review
- 🛡️ **Privacy-First**: Automatic PII anonymization protects customer data

## Quick Start

**New to this tool?** Start with **[QUICKSTART.md](QUICKSTART.md)** for a 5-minute setup guide!

### Option 1: Web UI (Recommended for Teams)

**See [UI_QUICK_START.md](UI_QUICK_START.md) for a 2-minute guided setup!**

```bash
# Quick launch (easiest)
cd pikl-kb-processor
./start_ui.sh

# Or manually
source venv/bin/activate
streamlit run app.py

# Opens at http://localhost:8501
```

**Features:** Visual dashboard, drag-and-drop uploads, FAQ review workflow, one-click publishing to Intercom, analytics charts. Perfect for teams!

### Option 2: Command Line Interface

```bash
# 1. Setup (automated)
cd pikl-kb-processor
./setup.sh

# 2. Configure API keys
# Edit .env.local and add your ANTHROPIC_API_KEY and INTERCOM_ACCESS_TOKEN

# 3. Activate environment
source venv/bin/activate

# 4. Test connection
python cli.py test-intercom

# 5. Fetch your KB
python cli.py fetch-kb

# 6. Process your data
python cli.py process \
  --kb-articles ./data/kb_articles.json \
  --transcripts ./data/transcripts \
  --emails ./data/emails

# 7. Review reports in ./reports/
```

## Documentation

### Getting Started
- **[UI_QUICK_START.md](UI_QUICK_START.md)**: 2-minute Web UI quick start (NEW! ⭐)
- **[QUICKSTART.md](QUICKSTART.md)**: 5-minute CLI setup guide

### User Guides
- **[UI_GUIDE.md](UI_GUIDE.md)**: Complete Web UI user guide with workflows
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)**: Comprehensive CLI usage guide with examples

### Reference
- **[INTERCOM_PUBLISHING.md](INTERCOM_PUBLISHING.md)**: Guide to publishing FAQs directly to Intercom
- **[PII_ANONYMIZATION.md](PII_ANONYMIZATION.md)**: Privacy & PII anonymization (IMPORTANT!)
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**: Technical overview and architecture
- **[CLI Reference](#cli-reference)**: Full CLI command reference below

## Architecture

```
pikl-kb-processor/
├── ingest/          # Data ingestion
│   ├── intercom.py     # Fetch KB articles from Intercom API
│   ├── emails.py       # Parse EML/MSG email files
│   └── transcripts.py  # Parse JSON/CSV call transcripts
├── analyze/         # Analysis engines
│   ├── extractor.py    # Extract Q&A using Claude
│   ├── matcher.py      # Semantic similarity matching
│   └── gaps.py         # Gap identification & prioritization
├── generate/        # Content generation
│   └── faqs.py         # Generate FAQ candidates using Claude
├── output/          # Reporting
│   └── reports.py      # Generate reports in multiple formats
├── anonymize.py     # PII anonymization
├── config.py        # Configuration management
├── models.py        # Data models (Pydantic)
├── app.py           # Streamlit Web UI (NEW!)
└── cli.py           # CLI interface
```

## Web UI Features

The Streamlit-based Web UI provides a visual, team-friendly interface with:

### 📊 Dashboard
- Real-time metrics overview (KB articles, gaps, coverage %)
- System health status
- Recent activity feed
- Quick access to all features

### 📥 Data Ingestion
- Visual file upload for transcripts and emails
- One-click Intercom KB fetching
- Live processing progress with logs
- Processing status indicators

### 🔍 Knowledge Gaps Analysis
- Filterable and sortable gap list
- Priority indicators (High/Medium/Low)
- Theme-based grouping
- Search functionality
- Export options

### ✏️ FAQ Review & Approval
- Side-by-side FAQ review interface
- Approve/Edit/Reject workflow
- Batch actions for multiple FAQs
- In-app editing capabilities
- Status tracking (pending/approved/rejected)

### 🚀 Publishing to Intercom
- Select FAQs to publish in batches
- Draft vs. Publish toggle
- Preview before publishing
- Live publishing status
- Success/error notifications

### 📈 Analytics & Reporting
- Visual charts for themes and priorities
- Coverage trends over time
- Export reports (CSV, JSON, Markdown)
- Downloadable analysis

**Perfect for:** Product managers, support team leads, content strategists, and anyone who prefers visual interfaces over command line.

## CLI Features

### 1. Intelligent Q&A Extraction
Uses Claude to understand conversation context and extract:
- Customer questions (including implicit questions)
- Agent responses and answers
- Urgency/priority signals
- Contextual information

### 2. Semantic KB Matching
Uses sentence transformers to:
- Create embeddings of your KB articles
- Match questions to articles by meaning, not just keywords
- Calculate similarity scores
- Identify gaps where no good match exists

### 3. Smart Gap Analysis
Prioritizes gaps based on:
- Question urgency
- Gap severity (how far from matching threshold)
- Frequency of similar questions
- Thematic clustering

### 4. AI-Powered FAQ Generation
Generates comprehensive FAQ candidates with:
- Clear, well-phrased question
- Multiple question variants
- Complete, accurate answer
- Appropriate categorization
- Searchable tags
- Confidence scores

### 5. Comprehensive Reporting
Outputs multiple report formats:
- **Markdown report**: Human-readable analysis
- **CSV exports**: For spreadsheet analysis
- **JSON exports**: For programmatic access
- **Summary statistics**: Coverage, themes, priorities

## CLI Reference

### `test-intercom`
Test your Intercom API connection.

```bash
python cli.py test-intercom
```

### `fetch-kb`
Fetch existing KB articles from Intercom.

```bash
python cli.py fetch-kb [OPTIONS]

Options:
  --output, -o PATH  Output file path [default: ./data/kb_articles.json]
```

### `process`
Main processing pipeline: analyze data and identify gaps.

```bash
python cli.py process [OPTIONS]

Required:
  --kb-articles PATH  Path to KB articles JSON file

Options:
  --transcripts PATH   Directory with transcript files
  --emails PATH        Directory with email files
  --output, -o PATH    Output directory [default: ./reports]
  --generate-faqs      Generate FAQ candidates [default: true]
  --no-generate-faqs   Skip FAQ generation (faster)

Note: Must provide at least --transcripts or --emails
```

### `generate-faqs-only`
Generate FAQs from an existing gaps CSV.

```bash
python cli.py generate-faqs-only [OPTIONS]

Required:
  --gaps PATH       Path to knowledge_gaps.csv file

Options:
  --output, -o PATH  Output directory [default: ./reports]
  --limit, -n INT    Limit number of FAQs to generate
```

### `publish-to-intercom`
Publish FAQ candidates directly to Intercom as help articles.

```bash
python cli.py publish-to-intercom [OPTIONS]

Required:
  --faqs PATH         Path to faq_candidates.json file

Options:
  --limit, -n INT     Limit number of FAQs to publish
  --publish           Publish immediately (default: creates as drafts)
  --author-id INT     Intercom admin/author ID (optional)
```

**Safety features:**
- Creates as **drafts** by default (requires `--publish` flag to publish immediately)
- Shows confirmation prompt before creating articles
- Rate-limited to avoid API throttling
- Includes question variants in article body

## Requirements

- **Python 3.9+**
- **Anthropic API key** (Claude Sonnet 4.5)
- **Intercom API access token** (with Read Articles permission)

### Python Dependencies
- `anthropic>=0.39.0` - Claude API client
- `requests>=2.31.0` - HTTP requests
- `sentence-transformers>=2.3.0` - Semantic embeddings
- `pandas>=2.2.0` - Data processing
- `click>=8.1.7` - CLI framework
- `rich>=13.7.0` - Beautiful terminal output
- `pydantic>=2.5.0` - Data validation

See [requirements.txt](requirements.txt) for full list.

## Configuration

Edit `.env` to customize:

```env
# API Keys (required)
ANTHROPIC_API_KEY=your_key_here
INTERCOM_ACCESS_TOKEN=your_token_here

# Model Configuration
LLM_MODEL=claude-sonnet-4-5-20250929
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Processing Settings
BATCH_SIZE=10
SIMILARITY_THRESHOLD=0.75  # 0.0-1.0, higher = stricter matching
```

## Cost Estimates

Using Claude Sonnet 4.5:
- **Input**: $3.00 per million tokens
- **Output**: $15.00 per million tokens

Typical processing costs:
- 1,000 call transcripts (avg 5K tokens): ~$46
- 500 emails (avg 1K tokens): ~$2.50
- Total for typical batch: **$45-50**

See [USAGE_GUIDE.md](USAGE_GUIDE.md) for cost optimization tips.

## Data Formats

### Call Transcripts
Supported formats: JSON, JSONL, CSV

**JSON Example**:
```json
{
  "id": "call_001",
  "turns": [
    {
      "speaker": "customer",
      "text": "How do I file a claim?",
      "timestamp": "00:00:12"
    },
    {
      "speaker": "agent",
      "text": "You can file a claim online...",
      "timestamp": "00:00:25"
    }
  ],
  "metadata": {
    "duration": "5:30",
    "date": "2024-01-15"
  }
}
```

### Emails
Supported formats: EML, MSG (requires extract-msg)

Export from Outlook: File > Save As > EML Format

## Output Reports

Generated in the `--output` directory:

| File | Description |
|------|-------------|
| `report.md` | Human-readable markdown report with analysis and recommendations |
| `knowledge_gaps.csv` | All identified gaps with priority scores |
| `faq_candidates.csv` | Generated FAQ entries ready for review |
| `faq_candidates.json` | Same FAQs in JSON format for import |
| `summary_report.json` | Machine-readable statistics |

## Workflow Example

```bash
# Step 1: Get your baseline KB
python cli.py fetch-kb

# Step 2: Process 10 sample transcripts (test run)
python cli.py process \
  --kb-articles ./data/kb_articles.json \
  --transcripts ./data/transcripts_sample \
  --output ./reports_test

# Step 3: Review reports_test/report.md

# Step 4: If satisfied, process full dataset
python cli.py process \
  --kb-articles ./data/kb_articles.json \
  --transcripts ./data/transcripts \
  --emails ./data/emails \
  --output ./reports

# Step 5: Review and approve FAQ candidates
# Open reports/faq_candidates.csv in Excel

# Step 6: Import approved FAQs to Intercom
# (manually or via API)
```

## Privacy & Security

### 🛡️ Automatic PII Anonymization

The tool **automatically anonymizes PII** before sending data to external APIs:

- ✅ Email addresses → `customer1@example.com`
- ✅ Phone numbers → `[REDACTED_PHONE]`
- ✅ Policy numbers → `POL-0001`
- ✅ Credit cards → `[REDACTED_CARD]`
- ✅ Addresses → `[REDACTED_ADDRESS]`
- ✅ And more...

**See [PII_ANONYMIZATION.md](PII_ANONYMIZATION.md) for full details.**

### Data Flow
1. Original data stays on your local system
2. PII is anonymized before API calls
3. Only anonymized text sent to Claude
4. Reports generated locally (no PII)

## Tips

- **Start small**: Process 10-20 transcripts first to verify quality
- **Review before publishing**: AI-generated FAQs are drafts, not final content
- **Iterate**: Run processing multiple times as you improve your KB
- **Batch processing**: Process large datasets overnight
- **Cost control**: Use `--no-generate-faqs` to just identify gaps first
- **Privacy first**: Anonymization is automatic - your customer data is protected

## Contributing

This is an internal tool for Pikl. For issues or improvements, create a GitHub issue or submit a PR.

## License

Proprietary - Pikl Insurance
