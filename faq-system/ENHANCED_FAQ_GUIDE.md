# Enhanced Agent-Friendly FAQ System

## Overview

I've redesigned your FAQ system to be truly agent-friendly. Instead of just technical policy information, each FAQ now includes practical guidance that agents can directly use when communicating with customers.

## What's New: Enhanced FAQ Format

Each enhanced FAQ now includes:

### 1. **Quick Answer**
- Concise 2-3 sentence summary
- Direct, clear response agents can quickly scan

### 2. **What This Means for Your Customer**
- Plain-language explanation of practical implications
- Helps agents understand the "so what?" for customers
- Context about how it affects their coverage

### 3. **How to Communicate This**
- 2-3 example phrases/scripts agents can actually use
- Natural, empathetic language
- Ready-to-use in phone or email responses

### 4. **Common Follow-up Questions**
- 2-3 typical questions customers ask
- Brief answers for each
- Helps agents anticipate and prepare

### 5. **Important Notes for Agents**
- Critical details to remember
- Exceptions, time limits, documentation requirements
- Things that could cause problems if overlooked

## Example: Before vs After

### BEFORE (Original):
```
Question: Does AXA Insurance UK plc Home Insurance exclude terrorism?

Answer: Yes, AXA Insurance UK plc's Home Insurance policy excludes:
• War, terrorism, radioactive contamination, sonic bangs
```

### AFTER (Enhanced):
```
## Quick Answer
Yes, AXA Home Insurance does exclude damage caused by terrorism, along with war,
radioactive contamination, and sonic bangs. This is a standard exclusion across
most home insurance policies in the UK.

## What This Means for Your Customer
This means that if your home or belongings are damaged as a direct result of a
terrorist act, this damage would not be covered under your AXA Home Insurance policy.
However, it's important to note that the government-backed Pool Re scheme provides
terrorism coverage for commercial properties...

## How to Communicate This
Example 1: "Your AXA Home Insurance covers you for the everyday risks you're most
likely to face - things like fire, theft, storm damage, and accidental damage.
Terrorism is one of the standard exclusions across home insurance policies..."

Example 2: "I can confirm that acts of terrorism are excluded from your coverage,
along with war and radioactive contamination. These are standard exclusions in the
insurance industry. The good news is that your policy protects you against all the
common risks to your home..."

## Common Follow-up Questions
Q: Why isn't terrorism covered if I'm paying for comprehensive insurance?
A: Terrorism is excluded because these events are unpredictable and could result in
catastrophic losses across many policies simultaneously...

Q: What happens if there's a terrorist attack in my area?
A: Direct damage from terrorism wouldn't be covered. However, if your home is damaged
by a covered peril that occurs as an indirect result...

## Important Notes for Agents
• This exclusion is standard across the UK home insurance industry, not unique to AXA
• Don't make assumptions about what is or isn't related to terrorism - refer complex
  scenarios to claims teams
• Customers in high-profile locations may have heightened concerns - be empathetic
  and focus on the comprehensive coverage they do have
```

## How Articles Appear in Intercom

The enhanced format is beautifully formatted in Intercom with:
- Clear section headers
- Blockquotes for example scripts
- Bullet points for important notes
- Policy details at the bottom for reference

**Check it out:** https://intercom.help/pikl/en/collections/16646535

## Making Articles "Internal Only"

I noticed the test articles are showing as "Public" instead of "Internal". Here's how to fix this:

### In Intercom:
1. Go to **Help Center → Collections**
2. Find the collection (e.g., "[TEST] Enhanced Policy Knowledge")
3. Click the collection settings (gear icon)
4. Under **Visibility**, select **"Team only"**
5. Save changes

**All articles in that collection will now be internal/team-only.**

### For New Imports:
- Collections are named with `[INTERNAL]` prefix to remind you
- Descriptions include "⚠️ INTERNAL USE ONLY" warnings
- You must manually set visibility to "Team only" after import

## Next Steps

### Step 1: Review the Test Import
Check out the 5 enhanced articles I just imported:
- Collection: "[TEST] Enhanced Policy Knowledge"
- URL: https://intercom.help/pikl/en/collections/16646535
- **Set this collection to "Team only"**

Review:
- Is the format helpful for agents?
- Are the communication examples useful?
- Does the structure make sense?
- Any improvements needed?

### Step 2: Enhance All FAQs
Once you're happy with the format, enhance all 1,441 FAQs:

```bash
cd faq-system/scripts
export ANTHROPIC_API_KEY="your-key"
../venv/bin/python enhance_faqs_for_agents.py
```

**Important notes:**
- This will use API credits (approximately 1,441 API calls)
- Takes about 15-20 minutes with rate limiting
- Saves progress every 10 FAQs
- Can be resumed if interrupted

**Cost estimate:** ~$30-40 in API credits (at current Sonnet rates)

### Step 3: Import Enhanced FAQs to Intercom

Create a full import script for all enhanced FAQs:

```bash
cd faq-system/scripts
export INTERCOM_ACCESS_TOKEN="your-token"
export ANTHROPIC_API_KEY="your-key"
../venv/bin/python intercom_import_full_enhanced.py
```

This will:
- Create main collection: "[INTERNAL] Policy Knowledge Base"
- Create 8 sub-collections (Exclusions, Claims, etc.)
- Import all 1,441 enhanced FAQs
- Import as drafts for review

**Time estimate:** 15-20 minutes

### Step 4: Set Up in Intercom
1. Set main collection to **"Team only"** visibility
2. Review sample articles from each category
3. Publish articles when ready
4. Configure search/navigation
5. Train agents on new format

## Files Created

### Scripts:
- `enhance_faqs_for_agents.py` - Adds agent-friendly context to FAQs
- `intercom_import_enhanced.py` - Imports enhanced FAQs to Intercom
- `intercom_import_full_enhanced.py` - Full import of all enhanced FAQs (to be created)

### Data:
- `data/internal_faqs.json` - Original FAQs (1,441 entries)
- `data/internal_faqs_enhanced.json` - Enhanced FAQs with agent context
- `data/intercom_import_progress.json` - Import progress tracking

## Benefits for Your Team

### For Agents:
✅ **Quick answers** - Get to the point fast
✅ **Customer language** - Ready-to-use phrases for emails/calls
✅ **Context** - Understand why something matters
✅ **Preparation** - Know what customers will ask next
✅ **Confidence** - Important notes prevent mistakes

### For Customers:
✅ **Consistent messaging** - All agents use clear, approved language
✅ **Better explanations** - Agents understand context, not just facts
✅ **Faster resolution** - Agents have answers and scripts ready
✅ **Empathetic communication** - Scripts are designed to be customer-friendly

### For You:
✅ **Quality control** - Standardized responses across team
✅ **Training tool** - New agents learn proper communication style
✅ **Reduced errors** - Important notes catch common mistakes
✅ **Scalability** - Knowledge base that actually gets used

## Maintenance

### Updating FAQs:
When policies change:
1. Update policy PDFs in `policy-wordings/raw/`
2. Re-run: `python parse_policies.py`
3. Re-run: `python generate_faqs.py`
4. Re-run: `python enhance_faqs_for_agents.py`
5. Update affected articles in Intercom (or re-import)

### Improving Enhancement:
If you want to adjust the enhancement format:
1. Edit `ENHANCEMENT_PROMPT` in `enhance_faqs_for_agents.py`
2. Test on a sample: `python enhance_faqs_for_agents.py 5`
3. Review output in `data/internal_faqs_enhanced.json`
4. When happy, run on all FAQs

## Support

### Common Issues:

**"Articles showing as Public instead of Internal"**
- Solution: Set collection visibility to "Team only" in Intercom settings

**"Enhancement script fails"**
- Check: ANTHROPIC_API_KEY is set correctly
- Check: You have API credits available
- Check: Internet connection is stable

**"Import creates duplicate articles"**
- Check: Progress file - imports resume from where they left off
- To start fresh: Delete `data/intercom_import_progress.json`

**"Articles look wrong in Intercom"**
- Markdown formatting might differ between preview and published
- Publish one article to see final formatting
- Adjust `format_enhanced_article_body()` in import script if needed

## Summary

**What we've done:**
✅ Enhanced 5 sample FAQs with agent-friendly content
✅ Imported them to Intercom for your review
✅ Created scripts to enhance all 1,441 FAQs
✅ Set up process for full import

**What you need to do:**
1. Review the 5 test articles in Intercom: https://intercom.help/pikl/en/collections/16646535
2. Set test collection to "Team only" visibility
3. Provide feedback on format/content
4. Approve enhancement of all FAQs (~$35 in API costs)
5. Approve full import to Intercom

**Ready to proceed?** Let me know your thoughts on the enhanced format, and I'll run the full enhancement + import process!
