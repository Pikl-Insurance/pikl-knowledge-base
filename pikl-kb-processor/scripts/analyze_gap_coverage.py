#!/usr/bin/env python3
"""
Knowledge Gap Coverage Analysis
Analyzes how well the uploaded FAQs address the original knowledge gaps.
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
import re


def load_knowledge_gaps() -> pd.DataFrame:
    """Load original knowledge gaps."""
    gaps_path = Path("../reports/knowledge_gaps.csv")
    if gaps_path.exists():
        return pd.read_csv(gaps_path)
    return pd.DataFrame()


def load_uploaded_faqs() -> List[Dict]:
    """Load FAQs that were uploaded to Intercom."""
    faqs_path = Path("../../faq-system/data/internal_faqs.json")
    if faqs_path.exists():
        with open(faqs_path) as f:
            data = json.load(f)
            return data.get('faqs', [])
    return []


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Simple text similarity based on common words."""
    # Normalize texts
    text1 = text1.lower()
    text2 = text2.lower()

    # Remove punctuation and split into words
    words1 = set(re.findall(r'\w+', text1))
    words2 = set(re.findall(r'\w+', text2))

    # Remove common stopwords
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                 'what', 'does', 'do', 'how', 'when', 'where', 'why', 'which'}
    words1 = words1 - stopwords
    words2 = words2 - stopwords

    if not words1 or not words2:
        return 0.0

    # Calculate Jaccard similarity
    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union)


def find_best_faq_match(gap_question: str, faqs: List[Dict]) -> Tuple[Dict, float]:
    """Find the best matching FAQ for a knowledge gap question."""
    best_match = None
    best_score = 0.0

    for faq in faqs:
        # Check question match
        question = faq.get('question', '')
        score = calculate_text_similarity(gap_question, question)

        # Also check against answer for context
        answer = faq.get('answer', '')
        answer_score = calculate_text_similarity(gap_question, answer) * 0.5

        total_score = max(score, answer_score)

        if total_score > best_score:
            best_score = total_score
            best_match = faq

    return best_match, best_score


def analyze_gap_coverage(gaps: pd.DataFrame, faqs: List[Dict]) -> Dict:
    """Analyze how well FAQs cover the knowledge gaps."""

    print("Analyzing gap coverage...")
    print(f"  Knowledge gaps: {len(gaps)}")
    print(f"  Uploaded FAQs: {len(faqs)}")
    print()

    # Track coverage by theme
    coverage_by_theme = defaultdict(lambda: {'total': 0, 'covered': 0, 'scores': []})

    # Track individual gaps
    gap_analysis = []

    for idx, row in gaps.iterrows():
        gap_question = row['question']
        theme = row.get('theme', 'Unknown')
        priority = row.get('priority_score', 0.0)

        # Find best matching FAQ
        best_faq, match_score = find_best_faq_match(gap_question, faqs)

        # Consider it covered if match score >= 0.3
        is_covered = match_score >= 0.3

        coverage_by_theme[theme]['total'] += 1
        coverage_by_theme[theme]['scores'].append(match_score)
        if is_covered:
            coverage_by_theme[theme]['covered'] += 1

        gap_analysis.append({
            'question': gap_question,
            'theme': theme,
            'priority': priority,
            'is_covered': is_covered,
            'match_score': match_score,
            'matched_faq': best_faq.get('question', '') if best_faq else '',
            'faq_category': best_faq.get('category', '') if best_faq else ''
        })

    # Calculate overall stats
    total_gaps = len(gaps)
    covered_gaps = sum(1 for g in gap_analysis if g['is_covered'])
    coverage_percentage = (covered_gaps / total_gaps * 100) if total_gaps > 0 else 0

    # Calculate average match score
    avg_match_score = sum(g['match_score'] for g in gap_analysis) / total_gaps if total_gaps > 0 else 0

    # Identify remaining high-priority gaps
    remaining_high_priority = [
        g for g in gap_analysis
        if not g['is_covered'] and g['priority'] > 0.7
    ]

    return {
        'overall': {
            'total_gaps': total_gaps,
            'covered_gaps': covered_gaps,
            'remaining_gaps': total_gaps - covered_gaps,
            'coverage_percentage': coverage_percentage,
            'avg_match_score': avg_match_score
        },
        'by_theme': dict(coverage_by_theme),
        'gap_details': gap_analysis,
        'high_priority_remaining': remaining_high_priority
    }


def save_analysis_report(analysis: Dict, output_dir: Path):
    """Save detailed analysis report."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON report
    json_file = output_dir / "gap_coverage_analysis.json"
    with open(json_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"✓ Saved JSON report: {json_file}")

    # Save CSV of gap details
    csv_file = output_dir / "gap_coverage_details.csv"
    df = pd.DataFrame(analysis['gap_details'])
    df.to_csv(csv_file, index=False)

    print(f"✓ Saved CSV report: {csv_file}")

    # Generate markdown summary
    md_file = output_dir / "GAP_COVERAGE_SUMMARY.md"

    overall = analysis['overall']

    md_content = f"""# Knowledge Gap Coverage Analysis

## Executive Summary

After uploading **1,441 FAQs** to Intercom, we analyzed coverage of the original **{overall['total_gaps']} knowledge gaps** identified from customer interactions.

### Overall Coverage

- **Gaps Addressed:** {overall['covered_gaps']} ({overall['coverage_percentage']:.1f}%)
- **Remaining Gaps:** {overall['remaining_gaps']} ({100 - overall['coverage_percentage']:.1f}%)
- **Average Match Quality:** {overall['avg_match_score']:.2f}

## Coverage by Theme

"""

    # Sort themes by coverage percentage
    theme_stats = []
    for theme, stats in analysis['by_theme'].items():
        pct = (stats['covered'] / stats['total'] * 100) if stats['total'] > 0 else 0
        avg_score = sum(stats['scores']) / len(stats['scores']) if stats['scores'] else 0
        theme_stats.append((theme, stats['total'], stats['covered'], pct, avg_score))

    theme_stats.sort(key=lambda x: x[3], reverse=True)

    md_content += "| Theme | Total Gaps | Covered | Coverage % | Avg Match |\n"
    md_content += "|-------|-----------|---------|------------|------------|\n"

    for theme, total, covered, pct, avg_score in theme_stats:
        md_content += f"| {theme} | {total} | {covered} | {pct:.1f}% | {avg_score:.2f} |\n"

    # High priority remaining gaps
    md_content += f"\n## High Priority Gaps Remaining\n\n"
    md_content += f"**{len(analysis['high_priority_remaining'])} high-priority gaps** still need attention:\n\n"

    if analysis['high_priority_remaining']:
        for idx, gap in enumerate(analysis['high_priority_remaining'][:10], 1):
            md_content += f"{idx}. **{gap['question']}**\n"
            md_content += f"   - Theme: {gap['theme']}\n"
            md_content += f"   - Priority: {gap['priority']:.2f}\n\n"

        if len(analysis['high_priority_remaining']) > 10:
            md_content += f"\n...and {len(analysis['high_priority_remaining']) - 10} more high-priority gaps.\n"
    else:
        md_content += "🎉 All high-priority gaps have been addressed!\n"

    md_content += "\n## Recommendations\n\n"

    if overall['coverage_percentage'] >= 80:
        md_content += "✅ **Excellent Coverage!** You've addressed the vast majority of knowledge gaps.\n\n"
    elif overall['coverage_percentage'] >= 60:
        md_content += "👍 **Good Coverage!** Most gaps are addressed, but there's room for improvement.\n\n"
    else:
        md_content += "⚠️ **Needs Improvement.** Consider creating FAQs for remaining high-priority gaps.\n\n"

    md_content += f"1. Focus on the {len(analysis['high_priority_remaining'])} high-priority gaps first\n"
    md_content += "2. Review gaps by theme to identify patterns\n"
    md_content += "3. Monitor new customer questions to identify emerging gaps\n"

    with open(md_file, 'w') as f:
        f.write(md_content)

    print(f"✓ Saved summary: {md_file}")


def main():
    """Main analysis process."""
    print("=" * 70)
    print("Knowledge Gap Coverage Analysis")
    print("=" * 70)
    print()

    # Load data
    gaps = load_knowledge_gaps()
    faqs = load_uploaded_faqs()

    if gaps.empty:
        print("❌ No knowledge gaps data found")
        return

    if not faqs:
        print("❌ No uploaded FAQs found")
        return

    # Analyze coverage
    analysis = analyze_gap_coverage(gaps, faqs)

    # Print summary
    print()
    print("=" * 70)
    print("Analysis Complete")
    print("=" * 70)
    print()
    print(f"Total Knowledge Gaps: {analysis['overall']['total_gaps']}")
    print(f"Gaps Covered: {analysis['overall']['covered_gaps']} ({analysis['overall']['coverage_percentage']:.1f}%)")
    print(f"Gaps Remaining: {analysis['overall']['remaining_gaps']}")
    print(f"High-Priority Remaining: {len(analysis['high_priority_remaining'])}")
    print()

    # Save reports
    output_dir = Path("../reports")
    save_analysis_report(analysis, output_dir)

    print()
    print("✓ Analysis complete! Check reports/ directory for details.")


if __name__ == "__main__":
    main()
