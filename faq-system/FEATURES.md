# FAQ System Features & Capabilities

## Overview

This system extracts and organizes insurance policy information across **8 key dimensions** to help agents quickly find answers to customer questions and ensure regulatory compliance.

## Extracted Information Dimensions

### 1. Exclusions (Primary Focus)
**Why it matters:** Most common agent question - "Does [Insurer Y] exclude this?"

**What we extract:**
- Comprehensive list of all policy exclusions
- Categorized exclusions (pre-existing conditions, extreme sports, etc.)
- Exclusion-specific FAQs
- Cross-insurer exclusion comparisons

**Agent questions answered:**
- "Does AXA travel insurance exclude pre-existing conditions?"
- "What mental health exclusions does Zurich have?"
- "Do any insurers cover pandemic-related claims?"

---

### 2. Endorsements & Policy Modifications
**Why it matters:** Agents need to know what can be added or changed in policies

**What we extract:**
- Available endorsements/add-ons
- What each endorsement adds/removes
- Cost impact of endorsements
- Coverage impact on exclusions

**Agent questions answered:**
- "Can we add winter sports coverage to this policy?"
- "What does the 'golf equipment' endorsement cost?"
- "How does adding business equipment affect the excess?"

---

### 3. Claims Requirements & Process
**Why it matters:** Agents guide customers through claims - must know exact requirements

**What we extract:**
- Required documentation for claims
- Notification timeframes and deadlines
- Step-by-step claims process
- Evidence requirements (police reports, receipts, etc.)
- Claims contact information

**Agent questions answered:**
- "What documents does a customer need for a baggage claim?"
- "How quickly must we notify Aviva about a travel claim?"
- "Does the customer need a police report for theft?"

---

### 4. Eligibility Criteria
**Why it matters:** Avoid wasting time quoting ineligible customers

**What we extract:**
- Age limits and restrictions
- Medical conditions affecting eligibility
- Occupational restrictions
- Residency requirements
- Other eligibility restrictions

**Agent questions answered:**
- "Can a 75-year-old get this travel policy?"
- "Are offshore workers eligible for this policy?"
- "Do we need medical screening for this applicant?"

---

### 5. Policy Definitions
**Why it matters:** Reduces confusion and ensures consistent interpretation

**What we extract:**
- Key term definitions (immediate family, pre-existing condition, etc.)
- Policy-specific meanings of common terms
- Terms that differ between insurers

**Agent questions answered:**
- "Does 'extreme sports' include scuba diving for Zurich?"
- "Who counts as 'immediate family' under AXA policies?"
- "What's the definition of 'valuables' for baggage claims?"

---

### 6. Coverage Limits & Sub-Limits
**Why it matters:** Agents must quote accurate coverage amounts

**What we extract:**
- Main coverage limits by category
- Sub-limits (per-item, per-event)
- Aggregate limits
- Benefit schedules

**Agent questions answered:**
- "What's the maximum baggage claim under this policy?"
- "Is there a per-item limit for valuables?"
- "What's covered for medical expenses abroad?"

---

### 7. Time-Sensitive Requirements
**Why it matters:** Missing deadlines can invalidate claims

**What we extract:**
- Waiting periods before coverage starts
- Claims notification deadlines
- Cooling-off periods
- Cancellation notice requirements

**Agent questions answered:**
- "When does coverage start after purchase?"
- "Can the customer cancel in the cooling-off period?"
- "What's the deadline to notify about a missed flight?"

---

### 8. FCA Regulatory Compliance
**Why it matters:** Legal requirement and customer protection

**What we extract:**
- FCA-required disclosures
- IPID (Insurance Product Information Document) key points
- Fair treatment obligations
- Complaints process
- Regulatory warnings and notices

**Agent questions answered:**
- "What FCA disclosures must we provide?"
- "How does the customer make a complaint?"
- "What are the key IPID points for this policy?"

---

## FAQ Categories Generated

The system automatically creates FAQs in these categories:

1. **Exclusions** - General and specific exclusion questions
2. **Endorsements & Modifications** - What can be added/changed
3. **Claims Requirements** - Documentation and process
4. **Eligibility** - Who qualifies for coverage
5. **Policy Definitions** - Term meanings
6. **Coverage Limits** - Maximum payouts and sub-limits
7. **Comparisons** - Cross-insurer analysis
8. **Common Questions** - Policy-specific frequent questions

## Use Cases

### For Customer-Facing Agents
- Quick answers to "Does X cover Y?" questions
- Accurate claims guidance
- Eligibility screening before quoting
- Understanding policy terms to explain to customers

### For Compliance & Risk
- FCA disclosure tracking
- Exclusion oversight
- Claims process review
- Eligibility fairness assessment

### For Product Team
- Cross-insurer comparisons
- Coverage gap analysis
- Endorsement availability
- Market positioning insights

### For Training
- Onboarding new agents with policy knowledge
- Reference material for complex questions
- Consistent policy interpretation
- Regulatory requirement understanding

## Integration Points

### Intercom (Internal FAQs)
- Import structured FAQs as "Internal Only" articles
- Searchable by insurer, policy type, category
- Tagged for easy filtering
- Regular updates as policies change

### CRM Systems
- API-ready JSON exports
- Structured data for automation
- Eligibility checking
- Quote generation support

### AI-Powered Chat
- RAG (Retrieval Augmented Generation) enabled
- Natural language question answering
- Context-aware responses
- Source citations

## Benefits

### Efficiency
- Reduce time spent searching policy documents
- Instant answers to common questions
- Standardized responses across team

### Accuracy
- Information extracted directly from official policy wordings
- Consistent interpretation of terms
- Up-to-date with latest policy versions

### Compliance
- Track FCA requirements
- Document processes
- Fair treatment oversight
- Audit trail

### Customer Experience
- Faster quote turnaround
- Accurate information first time
- Confident agent interactions
- Reduced complaints from miscommunication

## Customization Options

You can customize:
- Which dimensions to extract (focus on what matters most)
- FAQ templates and formatting
- Export formats
- Search filters (by insurer, policy type, category)
- Compliance reporting focus areas

## Performance

**Initial Processing:**
- ~30-60 seconds per policy PDF
- One-time cost per policy

**FAQ Generation:**
- ~5-10 seconds for all FAQs
- Hundreds of FAQs per policy

**AI Search:**
- ~2-5 seconds per question
- Includes context from all policies

**Cost (Claude API):**
- ~£0.10-0.30 per policy (one-time)
- ~£0.01-0.05 per search query
- Pre-generated FAQs have zero ongoing cost
