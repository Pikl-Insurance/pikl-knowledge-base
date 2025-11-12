"""KB matching using semantic similarity."""

from typing import List, Tuple

import numpy as np
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from sentence_transformers import SentenceTransformer

from models import Article, KBMatch, Question

console = Console()


class KBMatcher:
    """Match questions to existing KB articles using semantic similarity."""

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        similarity_threshold: float = 0.75,
    ):
        """Initialize KB matcher.

        Args:
            embedding_model: Sentence transformer model name
            similarity_threshold: Minimum similarity score to consider a good match
        """
        console.print(f"Loading embedding model: {embedding_model}...")
        self.model = SentenceTransformer(embedding_model)
        self.similarity_threshold = similarity_threshold
        self.article_embeddings = None
        self.articles = []

    def index_articles(self, articles: List[Article]) -> None:
        """Create embeddings for all KB articles.

        Args:
            articles: List of articles to index
        """
        self.articles = articles

        if not articles:
            console.print("[yellow]Warning: No articles to index[/yellow]")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Indexing {len(articles)} KB articles...", total=None
            )

            # Create text representations of articles
            article_texts = []
            for article in articles:
                # Combine title, description, and body for better matching
                text_parts = [article.title]
                if article.description:
                    text_parts.append(article.description)
                # Include first 500 chars of body to avoid token limits
                text_parts.append(article.body[:500])

                article_text = " | ".join(text_parts)
                article_texts.append(article_text)

            # Generate embeddings
            self.article_embeddings = self.model.encode(
                article_texts,
                show_progress_bar=False,
                convert_to_numpy=True,
            )

            progress.update(
                task,
                description=f"✓ Indexed {len(articles)} KB articles",
                completed=True,
            )

        console.print(f"[green]KB index ready with {len(articles)} articles[/green]")

    def match_questions(self, questions: List[Question]) -> List[KBMatch]:
        """Match questions to KB articles.

        Args:
            questions: List of questions to match

        Returns:
            List of KBMatch objects
        """
        if not self.articles or self.article_embeddings is None:
            console.print("[red]Error: KB not indexed. Call index_articles() first.[/red]")
            return []

        matches = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Matching {len(questions)} questions to KB...", total=len(questions)
            )

            # Encode questions in batches for efficiency
            batch_size = 32
            for i in range(0, len(questions), batch_size):
                batch = questions[i : i + batch_size]
                question_texts = [q.text for q in batch]

                # Generate embeddings for questions
                question_embeddings = self.model.encode(
                    question_texts,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                )

                # Find best matches for each question
                for j, question in enumerate(batch):
                    question_embedding = question_embeddings[j]
                    best_article_idx, similarity = self._find_best_match(
                        question_embedding
                    )

                    if best_article_idx is not None:
                        is_good_match = similarity >= self.similarity_threshold
                        match = KBMatch(
                            question=question,
                            article=self.articles[best_article_idx],
                            similarity_score=float(similarity),
                            is_good_match=is_good_match,
                            notes=None,
                        )
                        matches.append(match)

                    progress.advance(task, advance=1)

        good_matches = sum(1 for m in matches if m.is_good_match)
        console.print(
            f"[green]Matched {len(matches)} questions: {good_matches} good matches, "
            f"{len(matches) - good_matches} potential gaps[/green]"
        )

        return matches

    def _find_best_match(
        self, question_embedding: np.ndarray
    ) -> Tuple[int | None, float]:
        """Find best matching article for a question embedding.

        Args:
            question_embedding: Question embedding vector

        Returns:
            Tuple of (article_index, similarity_score) or (None, 0.0)
        """
        if self.article_embeddings is None or len(self.article_embeddings) == 0:
            return None, 0.0

        # Calculate cosine similarity
        similarities = self._cosine_similarity(
            question_embedding, self.article_embeddings
        )

        # Find best match
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        return best_idx, best_score

    def _cosine_similarity(
        self, vec1: np.ndarray, vec2: np.ndarray
    ) -> np.ndarray:
        """Calculate cosine similarity between vectors.

        Args:
            vec1: First vector or matrix
            vec2: Second vector or matrix

        Returns:
            Similarity scores
        """
        # Normalize vectors
        vec1_norm = vec1 / np.linalg.norm(vec1)

        if vec2.ndim == 1:
            vec2_norm = vec2 / np.linalg.norm(vec2)
            return np.dot(vec1_norm, vec2_norm)
        else:
            vec2_norm = vec2 / np.linalg.norm(vec2, axis=1, keepdims=True)
            return np.dot(vec2_norm, vec1_norm)

    def get_top_matches(
        self, question: Question, top_k: int = 5
    ) -> List[Tuple[Article, float]]:
        """Get top K matching articles for a question.

        Args:
            question: Question to match
            top_k: Number of top matches to return

        Returns:
            List of (Article, similarity_score) tuples
        """
        if self.article_embeddings is None:
            return []

        # Encode question
        question_embedding = self.model.encode(
            question.text,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        # Calculate similarities
        similarities = self._cosine_similarity(
            question_embedding, self.article_embeddings
        )

        # Get top K indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Return articles with scores
        results = []
        for idx in top_indices:
            results.append((self.articles[idx], float(similarities[idx])))

        return results
