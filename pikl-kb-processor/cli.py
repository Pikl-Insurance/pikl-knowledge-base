#!/usr/bin/env python3
"""CLI for Pikl KB Processor."""

from pathlib import Path

import click
from rich.console import Console

from analyze import GapAnalyzer, KBMatcher, QuestionExtractor
from config import config
from generate import FAQGenerator
from ingest import EmailParser, IntercomFetcher, TranscriptParser
from output import ReportGenerator

console = Console()


@click.group()
def cli():
    """Pikl KB Processor - Process call transcripts and emails to enhance your knowledge base."""
    pass


@cli.command()
def test_intercom():
    """Test Intercom API connection."""
    try:
        config.validate_api_keys()
        fetcher = IntercomFetcher(config.intercom_access_token)
        success = fetcher.test_connection()
        if success:
            console.print("[green]✓ Intercom connection test passed[/green]")
        else:
            console.print("[red]✗ Intercom connection test failed[/red]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Please set your API keys in .env file[/yellow]")


@cli.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("./data/kb_articles.json"),
    help="Output file path for articles",
)
def fetch_kb(output: Path):
    """Fetch existing KB articles from Intercom."""
    try:
        config.validate_api_keys()
        config.ensure_directories()

        fetcher = IntercomFetcher(config.intercom_access_token)
        articles = fetcher.fetch_all_articles()

        # Save articles
        output.parent.mkdir(parents=True, exist_ok=True)
        import json

        with open(output, "w", encoding="utf-8") as f:
            json.dump([a.model_dump() for a in articles], f, indent=2, default=str)

        console.print(f"[green]✓ Saved {len(articles)} articles to {output}[/green]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Please set your API keys in .env file[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option(
    "--kb-articles",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to KB articles JSON file",
)
@click.option(
    "--transcripts",
    type=click.Path(exists=True, path_type=Path),
    help="Path to directory containing transcript files",
)
@click.option(
    "--emails",
    type=click.Path(exists=True, path_type=Path),
    help="Path to directory containing email files",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("./reports"),
    help="Output directory for reports",
)
@click.option(
    "--generate-faqs/--no-generate-faqs",
    default=True,
    help="Generate FAQ candidates for gaps",
)
def process(
    kb_articles: Path,
    transcripts: Path | None,
    emails: Path | None,
    output: Path,
    generate_faqs: bool,
):
    """Process transcripts and emails against KB to identify gaps."""
    try:
        config.validate_api_keys()
        config.ensure_directories()

        if not transcripts and not emails:
            console.print(
                "[red]Error: Must provide at least --transcripts or --emails[/red]"
            )
            return

        # Load KB articles
        console.print(f"\n[cyan]Loading KB articles from {kb_articles}...[/cyan]")
        import json

        with open(kb_articles, "r", encoding="utf-8") as f:
            articles_data = json.load(f)

        from models import Article

        articles = [Article(**a) for a in articles_data]
        console.print(f"[green]✓ Loaded {len(articles)} KB articles[/green]")

        # Parse transcripts
        all_questions = []
        all_answers = []

        if transcripts:
            console.print(f"\n[cyan]Parsing transcripts from {transcripts}...[/cyan]")
            parser = TranscriptParser()
            parsed_transcripts = parser.parse_directory(transcripts)

            if parsed_transcripts:
                console.print(f"\n[cyan]Extracting Q&A from transcripts...[/cyan]")
                extractor = QuestionExtractor(
                    api_key=config.anthropic_api_key, model=config.llm_model
                )
                questions, answers = extractor.extract_from_transcripts(
                    parsed_transcripts
                )
                all_questions.extend(questions)
                all_answers.extend(answers)

        # Parse emails
        if emails:
            console.print(f"\n[cyan]Parsing emails from {emails}...[/cyan]")
            email_parser = EmailParser()
            parsed_emails = email_parser.parse_directory(emails)

            if parsed_emails:
                console.print(f"\n[cyan]Extracting Q&A from emails...[/cyan]")
                extractor = QuestionExtractor(
                    api_key=config.anthropic_api_key, model=config.llm_model
                )
                questions, answers = extractor.extract_from_emails(parsed_emails)
                all_questions.extend(questions)
                all_answers.extend(answers)

        if not all_questions:
            console.print("[yellow]No questions extracted. Nothing to process.[/yellow]")
            return

        console.print(
            f"\n[green]Total extracted: {len(all_questions)} questions, {len(all_answers)} answers[/green]"
        )

        # Match questions to KB
        console.print(f"\n[cyan]Matching questions to KB articles...[/cyan]")
        matcher = KBMatcher(
            embedding_model=config.embedding_model,
            similarity_threshold=config.similarity_threshold,
        )
        matcher.index_articles(articles)
        matches = matcher.match_questions(all_questions)

        # Identify gaps
        console.print(f"\n[cyan]Analyzing knowledge gaps...[/cyan]")
        gap_analyzer = GapAnalyzer(similarity_threshold=config.similarity_threshold)
        gaps = gap_analyzer.identify_gaps(matches, all_answers)
        gap_stats = gap_analyzer.get_summary_stats(gaps)

        # Generate FAQs
        faq_candidates = []
        if generate_faqs and gaps:
            console.print(f"\n[cyan]Generating FAQ candidates...[/cyan]")
            faq_generator = FAQGenerator(
                api_key=config.anthropic_api_key, model=config.llm_model
            )
            # Generate FAQs for high-priority gaps
            high_priority_gaps = gap_analyzer.get_high_priority_gaps(gaps, threshold=0.6)
            console.print(
                f"Focusing on {len(high_priority_gaps)} high-priority gaps..."
            )
            faq_candidates = faq_generator.generate_faqs(high_priority_gaps)

        # Generate reports
        console.print(f"\n[cyan]Generating reports...[/cyan]")
        reporter = ReportGenerator(output)

        report = reporter.generate_full_report(matches, gaps, faq_candidates, gap_stats)
        reporter.print_summary(report)

        # Export files
        reporter.export_gaps_to_csv(gaps)
        if faq_candidates:
            reporter.export_faqs_to_csv(faq_candidates)
            reporter.export_faqs_to_json(faq_candidates)
        reporter.generate_markdown_report(report, gaps, faq_candidates)

        console.print(f"\n[green]✓ Processing complete! Reports saved to {output}[/green]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Please set your API keys in .env file[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback

        traceback.print_exc()


@cli.command()
@click.option(
    "--gaps",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to knowledge_gaps.csv file",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("./reports"),
    help="Output directory for FAQs",
)
@click.option(
    "--limit",
    "-n",
    type=int,
    help="Limit number of FAQs to generate",
)
def generate_faqs_only(gaps: Path, output: Path, limit: int | None):
    """Generate FAQs from an existing gaps CSV file."""
    try:
        config.validate_api_keys()

        import pandas as pd
        from models import KnowledgeGap, Question, SourceType

        console.print(f"[cyan]Loading gaps from {gaps}...[/cyan]")
        df = pd.read_csv(gaps)

        if limit:
            df = df.head(limit)

        # Convert to KnowledgeGap objects
        gap_objects = []
        for _, row in df.iterrows():
            question = Question(
                text=row["question"],
                source_type=SourceType(row["source_type"]),
                source_id=row["source_id"],
                urgency_score=row["urgency_score"],
            )
            gap = KnowledgeGap(
                question=question,
                priority_score=row["priority_score"],
                theme=row.get("theme"),
            )
            gap_objects.append(gap)

        console.print(f"[green]✓ Loaded {len(gap_objects)} gaps[/green]")

        # Generate FAQs
        console.print(f"\n[cyan]Generating FAQ candidates...[/cyan]")
        faq_generator = FAQGenerator(
            api_key=config.anthropic_api_key, model=config.llm_model
        )
        faqs = faq_generator.generate_faqs(gap_objects)

        # Export
        reporter = ReportGenerator(output)
        reporter.export_faqs_to_csv(faqs)
        reporter.export_faqs_to_json(faqs)

        console.print(f"\n[green]✓ Generated {len(faqs)} FAQs saved to {output}[/green]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Please set your API keys in .env file[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option(
    "--faqs",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to faq_candidates.json file",
)
@click.option(
    "--limit",
    "-n",
    type=int,
    help="Limit number of FAQs to publish",
)
@click.option(
    "--publish",
    is_flag=True,
    default=False,
    help="Publish articles immediately (default: create as drafts)",
)
@click.option(
    "--author-id",
    type=int,
    help="Intercom admin/author ID (optional)",
)
def publish_to_intercom(
    faqs: Path, limit: int | None, publish: bool, author_id: int | None
):
    """Publish FAQ candidates to Intercom as help articles."""
    try:
        config.validate_api_keys()

        import json

        console.print(f"\n[cyan]Loading FAQ candidates from {faqs}...[/cyan]")
        with open(faqs, "r", encoding="utf-8") as f:
            faq_candidates = json.load(f)

        console.print(f"[green]✓ Loaded {len(faq_candidates)} FAQ candidates[/green]")

        if limit:
            faq_candidates = faq_candidates[:limit]
            console.print(f"[yellow]Limiting to first {limit} FAQs[/yellow]")

        # Confirm with user
        state_text = "published articles" if publish else "draft articles"
        console.print(
            f"\n[yellow]About to create {len(faq_candidates)} {state_text} in Intercom.[/yellow]"
        )
        confirm = click.confirm("Do you want to continue?", default=True)

        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            return

        # Create articles
        fetcher = IntercomFetcher(config.intercom_access_token)
        created = fetcher.create_articles_from_faqs(
            faq_candidates, author_id=author_id, publish=publish
        )

        if created:
            console.print(
                f"\n[green]✓ Successfully created {len(created)} articles in Intercom![/green]"
            )
            if not publish:
                console.print(
                    "[yellow]Articles created as drafts. Review and publish them in Intercom.[/yellow]"
                )
        else:
            console.print("[red]No articles were created.[/red]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Please set your API keys in .env file[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    cli()
