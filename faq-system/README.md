# Pikl Internal FAQ System

An AI-powered knowledge base system that parses insurance policy wordings and generates internal FAQs for team members. This system helps agents quickly find answers to questions like "Does [Insurer Y] exclude this?" while ensuring regulatory compliance.

## System Overview

This system provides **three ways** to work with policy information:

1. **Structured FAQ Database**: Pre-generated FAQs organized by category, insurer, and policy type
2. **AI-Powered Search**: Dynamic question answering using Claude AI with RAG (Retrieval Augmented Generation)
3. **Compliance Reports**: FCA-focused reports for regulatory oversight

## What Information Is Extracted

The system extracts **8 key dimensions** from policy documents:

1. **Exclusions** - What's NOT covered (most common agent questions)
2. **Endorsements** - Available modifications and add-ons
3. **Claims Requirements** - Documents, timeframes, and process
4. **Eligibility Criteria** - Who qualifies for coverage
5. **Policy Definitions** - Key term meanings
6. **Coverage Limits** - Maximum payouts and sub-limits
7. **Time-Sensitive Requirements** - Deadlines and waiting periods
8. **FCA Compliance** - Regulatory disclosures and requirements

See [FEATURES.md](FEATURES.md) for detailed information about each dimension.

## Directory Structure

```
faq-system/
├── scripts/
│   ├── parse_policies.py       # Extract data from policy PDFs using Claude
│   ├── generate_faqs.py        # Generate structured FAQs from parsed data
│   ├── ai_search.py            # AI-powered search interface
│   ├── export_for_intercom.py  # Export FAQs for Intercom import
│   └── compliance_report.py    # Generate FCA compliance reports
├── data/
│   ├── internal_faqs.json      # Generated FAQ database
│   ├── exports/                # Export files for Intercom
│   └── compliance/             # Regulatory compliance reports
├── requirements.txt            # Python dependencies
└── FEATURES.md                 # Detailed feature documentation

policy-wordings/
├── raw/                        # Place your policy PDF files here
├── processed/                  # Extracted policy data (JSON)
└── README.md                   # Instructions for adding policies
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd faq-system
pip install -r requirements.txt
```

Or if using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up API Key

You need an Anthropic API key to use Claude AI:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

To make this permanent, add it to your `.bashrc`, `.zshrc`, or environment configuration.

### 3. Add Policy Documents

Place your insurance policy PDF files in the `policy-wordings/raw/` directory:

```bash
cd ../policy-wordings/raw
# Copy your PDF files here
```

**Naming convention** (recommended):
- `[InsurerId]_[PolicyType]_[Version].pdf`
- Examples:
  - `AXA_Travel_v2.1.pdf`
  - `Zurich_Home_2024.pdf`
  - `Aviva_Motor_Comprehensive.pdf`

## Usage Workflow

### Step 1: Parse Policy Documents

Extract structured information from PDFs using Claude AI:

```bash
cd faq-system/scripts
python parse_policies.py
```

This will:
- Read all PDFs from `policy-wordings/raw/`
- Use Claude to extract key information (exclusions, limits, conditions, etc.)
- Save structured data to `policy-wordings/processed/` as JSON files

**What gets extracted:**
- Insurer name and policy type
- Coverage summary and key inclusions
- **Exclusions** (comprehensive list)
- **Endorsements** (available modifications)
- **Claims requirements** (documents, timeframes, process)
- **Eligibility criteria** (age, medical, occupational, residency)
- **Policy definitions** (key terms and meanings)
- Coverage limits and sub-limits
- Time-sensitive requirements (deadlines, waiting periods)
- **FCA compliance** (disclosures, IPID, complaints process)
- Special conditions and geographical coverage

### Step 2: Generate FAQ Database

Create structured FAQs from the parsed data:

```bash
python generate_faqs.py
```

This will:
- Load all processed policy data
- Generate FAQs organized by category:
  - **Exclusions** (most important for agents!)
  - **Endorsements & Modifications**
  - **Claims Requirements**
  - **Eligibility**
  - **Policy Definitions**
  - **Coverage Limits**
  - **Comparisons** (across insurers)
  - **Common Questions**
- Save to `faq-system/data/internal_faqs.json`

### Step 3: Use AI-Powered Search

Ask questions directly using AI search:

```bash
python ai_search.py
```

This launches an interactive search interface where you can ask questions like:
- "Does AXA travel insurance exclude pre-existing conditions?"
- "What are the coverage limits for Zurich home insurance?"
- "Compare pregnancy exclusions across all travel insurers"
- "What does Aviva exclude for mental health claims?"

**Or** ask a single question from the command line:

```bash
python ai_search.py "Does Zurich exclude extreme sports?"
```

### Step 4: Generate Compliance Reports (Optional)

Create FCA-focused compliance reports:

```bash
python compliance_report.py
```

This generates regulatory oversight reports:
- `compliance/compliance_summary.txt` - Executive summary of compliance status
- `compliance/fca_disclosures.txt` - FCA disclosure tracking
- `compliance/exclusions_compliance.txt` - Exclusions requiring clear disclosure
- `compliance/eligibility_compliance.txt` - Fair treatment and discrimination review
- `compliance/claims_compliance.txt` - Claims process fairness review

These reports help ensure:
- FCA requirements are met
- Customer communication is clear
- Fair treatment principles are followed
- Claims processes are reasonable

### Step 5: Export for Intercom

Export FAQs in formats suitable for Intercom:

```bash
python export_for_intercom.py
```

This generates:
- `exports/intercom_faqs.csv` - For bulk CSV import
- `exports/intercom_faqs.md` - Human-readable format for manual copy-paste
- `exports/intercom_faqs_structured.json` - For API import
- `exports/by_insurer/*.json` - Separate files per insurer
- `exports/faq_summary.txt` - Statistics and overview

## Key Features

### 1. Comprehensive Exclusion Coverage

The system focuses heavily on exclusions since these are the most common questions:
- General exclusion overviews per policy
- Specific exclusion searches (pre-existing conditions, mental health, etc.)
- Cross-insurer exclusion comparisons

### 2. Multi-Dimensional Coverage

Beyond exclusions, the system tracks:
- **Endorsements** - What can be added to policies
- **Claims Process** - Required documents and timeframes
- **Eligibility** - Who qualifies for coverage
- **Definitions** - Clear term meanings
- **Limits** - Coverage amounts and sub-limits
- **Compliance** - FCA regulatory requirements

### 3. Smart FAQ Generation

FAQs are automatically generated in formats agents need:
- "What does [Insurer X] exclude?"
- "What endorsements are available for [Policy Y]?"
- "What documents are needed to file a claim?"
- "Who is eligible for [Policy Y]?"
- "What's the limit for [coverage type]?"
- "How do insurers compare on [topic]?"

### 4. AI-Powered Dynamic Search

When pre-generated FAQs don't cover a question:
- Ask in natural language
- Get answers based on actual policy documents
- Responses cite specific insurers and policies
- Handles complex comparison questions

### 5. Regulatory Compliance Reports

FCA-focused reports for compliance teams:
- Track required disclosures
- Review eligibility for fairness
- Assess claims process reasonableness
- Identify high-risk exclusions

### 6. Intercom Integration

Export FAQs as **Internal Only** articles in Intercom:
- Mark all as "Team Only" visibility
- Organize by category and insurer
- Tag for easy searching
- Update as policies change

## Example Questions You Can Answer

**Exclusion Questions:**
- "Does AXA travel insurance exclude pre-existing conditions?"
- "What mental health exclusions does Zurich have?"
- "Do any of our insurers cover pandemic-related claims?"

**Endorsement Questions:**
- "Can we add winter sports coverage to this policy?"
- "What endorsements are available for Aviva home insurance?"
- "How much does the golf equipment endorsement cost?"

**Claims Questions:**
- "What documents are needed for a baggage claim with Zurich?"
- "How quickly must I notify AXA about a travel claim?"
- "Does the customer need a police report for theft claims?"

**Eligibility Questions:**
- "Can a 75-year-old get this travel policy?"
- "Are offshore workers eligible for this policy?"
- "What are the residency requirements for home insurance?"

**Definition Questions:**
- "How does Zurich define 'extreme sports'?"
- "Who counts as 'immediate family' under AXA policies?"
- "What qualifies as 'valuables' for baggage claims?"

**Coverage & Limit Questions:**
- "What's the maximum baggage claim under Aviva travel?"
- "Is there a per-item limit for valuables?"
- "What are the coverage limits for medical expenses abroad?"

**Comparison Questions:**
- "Compare pregnancy coverage across all travel insurers"
- "Which insurer has the best claims process for travel?"
- "What are the key differences between AXA and Zurich travel policies?"

**Compliance Questions:**
- "What FCA disclosures are required for this policy?"
- "How do customers make complaints?"
- "Are there any eligibility criteria that need review?"

## Updating the Knowledge Base

When you receive new policy documents:

1. Add new PDFs to `policy-wordings/raw/`
2. Run `parse_policies.py` to process them
3. Run `generate_faqs.py` to update the FAQ database
4. Run `export_for_intercom.py` to generate new exports
5. Import updated FAQs into Intercom

## Tips for Best Results

### For Policy Parsing:
- Use clear, official policy wording PDFs (not marketing materials)
- Ensure PDFs are text-based, not scanned images
- One policy document per file works best

### For FAQ Generation:
- Review generated FAQs before importing to Intercom
- Customize categories and tags to match your team's workflow
- Add your own questions to the `common_questions` section

### For AI Search:
- Be specific in your questions
- Mention insurer names when relevant
- Use policy type filters for faster searches
- Test with real agent questions

## Integration with Intercom

### Setting Up Internal FAQs:

1. In Intercom, create a new "Help Collection" called "Internal: Policy Knowledge"
2. Mark it as "Team Only" (not visible to customers)
3. Import FAQs using one of these methods:
   - **CSV Import**: Use `intercom_faqs.csv`
   - **Manual Entry**: Copy from `intercom_faqs.md`
   - **API Import**: Use `intercom_faqs_structured.json`

### Recommended Structure in Intercom:

```
Internal: Policy Knowledge
├── Exclusions
│   ├── By Insurer
│   └── By Topic (pre-existing, mental health, etc.)
├── Coverage Limits
│   └── By Policy Type
├── Comparisons
│   └── Cross-Insurer
└── Common Questions
    └── By Policy Type
```

## Maintenance

### Regular Updates:
- Re-run processing when policies are updated
- Review and add frequently asked questions
- Monitor which FAQs get the most use

### Quality Checks:
- Spot-check AI-extracted information against source PDFs
- Update FAQs when agents find inaccuracies
- Add new exclusion categories as they emerge

## Troubleshooting

**Error: "No processed policies found"**
- Make sure you've run `parse_policies.py` first
- Check that PDFs are in `policy-wordings/raw/`

**Error: "ANTHROPIC_API_KEY not set"**
- Set your API key: `export ANTHROPIC_API_KEY='your-key'`

**Poor quality extractions:**
- Ensure PDFs are text-based, not scanned images
- Try using higher quality/official policy documents
- Check that PDFs aren't corrupted

**AI search not finding answers:**
- Make sure you've run both parse and generate scripts
- Check that the question relates to policies in the knowledge base
- Try being more specific with insurer/policy type

## Cost Considerations

This system uses Claude AI API calls:
- **Parsing**: ~$0.10-0.30 per policy document (one-time)
- **Search**: ~$0.01-0.05 per question
- Pre-generated FAQs have no ongoing costs

For a typical setup with 10-20 policy documents, initial parsing costs ~$2-6, with minimal ongoing costs for searches.

## Future Enhancements

Potential additions:
- Web interface for easier searching
- Automatic policy change detection
- Integration with Pikl's CRM system
- Multi-language support
- Agent usage analytics

## Support

For questions or issues with this system, contact your technical team or refer to the Anthropic Claude API documentation at https://docs.anthropic.com/
