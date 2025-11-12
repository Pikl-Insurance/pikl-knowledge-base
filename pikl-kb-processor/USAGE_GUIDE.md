# Pikl KB Processor - Usage Guide

## Quick Start

### 1. Installation

```bash
cd pikl-kb-processor
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add:
- `ANTHROPIC_API_KEY`: Your Anthropic (Claude) API key
- `INTERCOM_ACCESS_TOKEN`: Your Intercom API access token

To get an Intercom access token:
1. Go to your Intercom workspace
2. Navigate to Settings > Developers > Developer Hub
3. Create a new app or use an existing one
4. Add "Read articles" permission
5. Copy the access token

### 3. Test Your Setup

```bash
python cli.py test-intercom
```

This will verify your Intercom API connection.

## Workflow

### Step 1: Fetch Your Knowledge Base

First, download your existing Intercom help articles:

```bash
python cli.py fetch-kb --output ./data/kb_articles.json
```

This creates a baseline of your current knowledge base.

### Step 2: Prepare Your Data

**Transcripts**: Place your call transcript files in a directory. Supported formats:
- JSON (`.json`)
- JSONL (`.jsonl`) - one turn per line
- CSV (`.csv`) - must have `speaker` and `text` columns

Example JSON format:
```json
{
  "id": "call_001",
  "turns": [
    {"speaker": "customer", "text": "How do I file a claim?", "timestamp": "00:00:12"},
    {"speaker": "agent", "text": "You can file a claim online...", "timestamp": "00:00:25"}
  ],
  "metadata": {"duration": "5:30", "date": "2024-01-15"}
}
```

**Emails**: Export your Outlook emails to EML format. Save them in a directory.

To export from Outlook:
1. Select email(s)
2. File > Save As
3. Choose "EML Format (*.eml)"
4. Save to a folder

### Step 3: Process Your Data

Run the full processing pipeline:

```bash
python cli.py process \
  --kb-articles ./data/kb_articles.json \
  --transcripts ./data/transcripts \
  --emails ./data/emails \
  --output ./reports
```

Options:
- `--kb-articles`: Path to KB articles JSON (from Step 1)
- `--transcripts`: Directory with transcript files (optional)
- `--emails`: Directory with email files (optional)
- `--output`: Where to save reports (default: `./reports`)
- `--no-generate-faqs`: Skip FAQ generation (faster, just identify gaps)

What this does:
1. Loads your KB articles
2. Parses transcripts and emails
3. Extracts customer questions using Claude
4. Matches questions to existing KB articles
5. Identifies knowledge gaps (questions not well-covered)
6. Generates FAQ candidates for gaps
7. Creates detailed reports

### Step 4: Review the Reports

Check the `./reports` directory for:

**`report.md`**: Human-readable markdown report with:
- Summary statistics
- High-priority knowledge gaps
- Top FAQ candidates with full content
- Recommendations

**`knowledge_gaps.csv`**: All identified gaps with:
- Question text
- Priority score
- Theme/category
- Best matching article (if any)
- Source information

**`faq_candidates.csv`**: Generated FAQ entries with:
- Question and variants
- Answer text
- Category and tags
- Confidence and priority scores

**`faq_candidates.json`**: Same FAQs in JSON format for import

**`summary_report.json`**: Machine-readable summary statistics

## Advanced Usage

### Generate FAQs from Existing Gaps

If you've already run processing and want to generate more FAQs:

```bash
python cli.py generate-faqs-only \
  --gaps ./reports/knowledge_gaps.csv \
  --output ./reports \
  --limit 20
```

This is useful if you:
- Want to generate FAQs for specific gaps after review
- Need to regenerate with different parameters
- Want to process gaps in batches

### Customizing Configuration

Edit `.env` to adjust settings:

```env
# Model selection
LLM_MODEL=claude-sonnet-4-5-20250929

# Embedding model for similarity matching
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Similarity threshold (0.0-1.0)
# Higher = stricter matching, more gaps identified
SIMILARITY_THRESHOLD=0.75

# Batch size for processing
BATCH_SIZE=10
```

**Similarity Threshold Guide**:
- `0.85+`: Very strict - only near-perfect matches count as "good"
- `0.75`: Balanced (default) - good for most cases
- `0.65`: Lenient - fewer gaps, but might miss nuances
- `0.50`: Very lenient - most questions match existing content

## Understanding the Reports

### Priority Scores

Each gap has a priority score (0.0-1.0) based on:
- **Urgency**: How urgent/critical the customer's question was
- **Gap Severity**: How far the best match is from the threshold
- **Frequency**: How often this question appears

Focus on gaps with priority > 0.7 first.

### Themes

Questions are automatically categorized by theme:
- **claim**: Claims and filing
- **policy**: Policy and coverage questions
- **payment**: Billing and payment
- **account**: Account access and management
- **cancellation**: Policy cancellation
- **renewal**: Policy renewal
- **quote**: Quotes and pricing
- **document**: Documents and paperwork
- **contact**: Contact and support
- **change**: Making changes to policies
- **general**: Uncategorized questions

### Coverage Percentage

Shows what % of customer questions have good matches in your KB.

- **<50%**: Low coverage - prioritize creating FAQs
- **50-75%**: Moderate - focus on medium-priority gaps
- **>75%**: Good - refine existing content and handle edge cases

## Publishing FAQs to Intercom

Once you've reviewed and approved FAQ candidates, you have several options:

### Option 1: Direct Publishing via CLI (Recommended!)

The tool now includes a command to publish FAQs directly to Intercom:

```bash
# Create FAQs as drafts (safe, allows review in Intercom)
python cli.py publish-to-intercom \
  --faqs ./reports/faq_candidates.json \
  --limit 10

# Publish immediately (skips draft stage)
python cli.py publish-to-intercom \
  --faqs ./reports/faq_candidates.json \
  --limit 5 \
  --publish
```

**What it does:**
- Creates articles in your Intercom help center
- Includes the main question as title
- Adds question variants in the body
- Shows category information
- Creates as drafts by default (safe!)
- Asks for confirmation before proceeding
- Rate-limited to respect API limits

**Recommended workflow:**
1. Review `faq_candidates.json` manually first
2. Remove any FAQs you don't want to publish (edit the JSON file)
3. Run `publish-to-intercom` to create as drafts
4. Review drafts in Intercom interface
5. Publish manually from Intercom after final review

### Option 2: Manual Entry
1. Open `faq_candidates.csv` in Excel/Google Sheets
2. Copy the question and answer
3. Create new article in Intercom
4. Use suggested category and tags

Good for when you want maximum control over each article.

### Option 3: Custom Integration
If you need more control over the article structure, you can use the Intercom API directly:

```python
import json
import requests

with open('reports/faq_candidates.json') as f:
    faqs = json.load(f)

headers = {
    'Authorization': f'Bearer {INTERCOM_TOKEN}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

for faq in faqs:
    data = {
        'title': faq['question_text'],
        'body': faq['answer_text'],
        'description': faq['question_variants'][0] if faq['question_variants'] else '',
        'state': 'draft'  # or 'published'
    }

    response = requests.post(
        'https://api.intercom.io/articles',
        headers=headers,
        json=data
    )
    print(f"Created: {faq['question_text']}")
```

## Tips and Best Practices

### 1. Start Small
- Process a sample of 10-20 transcripts first
- Review the quality of extraction and FAQs
- Adjust settings if needed
- Then process the full dataset

### 2. Review Before Publishing
- Generated FAQs are drafts - always review them
- Check for accuracy, completeness, and tone
- Verify technical details and policy information
- Add your brand voice and style

### 3. Iterative Approach
- Run initial processing
- Review high-priority gaps
- Create/update FAQs in Intercom
- Re-run processing to see improved coverage
- Repeat until satisfied

### 4. Cost Management
- Processing uses Claude API (costs money)
- 1,000 transcripts ≈ $40-50 with Sonnet 4.5
- Consider processing in batches
- Use `--no-generate-faqs` flag to just identify gaps first

### 5. Data Quality
- Better transcripts = better results
- Remove duplicate emails/calls before processing
- Filter out very short or irrelevant conversations
- Clean up any PII or sensitive information first

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Check your `.env` file exists in the right directory
- Verify the variable name is exactly `ANTHROPIC_API_KEY`
- Make sure there are no quotes around the key

### "No transcript files found"
- Check file extensions (.json, .jsonl, .csv)
- Verify the directory path is correct
- Check file permissions

### "Failed to parse LLM response"
- This is usually temporary - the LLM response wasn't valid JSON
- The tool will skip that item and continue
- If it happens frequently, check your API key and quotas

### Low Quality FAQs
- Try adjusting the similarity threshold
- Provide more context in transcripts
- Review the source questions - are they clear?
- Consider using Opus model for higher quality (more expensive)

### Slow Processing
- Processing is intentional to avoid rate limits
- Reduce batch size in `.env` if hitting rate limits
- Consider processing overnight for large datasets
- Use `--no-generate-faqs` for faster gap identification

## Next Steps

1. **Review the markdown report** - Start with high-priority gaps
2. **Validate FAQ candidates** - Check accuracy and completeness
3. **Publish approved FAQs** - Add them to your Intercom KB
4. **Re-run processing** - Measure improvement in coverage
5. **Monitor ongoing** - Process new calls/emails periodically

## Support

For issues or questions:
- Check this guide first
- Review error messages carefully
- Check API key permissions and quotas
- Verify file formats match expected structure
