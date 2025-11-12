"""Knowledge gap analysis and prioritization."""

from collections import Counter, defaultdict
from typing import List

from rich.console import Console

from models import AnswerCandidate, KBMatch, KnowledgeGap, Question

console = Console()


class GapAnalyzer:
    """Analyze knowledge gaps and prioritize FAQ creation."""

    def __init__(self, similarity_threshold: float = 0.75):
        """Initialize gap analyzer.

        Args:
            similarity_threshold: Threshold for considering a match as "good"
        """
        self.similarity_threshold = similarity_threshold

    def identify_gaps(
        self,
        matches: List[KBMatch],
        answer_candidates: List[AnswerCandidate],
    ) -> List[KnowledgeGap]:
        """Identify knowledge gaps from KB matches.

        Args:
            matches: List of KB matches
            answer_candidates: List of answer candidates from transcripts/emails

        Returns:
            List of KnowledgeGap objects
        """
        gaps = []

        # Group poor matches (potential gaps)
        poor_matches = [m for m in matches if not m.is_good_match]

        console.print(f"Analyzing {len(poor_matches)} potential knowledge gaps...")

        # Create answer lookup by source
        answer_by_source = defaultdict(list)
        for answer in answer_candidates:
            answer_by_source[answer.source_id].append(answer)

        for match in poor_matches:
            question = match.question

            # Find relevant answer candidates from the same source
            relevant_answers = answer_by_source.get(question.source_id, [])

            # Calculate priority score based on:
            # - Urgency of the question
            # - How far the best match is from threshold
            # - Number of times this question appears
            gap_severity = self.similarity_threshold - match.similarity_score
            priority = (
                question.urgency_score * 0.4
                + gap_severity * 0.4
                + min(question.frequency / 10.0, 0.2)
            )

            gap = KnowledgeGap(
                question=question,
                best_match=match if match.similarity_score > 0.5 else None,
                answer_candidates=relevant_answers,
                priority_score=min(priority, 1.0),
                theme=None,  # Will be set by theme clustering
            )
            gaps.append(gap)

        # Cluster similar questions and identify themes
        gaps_with_themes = self._cluster_and_theme(gaps)

        # Sort by priority
        gaps_with_themes.sort(key=lambda g: g.priority_score, reverse=True)

        console.print(f"[green]Identified {len(gaps_with_themes)} knowledge gaps[/green]")

        return gaps_with_themes

    def _cluster_and_theme(self, gaps: List[KnowledgeGap]) -> List[KnowledgeGap]:
        """Cluster similar gaps and assign themes.

        Args:
            gaps: List of knowledge gaps

        Returns:
            Same gaps with themes assigned
        """
        # Simple keyword-based clustering for now
        # In a more sophisticated version, we could use embeddings

        # Extract keywords from questions
        theme_keywords = defaultdict(list)

        for gap in gaps:
            question_text = gap.question.text.lower()
            # Extract potential themes from question text
            themes = self._extract_themes(question_text)
            for theme in themes:
                theme_keywords[theme].append(gap)

        # Assign primary theme to each gap based on most common theme
        for gap in gaps:
            question_text = gap.question.text.lower()
            themes = self._extract_themes(question_text)
            if themes:
                # Assign the theme with most questions as primary
                theme_counts = [(t, len(theme_keywords[t])) for t in themes]
                theme_counts.sort(key=lambda x: x[1], reverse=True)
                gap.theme = theme_counts[0][0]

        return gaps

    def _extract_themes(self, text: str) -> List[str]:
        """Extract potential themes from question text.

        Args:
            text: Question text

        Returns:
            List of theme keywords
        """
        # Common insurance/customer service themes
        theme_patterns = {
            "claim": ["claim", "claims", "filing", "submit"],
            "policy": ["policy", "policies", "coverage", "plan"],
            "payment": ["payment", "pay", "billing", "invoice", "premium"],
            "account": ["account", "login", "password", "access"],
            "cancellation": ["cancel", "cancellation", "terminate", "end"],
            "renewal": ["renew", "renewal", "extension", "expiry", "expire"],
            "quote": ["quote", "quotation", "estimate", "price"],
            "document": ["document", "documents", "paperwork", "forms", "certificate"],
            "contact": ["contact", "reach", "phone", "email", "support"],
            "change": ["change", "update", "modify", "edit"],
        }

        themes = []
        for theme, keywords in theme_patterns.items():
            if any(keyword in text for keyword in keywords):
                themes.append(theme)

        return themes if themes else ["general"]

    def get_summary_stats(self, gaps: List[KnowledgeGap]) -> dict:
        """Generate summary statistics for knowledge gaps.

        Args:
            gaps: List of knowledge gaps

        Returns:
            Dictionary of statistics
        """
        if not gaps:
            return {
                "total_gaps": 0,
                "high_priority": 0,
                "medium_priority": 0,
                "low_priority": 0,
                "top_themes": [],
                "avg_priority": 0.0,
            }

        # Priority buckets
        high_priority = sum(1 for g in gaps if g.priority_score >= 0.7)
        medium_priority = sum(
            1 for g in gaps if 0.4 <= g.priority_score < 0.7
        )
        low_priority = sum(1 for g in gaps if g.priority_score < 0.4)

        # Top themes
        themes = [g.theme for g in gaps if g.theme]
        theme_counts = Counter(themes)
        top_themes = [
            {"theme": theme, "count": count}
            for theme, count in theme_counts.most_common(10)
        ]

        # Average priority
        avg_priority = sum(g.priority_score for g in gaps) / len(gaps)

        return {
            "total_gaps": len(gaps),
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "top_themes": top_themes,
            "avg_priority": round(avg_priority, 2),
        }

    def get_high_priority_gaps(
        self, gaps: List[KnowledgeGap], threshold: float = 0.7
    ) -> List[KnowledgeGap]:
        """Get high priority gaps above threshold.

        Args:
            gaps: List of knowledge gaps
            threshold: Priority threshold

        Returns:
            List of high priority gaps
        """
        high_priority = [g for g in gaps if g.priority_score >= threshold]
        return sorted(high_priority, key=lambda g: g.priority_score, reverse=True)

    def get_gaps_by_theme(self, gaps: List[KnowledgeGap]) -> dict:
        """Group gaps by theme.

        Args:
            gaps: List of knowledge gaps

        Returns:
            Dictionary mapping theme to list of gaps
        """
        by_theme = defaultdict(list)
        for gap in gaps:
            theme = gap.theme or "general"
            by_theme[theme].append(gap)

        # Sort gaps within each theme by priority
        for theme in by_theme:
            by_theme[theme].sort(key=lambda g: g.priority_score, reverse=True)

        return dict(by_theme)
