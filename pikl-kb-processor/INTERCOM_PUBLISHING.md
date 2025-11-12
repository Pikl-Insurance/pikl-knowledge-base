# Publishing FAQs to Intercom

## Overview

The Pikl KB Processor now includes **direct integration with Intercom** to automatically publish your AI-generated FAQ candidates as help articles. This closes the loop from identifying knowledge gaps to filling them in your actual knowledge base.

## How It Works

```
Call Transcripts/Emails
         ↓
    Extract Q&A (AI)
         ↓
   Match to KB (Semantic)
         ↓
  Identify Gaps (Analysis)
         ↓
  Generate FAQs (AI)
         ↓
   Review & Approve
         ↓
  Publish to Intercom ← NEW!
```

## Quick Start

```bash
# Step 1: Process your data and generate FAQs
python cli.py process \
  --kb-articles ./data/kb_articles.json \
  --transcripts ./data/transcripts \
  --output ./reports

# Step 2: Review the FAQs in reports/faq_candidates.json

# Step 3: Publish to Intercom as drafts
python cli.py publish-to-intercom \
  --faqs ./reports/faq_candidates.json \
  --limit 10

# Step 4: Review drafts in Intercom and publish
```

## Command Options

### Basic Usage

```bash
python cli.py publish-to-intercom --faqs ./reports/faq_candidates.json
```

This will:
- Create articles as **drafts** (not published)
- Ask for confirmation before creating
- Upload ALL FAQs from the file
- Rate-limit requests to avoid API throttling

### Advanced Options

**Limit number of articles:**
```bash
python cli.py publish-to-intercom \
  --faqs ./reports/faq_candidates.json \
  --limit 5
```
Only creates the first 5 FAQs from the file.

**Publish immediately:**
```bash
python cli.py publish-to-intercom \
  --faqs ./reports/faq_candidates.json \
  --publish
```
⚠️ **Warning**: This publishes articles immediately, skipping the draft stage.

**Specify author:**
```bash
python cli.py publish-to-intercom \
  --faqs ./reports/faq_candidates.json \
  --author-id 12345
```
Sets the Intercom admin/author ID for the articles.

## Article Structure

Each published article includes:

**Title**: The main question
```
How do I file a claim?
```

**Body**: The AI-generated answer plus context
```
You can file a claim online through our customer portal, or by calling
our support team. You'll need to provide photos of the damage and a
police report if available.

**Related questions:**
- What do I need to file a claim?
- Can I file a claim online?
- How long does claim processing take?

*Category: claim*
```

**Description**: First question variant (for search/preview)
```
What do I need to file a claim?
```

**State**: `draft` (default) or `published` (with --publish flag)

## Recommended Workflow

### For Safety: Three-Step Review

1. **Generate FAQs** (AI-assisted, requires review)
   ```bash
   python cli.py process \
     --kb-articles ./data/kb_articles.json \
     --transcripts ./data/transcripts
   ```

2. **Manual Review** (Critical!)
   - Open `reports/faq_candidates.json`
   - Review each FAQ for accuracy
   - Edit answers if needed
   - Remove low-quality FAQs
   - Save the edited file

3. **Publish as Drafts** (Safe)
   ```bash
   python cli.py publish-to-intercom \
     --faqs ./reports/faq_candidates.json
   ```

4. **Final Review in Intercom**
   - Go to your Intercom help center
   - Review draft articles
   - Make final edits if needed
   - Publish manually

### For Speed: Two-Step Review

1. **Generate and publish as drafts**
   ```bash
   python cli.py process \
     --kb-articles ./data/kb_articles.json \
     --transcripts ./data/transcripts

   python cli.py publish-to-intercom \
     --faqs ./reports/faq_candidates.json
   ```

2. **Review in Intercom**
   - Review all drafts in Intercom interface
   - Edit as needed
   - Publish or delete

### For Automation: Direct Publishing

⚠️ **Only recommended after you've validated the quality of AI-generated FAQs**

```bash
python cli.py process \
  --kb-articles ./data/kb_articles.json \
  --transcripts ./data/transcripts

python cli.py publish-to-intercom \
  --faqs ./reports/faq_candidates.json \
  --publish
```

This publishes immediately. Use with caution!

## Filtering FAQs Before Publishing

You can edit the `faq_candidates.json` file to remove or modify FAQs before publishing:

```bash
# Make a copy
cp reports/faq_candidates.json reports/faq_candidates_filtered.json

# Edit the file (remove unwanted FAQs, edit answers, etc.)
# Use any text editor or:
python -c "
import json
with open('reports/faq_candidates.json') as f:
    faqs = json.load(f)

# Keep only high-priority FAQs
filtered = [f for f in faqs if f['priority_score'] >= 0.7]

with open('reports/faq_candidates_filtered.json', 'w') as f:
    json.dump(filtered, f, indent=2)
"

# Publish the filtered set
python cli.py publish-to-intercom \
  --faqs ./reports/faq_candidates_filtered.json
```

## Selective Publishing by Priority

```bash
# Publish only top 10 highest priority FAQs
python cli.py publish-to-intercom \
  --faqs ./reports/faq_candidates.json \
  --limit 10

# (FAQs are already sorted by priority in the JSON file)
```

## Error Handling

The tool handles errors gracefully:

- **Authentication errors**: Check your Intercom access token
- **Rate limiting**: Built-in 0.5s delay between articles
- **Invalid data**: Skips invalid FAQs and continues
- **Network errors**: Reports error and continues with next article

If an article fails to create, the tool will:
1. Print an error message
2. Continue with remaining articles
3. Report final success count

## API Permissions Required

Your Intercom access token needs:
- ✅ **Read articles** (to fetch KB)
- ✅ **Write articles** (to create new articles)

To check/update permissions:
1. Go to Intercom > Settings > Developers
2. Select your app
3. Ensure "Articles" has Read and Write permissions

## Rate Limits

Intercom API rate limits:
- **Standard**: 500 requests per minute
- **Tool behavior**: 0.5s between requests = ~120 articles/minute

The tool stays well within limits. For bulk uploads (100+ articles), expect:
- 100 articles: ~1 minute
- 500 articles: ~5 minutes

## Monitoring Created Articles

After publishing, you can:

1. **View in Intercom**:
   - Go to Articles in your Intercom workspace
   - Filter by "Draft" status
   - Review and publish

2. **Re-fetch your KB**:
   ```bash
   python cli.py fetch-kb
   ```
   Your newly created articles will be included in the next processing run.

## Best Practices

### ✅ Do:
- Start with `--limit 5` to test the output quality
- Review FAQs before publishing (edit the JSON file)
- Use draft mode first (default behavior)
- Create articles in batches (easier to review)
- Keep the confirmation prompt enabled
- Monitor the first few articles in Intercom

### ❌ Don't:
- Don't use `--publish` flag until you've validated quality
- Don't skip the review step (AI can make mistakes)
- Don't publish 100+ articles at once without review
- Don't disable confirmation prompts in scripts
- Don't forget to check for sensitive information

## Troubleshooting

**"Failed to create article"**
- Check your Intercom access token permissions
- Verify token has "Write articles" permission
- Check the error message for specifics

**"Authentication failed"**
- Regenerate your Intercom access token
- Update `.env.local` with new token

**Articles created but empty**
- Check the FAQ JSON file structure
- Ensure `question_text` and `answer_text` fields exist

**Want to undo?**
- If created as drafts: Delete from Intercom interface
- If published: Unpublish or delete from Intercom interface
- No bulk delete available - must be done in Intercom UI

## Integration with Existing Workflow

```bash
# Full workflow example
# 1. Fetch current KB
python cli.py fetch-kb

# 2. Process new transcripts
python cli.py process \
  --kb-articles ./data/kb_articles.json \
  --transcripts ./data/new_transcripts \
  --output ./reports

# 3. Review reports/report.md

# 4. Filter high-priority FAQs
python -c "
import json
with open('reports/faq_candidates.json') as f:
    faqs = [f for f in json.load(f) if f['priority_score'] >= 0.7]
with open('reports/high_priority_faqs.json', 'w') as f:
    json.dump(faqs, f, indent=2)
"

# 5. Publish high-priority FAQs as drafts
python cli.py publish-to-intercom \
  --faqs ./reports/high_priority_faqs.json

# 6. Review in Intercom and publish

# 7. Re-fetch KB to see improved coverage
python cli.py fetch-kb

# 8. Re-run analysis to measure improvement
python cli.py process \
  --kb-articles ./data/kb_articles.json \
  --transcripts ./data/new_transcripts \
  --output ./reports_v2 \
  --no-generate-faqs
```

## Summary

The Intercom publishing feature enables:
- 🚀 **End-to-end automation** from calls to published articles
- 🛡️ **Safety first** with draft mode and confirmations
- 📊 **Measured improvement** by comparing coverage before/after
- ⚡ **Fast iteration** to continuously improve your KB
- 🎯 **Prioritized publishing** focusing on high-impact gaps

You now have a complete system for data-driven knowledge base development!
