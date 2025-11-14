# Issues Fixed: Internal Articles & Formatting

## Problems Identified

1. **❌ Articles showing as "Public article" instead of "Internal article"**
2. **❌ Markdown formatting not rendering (showing as plain text in one block)**

## Root Causes Discovered

### Issue 1: Wrong API Endpoint
**Problem:** We were using `/articles` endpoint, which creates public Help Center articles.

**Solution:** Intercom has TWO separate endpoints:
- `/articles` → Creates **public** Help Center articles
- `/internal_articles` → Creates **internal** team-only articles

We needed to use the `/internal_articles` endpoint with the `Intercom-Version: Unstable` header.

### Issue 2: Wrong Body Format
**Problem:** We were sending Markdown text, but Intercom's internal articles expect HTML.

**Solution:** Looking at existing internal articles in your account, the body is HTML with specific formatting:
```html
<h1>Section Header</h1>
<p class="no-margin">Paragraph text</p>
<b>Bold text</b>
<i>Italic text</i>
```

We needed to:
1. Convert Markdown to HTML
2. Wrap paragraphs in `<p class="no-margin">` tags (Intercom's format)

## Fixes Applied

### 1. New Import Script: `intercom_import_internal.py`

**Key changes:**
- Uses `/internal_articles` endpoint instead of `/articles`
- Adds `"Intercom-Version": "Unstable"` header
- Converts Markdown to HTML using `markdown2` library
- Wraps paragraphs in `<p class="no-margin">` format
- Includes `owner_id` parameter (required for internal articles)

### 2. Added markdown2 Dependency

Updated `requirements.txt`:
```
anthropic>=0.39.0
requests>=2.31.0
markdown2>=2.5.0
```

## Test Results

✅ **Successfully created 3 test internal articles:**
- Article ID: 5622171
- Article ID: 5622172
- Article ID: 5622173

✅ **Verified proper HTML formatting:**
```html
<h1>Quick Answer</h1>
<p class="no-margin">AXA Home Insurance excludes...</p>
<h1>What This Means for Your Customer</h1>
<p class="no-margin">These exclusions mean...</p>
```

✅ **Confirmed internal article attributes:**
- Uses `/internal_articles` endpoint
- Includes `owner_id` and `author_id`
- Created via Unstable API version

## Check in Intercom

Please verify in your Intercom dashboard:

1. **Go to these articles:**
   - Search for article ID: 5622171, 5622172, or 5622173

2. **Confirm "Internal article" type:**
   - Should show "🔒 Internal article" (not "Public article")
   - Located in the article metadata/data panel

3. **Verify formatting:**
   - Headers should be large and bold
   - Bullet points should display properly
   - Sections should be clearly separated
   - Example phrases should be in blockquotes
   - No raw markdown symbols (no `##`, `**`, etc.)

## Comparison: Before vs After

### Before (Wrong):
```
Endpoint: /articles
API Version: 2.10
Body Format: Markdown text
Result:
- Type shows as "Public article"
- Content displays as plain text block
- ## headers visible as text
- ** bold markers visible
```

### After (Correct):
```
Endpoint: /internal_articles
API Version: Unstable
Body Format: HTML
Result:
- Type shows as "Internal article"
- Content properly formatted
- Headers display large/bold
- Bullet points render correctly
```

## Next Steps

### If Articles Look Good in Intercom:

1. **Clean up old test articles:**
   - Delete the previous test collections/articles (the public ones)
   - Keep only the new internal articles

2. **Enhance more FAQs:**
   ```bash
   # Enhance 20 more FAQs for testing
   ANTHROPIC_API_KEY="your-key" ../venv/bin/python enhance_faqs_for_agents.py 20
   ```

3. **Import enhanced batch:**
   ```bash
   # Test with 20 enhanced FAQs
   INTERCOM_ACCESS_TOKEN="your-token" ../venv/bin/python intercom_import_internal.py
   ```
   (Update script to load first 20 enhanced FAQs)

4. **Review in Intercom:**
   - Check formatting across different FAQ types
   - Test search functionality
   - Get agent feedback

5. **Full enhancement + import:**
   When ready, enhance all 1,441 FAQs and import them

### If Issues Remain:

Let me know specifically:
- Are they showing as "Internal article" now?
- Is the formatting displaying correctly?
- Any specific rendering issues?
- Screenshots would be helpful

## Files Created/Modified

### New Files:
- `scripts/intercom_import_internal.py` - Correct internal article import
- `FIXES_APPLIED.md` - This document

### Modified Files:
- `requirements.txt` - Added markdown2 dependency

### Obsolete Files (can keep for reference):
- `scripts/intercom_import_test.py` - Uses wrong endpoint
- `scripts/intercom_import_enhanced.py` - Uses wrong endpoint
- `scripts/intercom_import_full.py` - Uses wrong endpoint

## Technical Details

### Internal Articles API

**Endpoint:** `POST https://api.intercom.io/internal_articles`

**Headers:**
```
Authorization: Bearer {token}
Accept: application/json
Content-Type: application/json
Intercom-Version: Unstable
```

**Required Payload:**
```json
{
  "title": "Article title",
  "description": "Short description",
  "body": "<h1>HTML content</h1>",
  "author_id": 9277214,
  "owner_id": 9277214,
  "state": "published",
  "translated_content": {
    "en": {
      "title": "Article title",
      "description": "Short description",
      "body": "<h1>HTML content</h1>",
      "author_id": 9277214
    }
  }
}
```

### HTML Format

Intercom uses specific HTML structure:
- Headers: `<h1>`, `<h2>`, etc.
- Paragraphs: `<p class="no-margin">`
- Bold: `<b>` or `<strong>`
- Italic: `<i>` or `<em>`
- Bullets: `<ul><li>`
- Horizontal rules: `<hr>`
- Blockquotes: `<blockquote>`

## Summary

✅ **Root causes identified and fixed**
✅ **Proper endpoint now used** (`/internal_articles`)
✅ **HTML formatting implemented**
✅ **3 test articles successfully created**
⏳ **Awaiting your confirmation from Intercom UI**

Once confirmed working, we can proceed with full-scale enhancement and import of all 1,441 FAQs!
