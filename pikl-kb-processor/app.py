"""Streamlit UI for Pikl KB Processor."""

import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from rich.console import Console

# Page config
st.set_page_config(
    page_title="Pikl KB Processor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
    }
    .success-box {
        padding: 15px;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        padding: 15px;
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-box {
        padding: 15px;
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'kb_articles' not in st.session_state:
    st.session_state.kb_articles = None
if 'knowledge_gaps' not in st.session_state:
    st.session_state.knowledge_gaps = None
if 'faq_candidates' not in st.session_state:
    st.session_state.faq_candidates = None
if 'faq_statuses' not in st.session_state:
    st.session_state.faq_statuses = {}

# Sidebar navigation
st.sidebar.title("🎯 Pikl KB Processor")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "📥 Data Ingestion", "🔍 Knowledge Gaps",
     "✏️ FAQ Review", "🚀 Publish to Intercom", "📈 Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛡️ Privacy")
st.sidebar.info("PII anonymization is **enabled** by default")

st.sidebar.markdown("### 📚 Documentation")
st.sidebar.markdown("[Quick Start](QUICKSTART.md)")
st.sidebar.markdown("[User Guide](USAGE_GUIDE.md)")
st.sidebar.markdown("[Privacy Info](PII_ANONYMIZATION.md)")

# Helper functions
def load_kb_articles():
    """Load KB articles from file."""
    kb_path = Path("data/kb_articles.json")
    if kb_path.exists():
        with open(kb_path) as f:
            return json.load(f)
    return None

def load_knowledge_gaps():
    """Load knowledge gaps from CSV."""
    gaps_path = Path("reports/knowledge_gaps.csv")
    if gaps_path.exists():
        return pd.read_csv(gaps_path)
    return None

def load_faq_candidates():
    """Load FAQ candidates from JSON."""
    faq_path = Path("reports/faq_candidates.json")
    if faq_path.exists():
        with open(faq_path) as f:
            return json.load(f)
    return None

def count_files_in_dir(directory, extensions):
    """Count files with given extensions in directory."""
    if not Path(directory).exists():
        return 0
    count = 0
    for ext in extensions:
        count += len(list(Path(directory).glob(f"**/*{ext}")))
    return count

# Main content based on selected page
if page == "📊 Dashboard":
    st.title("📊 Knowledge Base Dashboard")
    st.markdown("Welcome to the Pikl KB Processor - your AI-powered knowledge management system")

    # Load data
    kb_articles = load_kb_articles()
    knowledge_gaps = load_knowledge_gaps()
    faq_candidates = load_faq_candidates()

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kb_count = len(kb_articles) if kb_articles else 0
        st.metric("📚 KB Articles", kb_count)

    with col2:
        gap_count = len(knowledge_gaps) if knowledge_gaps is not None else 0
        st.metric("🔍 Knowledge Gaps", gap_count)

    with col3:
        coverage = 0.0
        if knowledge_gaps is not None and len(knowledge_gaps) > 0:
            good_matches = len(knowledge_gaps[knowledge_gaps.get('best_match_score', 0) >= 0.75])
            coverage = (good_matches / len(knowledge_gaps)) * 100
        st.metric("✅ Coverage", f"{coverage:.1f}%")

    with col4:
        faq_count = len(faq_candidates) if faq_candidates else 0
        st.metric("💡 FAQ Candidates", faq_count)

    # Status indicators
    st.markdown("---")
    st.subheader("🔄 System Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        transcript_count = count_files_in_dir("data/transcripts", [".json", ".jsonl", ".csv"])
        if transcript_count > 0:
            st.markdown(f'<div class="success-box">✓ <strong>{transcript_count} transcripts</strong> ready</div>',
                       unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">⚠️ No transcripts uploaded</div>',
                       unsafe_allow_html=True)

    with col2:
        email_count = count_files_in_dir("data/emails", [".eml", ".msg"])
        if email_count > 0:
            st.markdown(f'<div class="success-box">✓ <strong>{email_count} emails</strong> ready</div>',
                       unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">⚠️ No emails uploaded</div>',
                       unsafe_allow_html=True)

    with col3:
        if kb_articles:
            st.markdown(f'<div class="success-box">✓ <strong>{len(kb_articles)} articles</strong> from Intercom</div>',
                       unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">⚠️ KB not fetched from Intercom</div>',
                       unsafe_allow_html=True)

    # Top themes
    if knowledge_gaps is not None:
        st.markdown("---")
        st.subheader("🏷️ Top Question Themes")

        theme_counts = knowledge_gaps['theme'].value_counts().head(5)

        for theme, count in theme_counts.items():
            percentage = (count / len(knowledge_gaps)) * 100
            st.progress(percentage / 100, text=f"**{theme.title()}**: {count} questions ({percentage:.1f}%)")

    # Quick actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📥 Fetch KB from Intercom", use_container_width=True):
            st.info("Navigate to 'Data Ingestion' to fetch KB articles")

    with col2:
        if st.button("🔄 Process New Data", use_container_width=True):
            st.info("Navigate to 'Data Ingestion' to process transcripts/emails")

    with col3:
        if st.button("✏️ Review FAQs", use_container_width=True):
            st.info("Navigate to 'FAQ Review' to review and approve FAQs")

    # Recent activity (placeholder)
    st.markdown("---")
    st.subheader("📝 Recent Activity")

    activity_data = []
    if faq_candidates:
        activity_data.append({
            "Time": "Just now",
            "Activity": f"📝 {len(faq_candidates)} FAQ candidates generated",
            "Status": "✓ Complete"
        })
    if knowledge_gaps is not None:
        activity_data.append({
            "Time": "Recently",
            "Activity": f"🔍 {len(knowledge_gaps)} knowledge gaps identified",
            "Status": "✓ Complete"
        })
    if kb_articles:
        activity_data.append({
            "Time": "Recently",
            "Activity": f"📚 {len(kb_articles)} KB articles fetched",
            "Status": "✓ Complete"
        })

    if activity_data:
        st.table(pd.DataFrame(activity_data))
    else:
        st.info("No recent activity. Start by fetching KB articles or uploading data!")

elif page == "📥 Data Ingestion":
    st.title("📥 Data Ingestion")
    st.markdown("Upload and process customer interaction data")

    # Step 1: Fetch KB
    st.subheader("1️⃣ Fetch Knowledge Base from Intercom")

    col1, col2 = st.columns([3, 1])
    with col1:
        kb_articles = load_kb_articles()
        if kb_articles:
            st.success(f"✓ {len(kb_articles)} articles fetched from Intercom")
            st.caption("Last fetched: Check file timestamp")
        else:
            st.warning("KB articles not yet fetched")

    with col2:
        if st.button("🔄 Fetch KB", use_container_width=True):
            with st.spinner("Fetching articles from Intercom..."):
                import subprocess
                result = subprocess.run(
                    ["./venv/bin/python", "cli.py", "fetch-kb"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    st.success("✓ KB articles fetched successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {result.stderr}")

    st.markdown("---")

    # Step 2: Transcripts
    st.subheader("2️⃣ Upload Call Transcripts")
    transcript_count = count_files_in_dir("data/transcripts", [".json", ".jsonl", ".csv"])
    st.info(f"📁 Current: {transcript_count} transcript files in data/transcripts/")

    uploaded_transcripts = st.file_uploader(
        "Upload transcript files (.json, .jsonl, .csv)",
        accept_multiple_files=True,
        type=["json", "jsonl", "csv"],
        key="transcripts"
    )

    if uploaded_transcripts:
        if st.button("💾 Save Transcripts"):
            Path("data/transcripts").mkdir(parents=True, exist_ok=True)
            for file in uploaded_transcripts:
                with open(f"data/transcripts/{file.name}", "wb") as f:
                    f.write(file.read())
            st.success(f"✓ Saved {len(uploaded_transcripts)} transcript files!")
            st.rerun()

    st.markdown("---")

    # Step 3: Emails
    st.subheader("3️⃣ Upload Customer Emails")
    email_count = count_files_in_dir("data/emails", [".eml", ".msg"])
    st.info(f"📧 Current: {email_count} email files in data/emails/")

    uploaded_emails = st.file_uploader(
        "Upload email files (.eml, .msg)",
        accept_multiple_files=True,
        type=["eml", "msg"],
        key="emails"
    )

    if uploaded_emails:
        if st.button("💾 Save Emails"):
            Path("data/emails").mkdir(parents=True, exist_ok=True)
            for file in uploaded_emails:
                with open(f"data/emails/{file.name}", "wb") as f:
                    f.write(file.read())
            st.success(f"✓ Saved {len(uploaded_emails)} email files!")
            st.rerun()

    st.markdown("---")

    # Step 4: Process
    st.subheader("4️⃣ Process All Data")

    anonymize_pii = st.checkbox("🛡️ Anonymize PII (recommended)", value=True)
    generate_faqs = st.checkbox("💡 Generate FAQ candidates", value=True)

    if st.button("▶️ Process All Data", type="primary", use_container_width=True):
        kb_articles = load_kb_articles()

        if not kb_articles:
            st.error("❌ Please fetch KB articles first!")
        elif transcript_count == 0 and email_count == 0:
            st.error("❌ Please upload transcripts or emails first!")
        else:
            with st.spinner("Processing data... This may take several minutes."):
                import subprocess

                cmd = ["./venv/bin/python", "cli.py", "process",
                       "--kb-articles", "./data/kb_articles.json",
                       "--output", "./reports"]

                if transcript_count > 0:
                    cmd.extend(["--transcripts", "./data/transcripts"])
                if email_count > 0:
                    cmd.extend(["--emails", "./data/emails"])
                if not generate_faqs:
                    cmd.append("--no-generate-faqs")

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    st.success("✓ Processing complete!")
                    st.code(result.stdout)
                    st.balloons()
                else:
                    st.error(f"Error: {result.stderr}")

elif page == "🔍 Knowledge Gaps":
    st.title("🔍 Knowledge Gaps Analysis")
    st.markdown("Review questions that aren't well-covered by your current KB")

    knowledge_gaps = load_knowledge_gaps()

    if knowledge_gaps is None:
        st.warning("No knowledge gaps data available. Please process data first.")
        if st.button("Go to Data Ingestion"):
            st.info("Navigate to 'Data Ingestion' page")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            themes = ["All"] + sorted(knowledge_gaps['theme'].unique().tolist())
            selected_theme = st.selectbox("Theme", themes)

        with col2:
            priority_options = ["All", "High (>0.7)", "Medium (0.5-0.7)", "Low (<0.5)"]
            selected_priority = st.selectbox("Priority", priority_options)

        with col3:
            sort_options = ["Priority (High to Low)", "Priority (Low to High)", "Theme"]
            selected_sort = st.selectbox("Sort by", sort_options)

        # Apply filters
        filtered_gaps = knowledge_gaps.copy()

        if selected_theme != "All":
            filtered_gaps = filtered_gaps[filtered_gaps['theme'] == selected_theme]

        if selected_priority != "All":
            if selected_priority == "High (>0.7)":
                filtered_gaps = filtered_gaps[filtered_gaps['priority_score'] > 0.7]
            elif selected_priority == "Medium (0.5-0.7)":
                filtered_gaps = filtered_gaps[
                    (filtered_gaps['priority_score'] >= 0.5) &
                    (filtered_gaps['priority_score'] <= 0.7)
                ]
            else:
                filtered_gaps = filtered_gaps[filtered_gaps['priority_score'] < 0.5]

        # Sort
        if "High to Low" in selected_sort:
            filtered_gaps = filtered_gaps.sort_values('priority_score', ascending=False)
        elif "Low to High" in selected_sort:
            filtered_gaps = filtered_gaps.sort_values('priority_score', ascending=True)
        else:
            filtered_gaps = filtered_gaps.sort_values('theme')

        # Display
        st.markdown(f"**Showing {len(filtered_gaps)} of {len(knowledge_gaps)} gaps**")

        # Pagination
        items_per_page = 10
        total_pages = (len(filtered_gaps) - 1) // items_per_page + 1

        if 'gap_page' not in st.session_state:
            st.session_state.gap_page = 1

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← Previous") and st.session_state.gap_page > 1:
                st.session_state.gap_page -= 1
        with col2:
            st.markdown(f"<div style='text-align: center'>Page {st.session_state.gap_page} of {total_pages}</div>",
                       unsafe_allow_html=True)
        with col3:
            if st.button("Next →") and st.session_state.gap_page < total_pages:
                st.session_state.gap_page += 1

        # Display gaps
        start_idx = (st.session_state.gap_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_gaps = filtered_gaps.iloc[start_idx:end_idx]

        for idx, row in page_gaps.iterrows():
            priority = row['priority_score']
            if priority > 0.7:
                priority_color = "🔴"
            elif priority > 0.5:
                priority_color = "🟡"
            else:
                priority_color = "🟢"

            with st.expander(f"{priority_color} {row['question']} (Priority: {priority:.2f})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Theme:** {row['theme']}")
                    st.markdown(f"**Source:** {row['source_type']}")
                    st.markdown(f"**Urgency:** {row['urgency_score']:.2f}")

                with col2:
                    st.markdown(f"**Best Match:** {row.get('best_match_article', 'None')}")
                    st.markdown(f"**Similarity:** {row.get('best_match_score', 0):.2f}")

                if st.button(f"💡 Generate FAQ for this gap", key=f"gen_{idx}"):
                    st.info("This would generate a FAQ candidate (to be implemented)")

elif page == "✏️ FAQ Review":
    st.title("✏️ FAQ Review & Approval")
    st.markdown("Review AI-generated FAQ candidates before publishing")

    faq_candidates = load_faq_candidates()

    if not faq_candidates:
        st.warning("No FAQ candidates available. Please process data and generate FAQs first.")
    else:
        # Summary
        col1, col2, col3, col4 = st.columns(4)

        approved = sum(1 for faq in faq_candidates
                      if st.session_state.faq_statuses.get(faq['question_text']) == 'approved')
        needs_edit = sum(1 for faq in faq_candidates
                        if st.session_state.faq_statuses.get(faq['question_text']) == 'edit')
        rejected = sum(1 for faq in faq_candidates
                      if st.session_state.faq_statuses.get(faq['question_text']) == 'rejected')
        pending = len(faq_candidates) - approved - needs_edit - rejected

        col1.metric("✅ Approved", approved)
        col2.metric("✏️ Needs Edit", needs_edit)
        col3.metric("❌ Rejected", rejected)
        col4.metric("⏸️ Pending", pending)

        st.markdown("---")

        # Filter
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Pending Review", "Approved", "Needs Edit", "Rejected"]
        )

        # Navigation
        if 'faq_index' not in st.session_state:
            st.session_state.faq_index = 0

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← Previous FAQ") and st.session_state.faq_index > 0:
                st.session_state.faq_index -= 1
        with col2:
            st.markdown(f"<div style='text-align: center'>FAQ {st.session_state.faq_index + 1} of {len(faq_candidates)}</div>",
                       unsafe_allow_html=True)
        with col3:
            if st.button("Next FAQ →") and st.session_state.faq_index < len(faq_candidates) - 1:
                st.session_state.faq_index += 1

        # Display current FAQ
        faq = faq_candidates[st.session_state.faq_index]

        current_status = st.session_state.faq_statuses.get(faq['question_text'], 'pending')

        st.markdown(f"### FAQ #{st.session_state.faq_index + 1}")
        st.markdown(f"**Priority:** {faq['priority_score']:.2f} | **Category:** {faq['category']} | **Confidence:** {faq['confidence_score']:.2f}")

        st.markdown("#### Question:")
        question = st.text_input("Main question", value=faq['question_text'], key=f"q_{st.session_state.faq_index}")

        st.markdown("#### Answer:")
        answer = st.text_area("Answer content", value=faq['answer_text'], height=200, key=f"a_{st.session_state.faq_index}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Question Variants:")
            for i, variant in enumerate(faq['question_variants']):
                st.markdown(f"• {variant}")

        with col2:
            st.markdown("#### Tags:")
            st.markdown(", ".join(faq['tags']))

        if faq.get('notes'):
            st.warning(f"**AI Note:** {faq['notes']}")

        st.markdown("---")
        st.markdown("#### Review Decision:")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("✅ Approve", use_container_width=True, type="primary"):
                st.session_state.faq_statuses[faq['question_text']] = 'approved'
                st.success("FAQ approved!")
                st.rerun()

        with col2:
            if st.button("✏️ Needs Edit", use_container_width=True):
                st.session_state.faq_statuses[faq['question_text']] = 'edit'
                st.info("Marked for editing")
                st.rerun()

        with col3:
            if st.button("❌ Reject", use_container_width=True):
                st.session_state.faq_statuses[faq['question_text']] = 'rejected'
                st.warning("FAQ rejected")
                st.rerun()

        with col4:
            if st.button("⏸️ Skip", use_container_width=True):
                st.session_state.faq_statuses[faq['question_text']] = 'pending'
                st.info("Marked as pending")

elif page == "🚀 Publish to Intercom":
    st.title("🚀 Publish to Intercom")
    st.markdown("Publish approved FAQ candidates to your Intercom knowledge base")

    faq_candidates = load_faq_candidates()

    if not faq_candidates:
        st.warning("No FAQ candidates available.")
    else:
        # Summary
        approved = [faq for faq in faq_candidates
                   if st.session_state.faq_statuses.get(faq['question_text']) == 'approved']

        st.subheader("📋 Publishing Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Approved FAQs", len(approved))
        col2.metric("📝 Total FAQs", len(faq_candidates))
        col3.metric("📊 Approval Rate", f"{(len(approved)/len(faq_candidates)*100):.0f}%")

        if len(approved) == 0:
            st.warning("No FAQs approved yet. Go to 'FAQ Review' to approve some FAQs first.")
        else:
            st.markdown("---")
            st.subheader("⚙️ Publishing Options")

            publish_as_draft = st.radio(
                "Publication mode:",
                ["Create as drafts (recommended)", "Publish immediately"],
                help="Drafts allow final review in Intercom before publishing"
            )

            limit_faqs = st.number_input(
                "Limit number of FAQs to publish (0 = all)",
                min_value=0,
                max_value=len(approved),
                value=0
            )

            st.markdown("---")
            st.subheader("📝 FAQs to be Published")

            faqs_to_publish = approved if limit_faqs == 0 else approved[:limit_faqs]

            for i, faq in enumerate(faqs_to_publish, 1):
                st.markdown(f"{i}. {faq['question_text']}")

            st.markdown("---")

            if st.button("🚀 Publish to Intercom", type="primary", use_container_width=True):
                confirm = st.checkbox(f"I confirm publishing {len(faqs_to_publish)} FAQs to Intercom")

                if confirm:
                    with st.spinner("Publishing to Intercom..."):
                        import subprocess

                        # Save approved FAQs to temp file
                        temp_faq_file = Path("reports/approved_faqs.json")
                        with open(temp_faq_file, 'w') as f:
                            json.dump(faqs_to_publish, f, indent=2)

                        cmd = ["./venv/bin/python", "cli.py", "publish-to-intercom",
                               "--faqs", str(temp_faq_file)]

                        if limit_faqs > 0:
                            cmd.extend(["--limit", str(limit_faqs)])

                        if publish_as_draft == "Publish immediately":
                            cmd.append("--publish")

                        result = subprocess.run(cmd, capture_output=True, text=True, input="y\n")

                        if result.returncode == 0:
                            st.success(f"✓ Successfully published {len(faqs_to_publish)} FAQs!")
                            st.balloons()
                            st.code(result.stdout)
                        else:
                            st.error(f"Error: {result.stderr}")
                else:
                    st.warning("Please confirm before publishing")

elif page == "📈 Analytics":
    st.title("📈 Analytics & Insights")
    st.markdown("Track your knowledge base performance over time")

    knowledge_gaps = load_knowledge_gaps()
    faq_candidates = load_faq_candidates()
    kb_articles = load_kb_articles()

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        questions = len(knowledge_gaps) if knowledge_gaps is not None else 0
        st.metric("📝 Questions Processed", questions)

    with col2:
        coverage = 0.0
        if knowledge_gaps is not None and len(knowledge_gaps) > 0:
            good_matches = len(knowledge_gaps[knowledge_gaps.get('best_match_score', 0) >= 0.75])
            coverage = (good_matches / len(knowledge_gaps)) * 100
        st.metric("📊 KB Coverage", f"{coverage:.1f}%")

    with col3:
        articles_count = len(kb_articles) if kb_articles else 0
        st.metric("📚 KB Articles", articles_count)

    with col4:
        faq_count = len(faq_candidates) if faq_candidates else 0
        st.metric("💡 FAQs Generated", faq_count)

    st.markdown("---")

    # Theme distribution
    if knowledge_gaps is not None:
        st.subheader("🏷️ Questions by Theme")

        theme_counts = knowledge_gaps['theme'].value_counts()

        chart_data = pd.DataFrame({
            'Theme': theme_counts.index,
            'Count': theme_counts.values
        })

        st.bar_chart(chart_data.set_index('Theme'))

    st.markdown("---")

    # Priority distribution
    if knowledge_gaps is not None:
        st.subheader("⭐ Priority Distribution")

        high_priority = len(knowledge_gaps[knowledge_gaps['priority_score'] > 0.7])
        medium_priority = len(knowledge_gaps[
            (knowledge_gaps['priority_score'] >= 0.5) &
            (knowledge_gaps['priority_score'] <= 0.7)
        ])
        low_priority = len(knowledge_gaps[knowledge_gaps['priority_score'] < 0.5])

        col1, col2, col3 = st.columns(3)
        col1.metric("🔴 High Priority", high_priority)
        col2.metric("🟡 Medium Priority", medium_priority)
        col3.metric("🟢 Low Priority", low_priority)

    st.markdown("---")

    # Export options
    st.subheader("📥 Export Reports")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Download Summary Report", use_container_width=True):
            st.info("See reports/report.md")

    with col2:
        if st.button("📋 Download Knowledge Gaps CSV", use_container_width=True):
            st.info("See reports/knowledge_gaps.csv")

    with col3:
        if st.button("💡 Download FAQ Candidates JSON", use_container_width=True):
            st.info("See reports/faq_candidates.json")
