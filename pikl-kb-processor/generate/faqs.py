"""FAQ generation from knowledge gaps using Claude."""

import json
from typing import List

import anthropic
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from models import FAQCandidate, KnowledgeGap

console = Console()


class FAQGenerator:
    """Generate FAQ candidates to fill knowledge gaps."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """Initialize FAQ generator.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate_faqs(self, gaps: List[KnowledgeGap]) -> List[FAQCandidate]:
        """Generate FAQ candidates for knowledge gaps.

        Args:
            gaps: List of knowledge gaps

        Returns:
            List of FAQ candidates
        """
        if not gaps:
            console.print("[yellow]No gaps to generate FAQs for[/yellow]")
            return []

        faq_candidates = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Generating FAQs for {len(gaps)} gaps...", total=len(gaps)
            )

            for gap in gaps:
                try:
                    faq = self._generate_faq_for_gap(gap)
                    if faq:
                        faq_candidates.append(faq)
                    progress.advance(task)
                except Exception as e:
                    console.print(
                        f"[yellow]Warning: Failed to generate FAQ: {e}[/yellow]"
                    )
                    progress.advance(task)

        console.print(
            f"[green]Generated {len(faq_candidates)} FAQ candidates[/green]"
        )
        return faq_candidates

    def _generate_faq_for_gap(self, gap: KnowledgeGap) -> FAQCandidate | None:
        """Generate FAQ candidate for a single knowledge gap.

        Args:
            gap: Knowledge gap

        Returns:
            FAQCandidate or None if generation fails
        """
        # Build context
        question_text = gap.question.text
        question_context = gap.question.context or ""

        # Include answer candidates if available
        answer_context = ""
        if gap.answer_candidates:
            answer_context = "\n\nAgent responses from the same interaction:\n"
            for i, answer in enumerate(gap.answer_candidates[:3], 1):
                answer_context += f"{i}. {answer.text}\n"

        # Include best match if available
        best_match_context = ""
        if gap.best_match:
            article = gap.best_match.article
            best_match_context = f"""

Closest existing KB article (similarity: {gap.best_match.similarity_score:.2f}):
Title: {article.title}
Content: {article.body[:500]}..."""

        prompt = f"""You are a knowledge base content writer for a customer service team. Your task is to create a comprehensive FAQ entry based on a customer question that isn't well-covered in the current knowledge base.

Customer Question: {question_text}

Context from conversation:
{question_context}
{answer_context}
{best_match_context}

Please create an FAQ entry with:
1. A clear, well-phrased question (the main question)
2. 2-3 alternative phrasings of the same question (question variants)
3. A comprehensive, accurate answer
4. Appropriate category/theme
5. Relevant tags for searchability

Important guidelines:
- Write in a professional, helpful tone
- Be specific and actionable
- If the agent responses provide good information, incorporate it
- If information seems uncertain, note what should be verified
- Make the answer self-contained and easy to understand

Return your response as JSON in this exact format:
{{
  "question": "Main question text",
  "question_variants": ["Alternative phrasing 1", "Alternative phrasing 2"],
  "answer": "Comprehensive answer text",
  "category": "Category name",
  "tags": ["tag1", "tag2", "tag3"],
  "confidence": 0.85,
  "notes": "Any notes about uncertainty or need for verification"
}}"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            data = json.loads(response_text)

            # Create FAQCandidate
            faq = FAQCandidate(
                question_text=data["question"],
                question_variants=data.get("question_variants", []),
                answer_text=data["answer"],
                category=data.get("category", gap.theme),
                tags=data.get("tags", []),
                confidence_score=data.get("confidence", 0.7),
                source_references=[gap.question.source_id],
                priority_score=gap.priority_score,
                notes=data.get("notes"),
            )

            return faq

        except json.JSONDecodeError as e:
            console.print(
                f"[yellow]Warning: Failed to parse FAQ generation response: {e}[/yellow]"
            )
            console.print(f"[dim]Response was: {response_text[:500]}...[/dim]")
            return None
        except Exception as e:
            console.print(f"[red]Error generating FAQ: {e}[/red]")
            return None

    def generate_batch(
        self, gaps: List[KnowledgeGap], batch_size: int = 5
    ) -> List[FAQCandidate]:
        """Generate FAQs in batches for better efficiency.

        Args:
            gaps: List of knowledge gaps
            batch_size: Number of gaps to process per batch

        Returns:
            List of FAQ candidates
        """
        # For now, we'll process individually for better quality
        # In future, could batch similar questions together
        return self.generate_faqs(gaps)

    def refine_faq(
        self, faq: FAQCandidate, feedback: str
    ) -> FAQCandidate | None:
        """Refine an FAQ based on feedback.

        Args:
            faq: Original FAQ candidate
            feedback: Feedback or instructions for refinement

        Returns:
            Refined FAQ candidate or None if refinement fails
        """
        prompt = f"""You are refining an FAQ entry based on feedback. Here is the current FAQ:

Question: {faq.question_text}
Question Variants: {', '.join(faq.question_variants)}
Answer: {faq.answer_text}
Category: {faq.category}
Tags: {', '.join(faq.tags)}

Feedback: {feedback}

Please provide an improved version of this FAQ incorporating the feedback.

Return your response as JSON in this exact format:
{{
  "question": "Main question text",
  "question_variants": ["Alternative phrasing 1", "Alternative phrasing 2"],
  "answer": "Comprehensive answer text",
  "category": "Category name",
  "tags": ["tag1", "tag2", "tag3"],
  "confidence": 0.85,
  "notes": "Any notes"
}}"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            data = json.loads(response_text)

            # Create refined FAQCandidate
            refined_faq = FAQCandidate(
                question_text=data["question"],
                question_variants=data.get("question_variants", []),
                answer_text=data["answer"],
                category=data.get("category", faq.category),
                tags=data.get("tags", []),
                confidence_score=data.get("confidence", faq.confidence_score),
                source_references=faq.source_references,
                priority_score=faq.priority_score,
                notes=data.get("notes"),
            )

            return refined_faq

        except Exception as e:
            console.print(f"[red]Error refining FAQ: {e}[/red]")
            return None
