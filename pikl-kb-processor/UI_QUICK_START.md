# Pikl KB Processor - Web UI Quick Start

**Get up and running with the visual interface in 2 minutes!**

---

## Launch the UI

### Option 1: Use the Quick Launch Script (Easiest)

```bash
cd pikl-kb-processor
./start_ui.sh
```

That's it! The UI will open automatically in your browser.

### Option 2: Manual Launch

```bash
# 1. Navigate to directory
cd pikl-kb-processor

# 2. Activate virtual environment
source venv/bin/activate

# 3. Launch Streamlit
streamlit run app.py
```

### Option 3: First Time Setup

If you haven't set up the project yet:

```bash
# 1. Run automated setup
./setup.sh

# 2. Configure API keys
nano .env.local
# Add:
# ANTHROPIC_API_KEY=your_key_here
# INTERCOM_ACCESS_TOKEN=your_token_here

# 3. Install UI dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Launch UI
./start_ui.sh
```

---

## What You'll See

When the UI loads, you'll see 6 pages in the left sidebar:

### 📊 Dashboard
**Your mission control** - See KB health metrics, coverage %, and system status at a glance.

### 📥 Data Ingestion
**Upload and process data** - Fetch KB articles, upload transcripts/emails, run processing.

### 🔍 Knowledge Gaps
**Review what's missing** - Browse all identified gaps, filter by priority, export for planning.

### ✏️ FAQ Review
**Approve AI-generated FAQs** - Review each FAQ candidate, approve/reject/edit decisions.

### 🚀 Publish to Intercom
**Go live** - Select approved FAQs and publish them to your Intercom help center.

### 📈 Analytics
**Measure impact** - Charts, trends, and export reports.

---

## Your First Session (10 minutes)

### Step 1: Check Connection (1 min)
1. Open **Dashboard** page
2. Verify "Intercom API: Connected" and "Claude API: Connected"
3. If not connected, check your `.env.local` file

### Step 2: Fetch Your KB (1 min)
1. Go to **Data Ingestion** page
2. Click **"Fetch KB Articles from Intercom"**
3. Wait for confirmation
4. You should see your article count on the Dashboard

### Step 3: Upload Sample Data (2 min)
1. Still on **Data Ingestion** page
2. Upload 5-10 transcripts (JSON/CSV) or emails (EML)
3. Click **"Upload"**
4. Verify files appear in the file list

### Step 4: Process Data (3-5 min)
1. Click **"Process All Data"** button
2. Watch the progress bar
3. See live logs of processing steps
4. Wait for "Processing Complete!" message

### Step 5: Review Results (2 min)
1. Go to **Dashboard** - see updated metrics
2. Go to **Knowledge Gaps** - browse identified gaps
3. Go to **FAQ Review** - see AI-generated FAQ candidates

### Step 6: Approve & Publish (2 min)
1. On **FAQ Review** page, review a few FAQs
2. Click **Approve** on ones that look good
3. Go to **Publish to Intercom** page
4. Select approved FAQs
5. Choose "Create as Drafts" (safe option)
6. Click **"Publish to Intercom"**
7. Go to Intercom to see your new draft articles!

---

## Tips for Success

### ✅ Do This:
- Start with 10-20 items for your first run (fast feedback)
- Always create as drafts first (safe to review before publishing)
- Read the AI notes on FAQs - they flag what needs verification
- Replace placeholders like `[PHONE NUMBER]` before publishing
- Use filters on Knowledge Gaps page to find high-priority items

### ❌ Avoid This:
- Don't upload hundreds of files on first try (start small)
- Don't publish immediately without review (use drafts first)
- Don't ignore validation warnings
- Don't skip verifying policy-specific details

---

## Common Questions

**Q: Can I close the terminal while the UI is running?**
A: No, the UI runs in the terminal. Closing it will stop the UI. Keep the terminal window open.

**Q: How do I stop the UI?**
A: Press `Ctrl+C` in the terminal where it's running.

**Q: Can multiple people use it at once?**
A: Each person needs to run their own instance (`./start_ui.sh` on their machine). Session state is per-user.

**Q: Does the CLI still work?**
A: Yes! CLI and UI both work. Use whichever you prefer. CLI is better for automation, UI is better for humans.

**Q: Where are the generated files saved?**
A: Reports go to `./reports/`, uploaded data stays in `./data/`.

**Q: What if I get errors?**
A: Check:
1. Are your API keys in `.env.local`?
2. Is the virtual environment activated?
3. Did you run `pip install -r requirements.txt`?
4. See [UI_GUIDE.md](UI_GUIDE.md) for detailed troubleshooting

---

## What's Next?

### For Team Collaboration
Share this with your team:
1. **Product/Support Teams:** Use **Knowledge Gaps** page to understand customer pain points
2. **Content Team:** Use **FAQ Review** page to polish AI-generated drafts
3. **Leadership:** Use **Analytics** page for reporting

### For Regular Use
Set up a monthly rhythm:
1. **Week 1:** Process new transcripts/emails
2. **Week 2:** Team review of FAQs
3. **Week 3:** Verify and polish
4. **Week 4:** Publish and measure impact

### Learn More
- **[UI_GUIDE.md](UI_GUIDE.md)** - Complete UI user guide (page-by-page walkthrough)
- **[README.md](README.md)** - Full project documentation
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - CLI usage for advanced users

---

## Troubleshooting Quick Fixes

**UI won't start**
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

**"ModuleNotFoundError"**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
# Then launch again
./start_ui.sh
```

**"Connection Error"**
```bash
# Check your API keys
cat .env.local
# Should show ANTHROPIC_API_KEY and INTERCOM_ACCESS_TOKEN
```

**Port already in use**
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

---

**Ready to transform your knowledge base?** 🚀

Run `./start_ui.sh` and get started!
