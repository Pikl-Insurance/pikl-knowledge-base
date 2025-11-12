# Pikl KB Processor - Web UI Guide

**A visual, team-friendly interface for knowledge base management**

---

## Why Use the Web UI?

The Web UI makes the Pikl KB Processor accessible to your entire team:

- ✅ **No command line knowledge needed** - Visual interface for all operations
- ✅ **Perfect for team reviews** - Collaborative FAQ approval workflow
- ✅ **Real-time visibility** - See processing status and metrics live
- ✅ **Easy data upload** - Drag-and-drop file uploads
- ✅ **Visual reporting** - Charts and graphs for insights
- ✅ **Streamlined publishing** - One-click publishing to Intercom

**Perfect for:** Product managers, support team leads, content strategists, marketing teams

---

## Getting Started

### Prerequisites

1. **Python 3.9+** installed
2. **API credentials** configured in `.env.local`:
   ```env
   ANTHROPIC_API_KEY=your_key_here
   INTERCOM_ACCESS_TOKEN=your_token_here
   ```

### Launch the UI

```bash
# 1. Navigate to the project directory
cd pikl-kb-processor

# 2. Activate the virtual environment
source venv/bin/activate

# 3. Install dependencies (first time only)
pip install -r requirements.txt

# 4. Launch the Web UI
streamlit run app.py
```

The UI will automatically open in your browser at `http://localhost:8501`

### First Time Setup

When you first launch the UI:

1. **Test your connection** - The dashboard will show your Intercom connection status
2. **Fetch your KB** - Click "Fetch KB Articles" to import your existing knowledge base
3. **Upload data** - Go to "Data Ingestion" to upload transcripts and emails

---

## Page-by-Page Guide

### 📊 Dashboard

**Purpose:** Overview of your knowledge base health and recent activity

**What you'll see:**
- **Metrics cards:**
  - Total KB articles
  - Number of knowledge gaps identified
  - Coverage percentage
  - FAQ candidates generated

- **System Status:**
  - Intercom API connection status
  - Claude API connection status
  - Last processing run timestamp

- **Recent Activity:**
  - Processing history
  - Published FAQ count
  - Recent changes

**Quick Actions:**
- View full reports
- Jump to FAQ review
- Access analytics

---

### 📥 Data Ingestion

**Purpose:** Upload and process customer data

#### Step 1: Fetch KB Articles

1. Click **"Fetch KB Articles from Intercom"**
2. Wait for the fetch to complete
3. Review article count and success message
4. Articles are saved to `./data/kb_articles.json`

**Tip:** You only need to fetch KB articles once per session, or when your KB has been updated.

#### Step 2: Upload Transcripts

**Supported formats:** JSON, JSONL, CSV

1. Click **"Browse files"** under Transcripts section
2. Select one or multiple transcript files
3. Files can be in folders or individual files
4. Click **"Upload"**

**Expected format:**
```json
{
  "id": "call_001",
  "turns": [
    {"speaker": "customer", "text": "How do I...?"},
    {"speaker": "agent", "text": "You can..."}
  ]
}
```

#### Step 3: Upload Emails

**Supported formats:** EML, MSG

1. Click **"Browse files"** under Emails section
2. Select one or multiple email files
3. Emails are automatically parsed
4. Click **"Upload"**

**How to export:**
- **Outlook:** File > Save As > EML Format
- **Gmail:** Download email > EML option

#### Step 4: Process Data

1. Verify your uploaded files are shown
2. Click **"Process All Data"**
3. Watch the live progress bar
4. Review processing logs in real-time
5. Wait for completion message

**Processing includes:**
- PII anonymization (automatic)
- Q&A extraction using Claude
- Semantic matching to KB articles
- Knowledge gap identification
- FAQ candidate generation

**Time estimates:**
- 10 transcripts: ~2-3 minutes
- 50 emails: ~1-2 minutes
- 100+ items: ~10-15 minutes

---

### 🔍 Knowledge Gaps Analysis

**Purpose:** Review identified gaps in your knowledge base

**Features:**

#### Filters
- **Priority:** All / High / Medium / Low
- **Theme:** All / General / Policy / Quote / Renewal / Contact / Other
- **Search:** Free-text search across questions

#### Gap List
Each gap shows:
- **Question** - What customers are asking
- **Priority** - Urgency score (High/Medium/Low)
- **Theme** - Categorization
- **Source** - Which transcript/email it came from
- **Best Match** - Closest existing KB article (if any)
- **Similarity Score** - How close the match is

#### Actions
- **Sort** by priority, theme, or similarity
- **Export** gaps to CSV for offline review
- **View details** - Click any gap for full context

**Use Cases:**
- Identify highest-priority content to create
- Understand customer pain points by theme
- Find patterns in unaddressed questions
- Share with content team for planning

---

### ✏️ FAQ Review & Approval

**Purpose:** Review and approve AI-generated FAQ candidates

**Workflow:**

#### 1. Browse FAQs
- FAQs are shown one at a time for focused review
- Navigate with **Previous/Next** buttons
- See progress (e.g., "FAQ 5 of 50")

#### 2. Review Each FAQ
Each FAQ displays:
- **Main Question** - Clear, customer-facing question
- **Question Variants** - Alternative phrasings for better search
- **Answer** - AI-generated comprehensive answer
- **Category** - Suggested categorization
- **Tags** - Keywords for discoverability
- **Priority Score** - Importance (0.0-1.0)
- **AI Notes** - Verification needed, placeholders to replace

#### 3. Make a Decision

**✅ Approve**
- Answer is accurate and ready to publish
- May need minor editing (tone, placeholders)
- Will be included in publishing queue

**✏️ Edit**
- Answer needs adjustments but is salvageable
- Content team should refine before publishing
- Mark for editorial review

**❌ Reject**
- Not relevant or incorrect
- Won't be included in publishing
- Can add rejection reason

**🔍 Needs Research**
- Can't verify accuracy without research
- Assign to subject matter expert
- Defer decision until verified

#### 4. Bulk Actions
- **Approve all high-priority** - Quick-approve top FAQs
- **Reject duplicates** - Remove redundant content
- **Export selections** - Share with team for offline review

#### 5. Track Status
- View approval counts by status
- Filter by approval status
- See what's ready to publish

**Best Practices:**
- ✅ Look for `[PLACEHOLDER]` text that needs replacing
- ✅ Verify specific amounts, dates, phone numbers
- ✅ Check tone matches your brand voice
- ✅ Confirm information is current
- ⚠️ Don't publish without verifying policy details
- ⚠️ Don't skip AI notes - they flag uncertainty

---

### 🚀 Publish to Intercom

**Purpose:** Publish approved FAQs directly to your Intercom help center

**Safety Features:**
- Creates as **drafts by default**
- Confirmation prompt before publishing
- Rate-limited to avoid API throttling
- Rollback capability (unpublish in Intercom)

**Steps:**

#### 1. Select FAQs to Publish
- View all approved FAQs
- Select individual FAQs or **"Select All Approved"**
- Review total count

#### 2. Configure Publishing Options

**Author ID** (optional)
- Specify Intercom admin ID for attribution
- Defaults to API token owner if not specified

**Publish Mode**
- ☐ **Create as Drafts** (default, recommended)
  - Creates articles but doesn't publish
  - Allows final review in Intercom before going live
  - No customer impact until manually published

- ☑ **Publish Immediately**
  - Articles go live instantly
  - Customers can see them right away
  - Use only if FAQs are fully verified

#### 3. Review Before Publishing

The UI shows:
- Number of FAQs to be created
- List of titles
- Publishing mode (draft/published)
- Confirmation checkbox

#### 4. Publish

1. Click **"Publish to Intercom"**
2. Confirm the action
3. Watch live progress bar
4. Review results:
   - ✅ Successfully created
   - ⚠️ Warnings (if any)
   - ❌ Errors (if any)

#### 5. Post-Publishing

**If created as drafts:**
1. Log into Intercom
2. Go to Articles
3. Find your new draft articles
4. Review and publish when ready

**If published immediately:**
1. Test search in your help center
2. Verify articles display correctly
3. Monitor analytics for views/feedback

**Troubleshooting:**
- **404 errors:** Check Intercom API token permissions
- **Rate limit errors:** Reduce batch size, wait and retry
- **Validation errors:** Check for required fields

---

### 📈 Analytics & Reporting

**Purpose:** Visual insights and data exports

**Charts Available:**

#### Knowledge Gaps by Theme
- Pie chart showing gap distribution
- Identify which themes need most content
- Click segments for drill-down

#### Priority Distribution
- Bar chart of gaps by priority level
- See how many high-priority gaps exist
- Plan content roadmap

#### Coverage Over Time
- Line chart showing KB coverage improvement
- Track progress month-over-month
- Measure impact of new content

#### Top Unaddressed Questions
- Table of most frequently asked gaps
- Sort by frequency or priority
- Quick-win opportunities

**Export Options:**

#### Download Reports
- **Markdown Report** - Human-readable analysis
- **Knowledge Gaps CSV** - All gaps for spreadsheet review
- **FAQ Candidates JSON** - Structured data for import
- **Summary Report JSON** - Statistics and metrics

**Use Cases:**
- Monthly stakeholder reporting
- Content planning sessions
- ROI demonstration
- Process improvement analysis

---

## Common Workflows

### Workflow 1: Monthly KB Update

**Goal:** Process new customer data and publish updates monthly

1. **Week 1, Day 1:**
   - Upload new transcripts/emails (Data Ingestion page)
   - Process data
   - Review dashboard metrics

2. **Week 1, Days 2-3:**
   - Review knowledge gaps (Knowledge Gaps page)
   - Share gap list with support team
   - Prioritize top 20 gaps

3. **Week 2:**
   - Review FAQ candidates (FAQ Review page)
   - Approve/Edit/Reject each FAQ
   - Assign research tasks for uncertain FAQs

4. **Week 3:**
   - Finalize approved FAQs
   - Replace placeholders
   - Verify all details

5. **Week 4:**
   - Publish approved FAQs as drafts (Publish page)
   - Final review in Intercom
   - Publish live
   - Monitor analytics

### Workflow 2: One-Time KB Audit

**Goal:** Comprehensive one-time analysis to identify all gaps

1. **Preparation:**
   - Collect 3-6 months of transcript/email data
   - Ensure API keys are configured

2. **Processing (Day 1):**
   - Fetch current KB articles
   - Upload all historical data
   - Run full processing (may take hours)
   - Let it run overnight if needed

3. **Analysis (Days 2-3):**
   - Review analytics for insights
   - Export gap list to CSV
   - Present findings to leadership

4. **Content Planning (Week 2):**
   - Review FAQ candidates with team
   - Categorize by priority
   - Assign owners for verification

5. **Publishing (Weeks 3-4):**
   - Batch 1: Top 20 FAQs (quick wins)
   - Batch 2: Next 30 FAQs
   - Ongoing: Remaining as verified

### Workflow 3: Weekly Team Review

**Goal:** Collaborative weekly session to review new FAQs

1. **Before Meeting:**
   - Process week's data
   - Generate FAQ candidates
   - Share UI link with team

2. **During Meeting (60 min):**
   - Present dashboard (5 min)
   - Review top knowledge gaps (10 min)
   - Go through FAQ candidates together (40 min)
     - Support lead verifies accuracy
     - Content person checks tone
     - Product person flags process issues
   - Make approve/reject decisions (5 min)

3. **After Meeting:**
   - Publish approved FAQs as drafts
   - Assign research tasks for uncertain FAQs
   - Schedule follow-up

---

## Tips & Best Practices

### Performance
- ⚡ Process data in batches of 50-100 items for optimal speed
- ⚡ Use "Fetch KB" once per session, not repeatedly
- ⚡ Large datasets (500+ items) may take 30+ minutes

### Accuracy
- ✅ Always verify AI-generated answers before publishing
- ✅ Replace `[PHONE NUMBER]` and other placeholders
- ✅ Read the AI notes - they flag what needs checking
- ✅ Test published articles from a customer perspective

### Collaboration
- 👥 Share the UI URL with your team (works on local network)
- 👥 Use Analytics page for presentations
- 👥 Export gap lists for offline discussion
- 👥 Assign FAQ review to subject matter experts

### Publishing Strategy
- 🎯 Start with 20 high-priority FAQs (quick wins)
- 🎯 Always create as drafts first for review
- 🎯 Publish in batches, monitor impact
- 🎯 Use Intercom analytics to see what customers search for

### Data Management
- 📁 Keep transcripts/emails organized by date
- 📁 Archive processed data monthly
- 📁 Re-run analysis quarterly to track improvement
- 📁 Export reports for record-keeping

---

## Troubleshooting

### UI Won't Load
**Problem:** Browser shows connection error

**Solutions:**
1. Check terminal for error messages
2. Ensure virtual environment is activated
3. Verify port 8501 isn't in use: `lsof -i :8501`
4. Try a different port: `streamlit run app.py --server.port 8502`

### API Connection Errors
**Problem:** Dashboard shows "Disconnected" for Intercom/Claude

**Solutions:**
1. Check `.env.local` has correct API keys
2. Verify API keys are valid (not expired)
3. Test keys using CLI: `python cli.py test-intercom`
4. Check network/firewall isn't blocking API calls

### File Upload Fails
**Problem:** Files upload but show error

**Solutions:**
1. Check file format matches expected (JSON/JSONL/CSV for transcripts, EML/MSG for emails)
2. Verify JSON is valid (use JSONLint)
3. Check files aren't corrupted
4. Try smaller batch (10 files at a time)

### Processing Hangs
**Problem:** Processing starts but never finishes

**Solutions:**
1. Check terminal for error messages
2. Monitor API rate limits (Claude/Intercom)
3. Try smaller batch size
4. Restart UI and try again
5. Check if API keys hit usage limits

### FAQs Won't Publish
**Problem:** Publishing returns errors

**Solutions:**
1. Verify Intercom token has "Write Articles" permission
2. Check if articles already exist (duplicates)
3. Ensure required fields aren't empty
4. Try publishing one FAQ at a time to isolate issue
5. Check Intercom API status page

### Changes Don't Persist
**Problem:** Approved FAQs reset after refresh

**Solutions:**
1. Session state is temporary - export approved FAQs before closing
2. Publishing to Intercom persists permanently
3. Future enhancement: Add database for persistence

---

## Keyboard Shortcuts

- **`Ctrl + R`** - Refresh the page
- **`Ctrl + Shift + R`** - Hard refresh (clear cache)
- **`F11`** - Toggle fullscreen
- **`Ctrl + F`** - Search on page

---

## Security Notes

### Data Privacy
- ✅ All PII is automatically anonymized before Claude API calls
- ✅ Original transcripts/emails stay on your local system
- ✅ No customer data is stored in the cloud
- ✅ See [PII_ANONYMIZATION.md](PII_ANONYMIZATION.md) for details

### Access Control
- 🔒 UI runs locally (localhost) - not accessible from internet
- 🔒 API keys stored in `.env.local` (never committed to Git)
- 🔒 Intercom publishing uses your personal API token
- 🔒 For team access, consider deploying to internal server with authentication

---

## Updating the UI

When new features are added:

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt

# Restart the UI
streamlit run app.py
```

---

## Feedback & Issues

Found a bug or have a feature request?

1. **For urgent issues:** Contact John (tool creator)
2. **For feature requests:** Create GitHub issue (if available)
3. **For usage questions:** See [USAGE_GUIDE.md](USAGE_GUIDE.md)

---

## FAQ About the UI

**Q: Can multiple people use the UI at once?**
A: Yes, but they need to run their own instance (`streamlit run app.py`). Session state is per-user. For true collaboration, consider deploying to a shared server.

**Q: Does the UI work on mobile?**
A: Partially. Streamlit is responsive but best experienced on desktop/tablet. Some features may be hard to use on phone.

**Q: Can I customize the UI?**
A: Yes! `app.py` is fully editable. Streamlit uses Python, so you can modify pages, add features, or change styling.

**Q: Is the UI required, or can I still use CLI?**
A: Both work! CLI is faster for automation/scripts. UI is better for humans. Use whichever fits your workflow.

**Q: How do I deploy this for my team?**
A: For team access:
1. Deploy to internal server (Linux VM, Docker)
2. Use Streamlit Community Cloud (public hosting)
3. Set up authentication if exposing publicly
4. See Streamlit deployment docs: https://docs.streamlit.io/deploy

**Q: Can I schedule automatic processing?**
A: Use the CLI with cron for automation. UI is for interactive use. See [USAGE_GUIDE.md](USAGE_GUIDE.md#automation) for cron examples.

---

## Next Steps

1. ✅ **Launch the UI** - `streamlit run app.py`
2. ✅ **Process your first batch** - Upload 10 transcripts as a test
3. ✅ **Review FAQs** - Go through the approval workflow
4. ✅ **Publish a draft** - Test the Intercom integration
5. ✅ **Share with your team** - Get feedback and iterate

**Happy knowledge base building!** 🚀

---

**Related Documentation:**
- [README.md](README.md) - Project overview
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - CLI usage
- [INTERCOM_PUBLISHING.md](INTERCOM_PUBLISHING.md) - Publishing guide
- [PII_ANONYMIZATION.md](PII_ANONYMIZATION.md) - Privacy details
