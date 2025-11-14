# Intercom Import Guide

This guide explains how to import your 1,441 FAQs to Intercom.

## Overview

Two scripts are available:
1. **intercom_import_test.py** - Test import (20 sample FAQs)
2. **intercom_import_full.py** - Full import (all 1,441 FAQs)

## Prerequisites

✅ Already completed:
- Python environment set up
- `requests` library installed
- FAQs generated in `data/internal_faqs.json`

✅ You need:
- Intercom access token (already in `.env.local`)
- Admin access to your Intercom workspace

## Step 1: Test Import (Recommended First)

Run the test import to verify everything works:

```bash
cd faq-system/scripts
export INTERCOM_ACCESS_TOKEN="your-token-from-env-file"
../venv/bin/python intercom_import_test.py
```

This will:
- Import 20 sample FAQs (diverse across categories)
- Create a test collection: `[TEST] Internal Policy Knowledge`
- Create articles as DRAFTS for review

**What to check:**
1. Go to Intercom → Help Center → Collections
2. Find `[TEST] Internal Policy Knowledge`
3. Review how articles look
4. Test search functionality
5. Check formatting and metadata

**Clean up test:**
- Delete the test collection in Intercom when done

## Step 2: Full Import

Once satisfied with test results:

```bash
cd faq-system/scripts
export INTERCOM_ACCESS_TOKEN="your-token-from-env-file"
../venv/bin/python intercom_import_full.py
```

### What It Creates

**Main Collection:**
- Name: `Internal: Policy Knowledge Base`
- Description: Comprehensive policy info for internal team

**Sub-Collections (8 categories):**
1. **Exclusions** (64 articles) - What's NOT covered
2. **Claims Requirements** (104 articles) - Documents, timeframes, process
3. **Eligibility** (104 articles) - Who qualifies
4. **Endorsements & Modifications** (101 articles) - Policy add-ons
5. **Policy Definitions** (416 articles) - Key terms
6. **Coverage Limits** (298 articles) - Max payouts
7. **Common Questions** (350 articles) - FAQ from policies
8. **Comparisons** (4 articles) - Cross-insurer

### Import Process

The script will:
1. Load all 1,441 FAQs
2. Show breakdown by category
3. Ask for confirmation
4. Create collection structure
5. Import articles (progress shown)
6. Save progress every 10 articles

**Articles are imported as DRAFTS** - you can review before publishing.

### Progress Tracking

- Progress saved to: `data/intercom_import_progress.json`
- Can resume if interrupted
- Failed articles tracked separately

### Time Estimate

- With rate limiting: ~15-20 minutes
- 0.5 seconds between API calls

## Step 3: Review & Publish in Intercom

After import completes:

### 1. Review Articles
- Go to Intercom → Help Center → Collections
- Find `Internal: Policy Knowledge Base`
- Review articles in each category
- Check formatting, links, metadata

### 2. Set Visibility
**IMPORTANT:** Set collection to Team Only
- Click collection settings
- Set visibility: **Team Only** (not public)
- Save changes

### 3. Publish Articles
When ready:
- Select all articles in a collection
- Bulk action → Publish
- Repeat for each category

### 4. Configure Search
- Enable search for the collection
- Test search with common queries:
  - "AXA exclusions"
  - "claims requirements"
  - "endorsements available"

## Troubleshooting

### Error: "INTERCOM_ACCESS_TOKEN not set"
```bash
export INTERCOM_ACCESS_TOKEN="your-token-here"
```

Or set it in your environment permanently.

### Error: Rate limit exceeded
The script includes built-in delays (0.5s). If you still hit limits:
- Increase `RATE_LIMIT_DELAY` in the script
- Wait a few minutes and resume

### Import interrupted?
Just run the script again:
```bash
../venv/bin/python intercom_import_full.py
```
It will resume from where it stopped.

### Start fresh?
Delete progress file:
```bash
rm ../data/intercom_import_progress.json
```

### Some articles failed?
Check `data/intercom_import_progress.json` for failed articles list.
Re-run import - it will skip successful ones.

## Collection Structure in Intercom

```
Internal: Policy Knowledge Base/
├── Exclusions/
│   └── 64 articles
├── Claims Requirements/
│   └── 104 articles
├── Eligibility/
│   └── 104 articles
├── Endorsements & Modifications/
│   └── 101 articles
├── Policy Definitions/
│   └── 416 articles
├── Coverage Limits/
│   └── 298 articles
├── Common Questions/
│   └── 350 articles
└── Comparisons/
    └── 4 articles
```

## Search Examples

Once imported, agents can search:

**By insurer:**
- "AXA exclusions"
- "Aviva claims"
- "Arkel eligibility"

**By topic:**
- "pre-existing conditions"
- "endorsements available"
- "claims documents"
- "age restrictions"

**By policy type:**
- "home insurance exclusions"
- "legal expenses definitions"
- "property host coverage"

## Updating FAQs

When policies change:

1. Update policy PDFs in `policy-wordings/raw/`
2. Re-run parsing: `python parse_policies.py`
3. Re-run FAQ generation: `python generate_faqs.py`
4. Export updated FAQs
5. In Intercom, update affected articles manually
   (Or delete old collection and re-import)

## Best Practices

### Naming
- Keep collection names clear and searchable
- Use consistent tagging
- Include insurer names in articles

### Organization
- Group by category (already done)
- Use tags for cross-referencing
- Link related articles

### Maintenance
- Review quarterly
- Update when policies change
- Monitor search analytics
- Get agent feedback

### Security
- Always mark as "Team Only"
- Never make policy details public
- Restrict access to internal team

## Support

If you encounter issues:
1. Check Intercom API status
2. Verify your access token
3. Check progress file for details
4. Review Intercom API logs

## Summary

**Test first:**
```bash
../venv/bin/python intercom_import_test.py
```

**Then import all:**
```bash
../venv/bin/python intercom_import_full.py
```

**Then in Intercom:**
1. Set collection to Team Only
2. Review articles
3. Publish when ready
4. Test search functionality

Your internal knowledge base will be ready for your team to use!
