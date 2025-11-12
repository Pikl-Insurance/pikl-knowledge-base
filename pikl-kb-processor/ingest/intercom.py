"""Intercom API integration for fetching help center articles."""

import time
from datetime import datetime
from typing import List, Optional

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from models import Article

console = Console()


class IntercomFetcher:
    """Fetch and create articles in Intercom help center."""

    def __init__(self, access_token: str):
        """Initialize Intercom fetcher.

        Args:
            access_token: Intercom API access token
        """
        self.access_token = access_token
        self.base_url = "https://api.intercom.io"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Intercom-Version": "2.11",
        }

    def fetch_all_articles(self) -> List[Article]:
        """Fetch all articles from Intercom help center.

        Returns:
            List of Article objects

        Raises:
            requests.HTTPError: If API request fails
        """
        articles = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching articles from Intercom...", total=None)

            # Try approach 1: Fetch via collections/sections
            collections = self._fetch_collections()
            progress.update(task, description=f"Found {len(collections)} collections")

            for collection in collections:
                collection_articles = self._fetch_articles_for_collection(
                    collection["id"]
                )
                articles.extend(collection_articles)
                progress.update(
                    task, description=f"Fetched {len(articles)} articles so far..."
                )

            # If no articles found via collections, try direct article search
            if len(articles) == 0:
                progress.update(task, description="Trying direct article search...")
                articles = self._fetch_all_articles_direct()

            progress.update(
                task,
                description=f"✓ Fetched {len(articles)} articles from Intercom",
                completed=True,
            )

        console.print(f"[green]Successfully fetched {len(articles)} articles[/green]")
        return articles

    def _fetch_collections(self) -> List[dict]:
        """Fetch all help center collections (categories).

        Returns:
            List of collection dictionaries
        """
        url = f"{self.base_url}/help_center/collections"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        data = response.json()
        return data.get("data", [])

    def _fetch_articles_for_collection(self, collection_id: str) -> List[Article]:
        """Fetch all articles for a specific collection.

        Args:
            collection_id: Collection ID

        Returns:
            List of Article objects
        """
        articles = []
        url = f"{self.base_url}/help_center/collections/{collection_id}/sections"

        try:
            # Get sections in this collection
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            sections = response.json().get("data", [])

            # Fetch articles for each section
            for section in sections:
                section_articles = self._fetch_articles_for_section(
                    section["id"], section.get("name")
                )
                articles.extend(section_articles)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                console.print(
                    f"[yellow]Warning: Collection {collection_id} has no sections or not accessible. Skipping.[/yellow]"
                )
            else:
                console.print(
                    f"[yellow]Warning: Error fetching articles for collection {collection_id}: {e}[/yellow]"
                )

        return articles

    def _fetch_articles_for_section(
        self, section_id: str, category_name: Optional[str] = None
    ) -> List[Article]:
        """Fetch all articles for a specific section.

        Args:
            section_id: Section ID
            category_name: Name of the category/section

        Returns:
            List of Article objects
        """
        articles = []
        url = f"{self.base_url}/articles"
        params = {"section_id": section_id}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        data = response.json()
        for article_data in data.get("data", []):
            article = self._parse_article(article_data, category_name)
            if article:
                articles.append(article)

        # Rate limiting - be nice to Intercom API
        time.sleep(0.1)

        return articles

    def _parse_article(
        self, article_data: dict, category: Optional[str] = None
    ) -> Optional[Article]:
        """Parse Intercom article data into Article model.

        Args:
            article_data: Raw article data from Intercom API
            category: Category/section name

        Returns:
            Article object or None if parsing fails
        """
        try:
            return Article(
                id=str(article_data.get("id", "")),
                title=article_data.get("title", ""),
                body=article_data.get("body", ""),
                description=article_data.get("description"),
                url=article_data.get("url"),
                category=category,
                tags=[],  # Intercom doesn't expose tags via API easily
                created_at=self._parse_timestamp(article_data.get("created_at")),
                updated_at=self._parse_timestamp(article_data.get("updated_at")),
            )
        except Exception as e:
            console.print(
                f"[yellow]Warning: Failed to parse article {article_data.get('id')}: {e}[/yellow]"
            )
            return None

    def _parse_timestamp(self, timestamp: Optional[int]) -> Optional[datetime]:
        """Parse Unix timestamp to datetime.

        Args:
            timestamp: Unix timestamp

        Returns:
            datetime object or None
        """
        if timestamp:
            return datetime.fromtimestamp(timestamp)
        return None

    def _fetch_all_articles_direct(self) -> List[Article]:
        """Fetch articles directly using list endpoint.

        Returns:
            List of Article objects
        """
        articles = []
        url = f"{self.base_url}/articles"
        params = {"per_page": 50}

        try:
            while url:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()

                # Parse articles from response
                for article_data in data.get("data", []):
                    article = self._parse_article(article_data)
                    if article:
                        articles.append(article)

                # Check for pagination
                pages = data.get("pages", {})
                url = pages.get("next")
                params = {}  # Next URL includes params

                # Rate limiting
                time.sleep(0.1)

        except requests.exceptions.HTTPError as e:
            console.print(
                f"[yellow]Warning: Could not fetch articles directly: {e}[/yellow]"
            )

        return articles

    def create_article(
        self,
        title: str,
        body: str,
        description: Optional[str] = None,
        author_id: Optional[int] = None,
        state: str = "draft",
    ) -> Optional[dict]:
        """Create a new help article in Intercom.

        Args:
            title: Article title
            body: Article body (HTML or plain text)
            description: Short description/summary
            author_id: Intercom admin/author ID (optional)
            state: Article state - "draft" or "published" (default: draft)

        Returns:
            Created article data or None if failed
        """
        url = f"{self.base_url}/articles"

        payload = {
            "title": title,
            "body": body,
            "state": state,
        }

        if description:
            payload["description"] = description
        if author_id:
            payload["author_id"] = author_id

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            article_data = response.json()
            console.print(f"[green]✓ Created article: {title}[/green]")
            return article_data
        except requests.exceptions.HTTPError as e:
            console.print(f"[red]✗ Failed to create article '{title}': {e}[/red]")
            if e.response:
                console.print(f"[dim]{e.response.text}[/dim]")
            return None
        except Exception as e:
            console.print(f"[red]✗ Error creating article: {e}[/red]")
            return None

    def create_article_from_faq(
        self, faq_data: dict, author_id: Optional[int] = None, publish: bool = False
    ) -> Optional[dict]:
        """Create an article from FAQ candidate data.

        Args:
            faq_data: FAQ candidate dictionary with question_text, answer_text, etc.
            author_id: Intercom admin/author ID (optional)
            publish: Whether to publish immediately (default: False, creates as draft)

        Returns:
            Created article data or None if failed
        """
        # Format the body with question variants
        body = faq_data["answer_text"]

        if faq_data.get("question_variants"):
            variants_section = "\n\n**Related questions:**\n"
            for variant in faq_data["question_variants"]:
                variants_section += f"- {variant}\n"
            body += variants_section

        # Add tags/category info if available
        if faq_data.get("category"):
            body += f"\n\n*Category: {faq_data['category']}*"

        state = "published" if publish else "draft"

        return self.create_article(
            title=faq_data["question_text"],
            body=body,
            description=faq_data.get("question_variants", [None])[0]
            if faq_data.get("question_variants")
            else None,
            author_id=author_id,
            state=state,
        )

    def create_articles_from_faqs(
        self,
        faq_candidates: List[dict],
        author_id: Optional[int] = None,
        publish: bool = False,
        limit: Optional[int] = None,
    ) -> List[dict]:
        """Create multiple articles from FAQ candidates.

        Args:
            faq_candidates: List of FAQ candidate dictionaries
            author_id: Intercom admin/author ID (optional)
            publish: Whether to publish immediately (default: False)
            limit: Maximum number of articles to create (optional)

        Returns:
            List of created article data
        """
        created_articles = []
        faqs_to_create = faq_candidates[:limit] if limit else faq_candidates

        console.print(
            f"\n[cyan]Creating {len(faqs_to_create)} articles in Intercom...[/cyan]"
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating articles...", total=len(faqs_to_create))

            for faq in faqs_to_create:
                article_data = self.create_article_from_faq(faq, author_id, publish)
                if article_data:
                    created_articles.append(article_data)

                progress.advance(task)

                # Rate limiting
                time.sleep(0.5)

        console.print(
            f"[green]✓ Successfully created {len(created_articles)}/{len(faqs_to_create)} articles[/green]"
        )

        return created_articles

    def test_connection(self) -> bool:
        """Test Intercom API connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            url = f"{self.base_url}/help_center/collections"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            console.print("[green]✓ Intercom API connection successful[/green]")
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                console.print(
                    "[red]✗ Authentication failed. Check your Intercom access token.[/red]"
                )
            else:
                console.print(f"[red]✗ API error: {e}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]✗ Connection failed: {e}[/red]")
            return False
