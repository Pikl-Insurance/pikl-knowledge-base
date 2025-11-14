# Pikl Knowledge Base

This repository contains the Pikl Insurance website and comprehensive AI-powered knowledge base management system for Intercom.

## Overview

**Current Status:**
- ✅ 1,441 FAQs uploaded to Intercom
- ✅ 100% policy coverage (26 policies processed)
- ✅ 135 customer knowledge gaps identified
- ✅ 22 gaps addressed (16.3% coverage)
- ✅ 8 category tags created for organization

## Contents

### Website
- Mock Pikl Insurance website with Intercom Fin agent integration
- Responsive design with brand assets
- Live chat support through Intercom

### pikl-kb-processor

AI-powered knowledge base processing system that:
- **Ingests customer interactions** from emails and phone call transcripts
- **Identifies knowledge gaps** in the existing knowledge base
- **Generates FAQs and articles** using AI to fill those gaps
- **Analyzes coverage** of customer questions and policy information
- **Provides visual dashboard** with Streamlit for monitoring and analytics

See the [pikl-kb-processor documentation](./pikl-kb-processor/README.md) for detailed usage instructions.

### faq-system

Complete FAQ management and Intercom integration system:

**Core Features:**
- Generate comprehensive FAQs from 26 policy wording documents
- Upload internal and public articles to Intercom
- De-duplicate articles by title
- Organize articles into folders
- Create and apply category tags
- Analyze knowledge gap coverage

**Available Scripts:**

1. **FAQ Generation & Upload**
   - `generate_faqs.py` - Generate FAQs from policy documents
   - `enhance_faqs_for_agents.py` - Enhance FAQs with agent-friendly details
   - `intercom_import.py` - Upload FAQs to Intercom as internal articles
   - `add_public_faq.py` - Create public Help Center articles

2. **Organization & Management**
   - `intercom_dedup.py` - Remove duplicate articles from Intercom
   - `move_to_folder.py` - Organize articles into folders
   - `tag_articles.py` - Create tags and apply to articles

3. **Analytics**
   - `analyze_gap_coverage.py` - Analyze how FAQs address customer knowledge gaps
   - `coverage_analysis.py` - Analyze FAQ coverage of policy information

**Categories:**
- Exclusions
- Claims Requirements
- Eligibility
- Endorsements & Modifications
- Policy Definitions
- Coverage Limits
- Common Questions
- Comparisons

**Data Files:**
- `data/internal_faqs.json` - 1,441 FAQs uploaded to Intercom
- `data/internal_faqs_enhanced.json` - Enhanced versions with agent details
- `data/deleted_duplicates_backup.json` - Backup of removed duplicates

## Getting Started

### Website
Open `index.html` in a browser to view the Pikl Insurance website.

### Knowledge Base Processor
See [pikl-kb-processor/QUICKSTART.md](./pikl-kb-processor/QUICKSTART.md) for setup and usage instructions.

### FAQ System

**Requirements:**
```bash
cd faq-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Environment Variables:**
```bash
export INTERCOM_ACCESS_TOKEN="your_token_here"
export ANTHROPIC_API_KEY="your_key_here"
```

**Quick Commands:**
```bash
# Generate FAQs from policies
cd scripts
python generate_faqs.py

# Upload to Intercom
python intercom_import.py

# De-duplicate articles
python intercom_dedup.py --execute

# Analyze gap coverage
cd ../pikl-kb-processor/scripts
python analyze_gap_coverage.py

# Run dashboard
cd ..
python -m streamlit run app.py
```

## Dashboard

The Streamlit dashboard provides:
- **Overview**: Key metrics and recent activity
- **Knowledge Gaps**: Customer questions and coverage analysis
- **Analytics**: FAQ distribution by category, theme breakdown, gap coverage
- **FAQ Review**: Browse and search all FAQs with categories

Access at: `http://localhost:8501`

## Intercom Integration

**Internal Articles Folder:** [Internal FAQs](https://app.intercom.com/a/apps/irjtf4l5/knowledge-hub/folder/2703344)

**Help Center:** [Pikl Help Center](https://intercom.help/pikl/en)

**Tags Created:**
- `exclusions`, `claims-requirements`, `eligibility`, `endorsements`
- `definitions`, `coverage-limits`, `common-questions`, `comparisons`

## Links
- [Pikl Help Center](https://intercom.help/pikl/en)
- [Intercom Internal FAQs Folder](https://app.intercom.com/a/apps/irjtf4l5/knowledge-hub/folder/2703344)
- [Intercom Integration](https://app.intercom.com/)
