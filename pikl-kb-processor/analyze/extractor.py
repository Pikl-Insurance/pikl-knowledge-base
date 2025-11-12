"""Question and answer extraction from transcripts and emails using LLM."""

import json
from typing import List, Optional

import anthropic
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from anonymize import PIIAnonymizer
from ingest.emails import ParsedEmail
from ingest.transcripts import ParsedTranscript
from models import AnswerCandidate, Question, SourceType

console = Console()


class QuestionExtractor:
    """Extract questions and answers from customer interactions using Claude."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929", anonymize: bool = True):
        """Initialize question extractor.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            anonymize: Whether to anonymize PII before sending to API (default: True)
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.anonymize_enabled = anonymize
        self.anonymizer = PIIAnonymizer() if anonymize else None

    def extract_from_transcripts(
        self, transcripts: List[ParsedTranscript]
    ) -> tuple[List[Question], List[AnswerCandidate]]:
        """Extract questions and answers from call transcripts.

        Args:
            transcripts: List of parsed transcripts

        Returns:
            Tuple of (questions, answer_candidates)
        """
        all_questions = []
        all_answers = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Extracting Q&A from {len(transcripts)} transcripts...", total=len(transcripts)
            )

            for transcript in transcripts:
                try:
                    questions, answers = self._extract_from_transcript(transcript)
                    all_questions.extend(questions)
                    all_answers.extend(answers)
                    progress.advance(task)
                except Exception as e:
                    console.print(
                        f"[yellow]Warning: Failed to extract from transcript {transcript.id}: {e}[/yellow]"
                    )
                    progress.advance(task)

        console.print(
            f"[green]Extracted {len(all_questions)} questions and {len(all_answers)} answers[/green]"
        )

        # Print anonymization stats if enabled
        if self.anonymize_enabled and self.anonymizer:
            stats = self.anonymizer.get_stats()
            console.print(
                f"[cyan]PII Anonymization: {stats['emails_anonymized']} emails, "
                f"{stats['policies_anonymized']} policies, {stats['names_anonymized']} names[/cyan]"
            )

        return all_questions, all_answers

    def extract_from_emails(
        self, emails: List[ParsedEmail]
    ) -> tuple[List[Question], List[AnswerCandidate]]:
        """Extract questions and answers from emails.

        Args:
            emails: List of parsed emails

        Returns:
            Tuple of (questions, answer_candidates)
        """
        all_questions = []
        all_answers = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Extracting Q&A from {len(emails)} emails...", total=len(emails)
            )

            for email in emails:
                try:
                    questions, answers = self._extract_from_email(email)
                    all_questions.extend(questions)
                    all_answers.extend(answers)
                    progress.advance(task)
                except Exception as e:
                    console.print(
                        f"[yellow]Warning: Failed to extract from email {email.id}: {e}[/yellow]"
                    )
                    progress.advance(task)

        console.print(
            f"[green]Extracted {len(all_questions)} questions and {len(all_answers)} answers[/green]"
        )

        # Print anonymization stats if enabled
        if self.anonymize_enabled and self.anonymizer:
            stats = self.anonymizer.get_stats()
            console.print(
                f"[cyan]PII Anonymization: {stats['emails_anonymized']} emails, "
                f"{stats['policies_anonymized']} policies, {stats['names_anonymized']} names[/cyan]"
            )

        return all_questions, all_answers

    def _extract_from_transcript(
        self, transcript: ParsedTranscript
    ) -> tuple[List[Question], List[AnswerCandidate]]:
        """Extract questions and answers from a single transcript.

        Args:
            transcript: Parsed transcript

        Returns:
            Tuple of (questions, answer_candidates)
        """
        # Build conversation text
        conversation = []
        for turn in transcript.turns:
            text = turn.text
            # Anonymize PII if enabled
            if self.anonymize_enabled and self.anonymizer:
                text = self.anonymizer.anonymize_text(text)
            conversation.append(f"{turn.speaker}: {text}")
        conversation_text = "\n".join(conversation)

        # Create prompt for Claude
        prompt = f"""Analyze this customer service call transcript and extract:
1. All questions asked by the customer (including implicit questions or concerns)
2. The answers/responses provided by the agent

For each question, provide:
- The question text (paraphrased if needed for clarity)
- A brief context excerpt from the conversation
- An urgency score (0.0-1.0, where 1.0 is highly urgent/critical)

For each answer, provide:
- The answer text (summarized if verbose)
- A confidence score (0.0-1.0, based on how definitive/accurate the answer seems)
- Brief context

Return your analysis as JSON in this exact format:
{{
  "questions": [
    {{"text": "...", "context": "...", "urgency": 0.7}}
  ],
  "answers": [
    {{"text": "...", "context": "...", "confidence": 0.9}}
  ]
}}

Transcript:
{conversation_text}"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            response_text = message.content[0].text

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            data = json.loads(response_text)

            # Create Question objects
            questions = []
            for q_data in data.get("questions", []):
                question = Question(
                    text=q_data["text"],
                    source_type=SourceType.CALL_TRANSCRIPT,
                    source_id=transcript.id,
                    source_excerpt=q_data.get("context"),
                    urgency_score=q_data.get("urgency", 0.5),
                    context=q_data.get("context"),
                )
                questions.append(question)

            # Create AnswerCandidate objects
            answers = []
            for a_data in data.get("answers", []):
                answer = AnswerCandidate(
                    text=a_data["text"],
                    source_type=SourceType.CALL_TRANSCRIPT,
                    source_id=transcript.id,
                    confidence_score=a_data.get("confidence", 0.5),
                    context=a_data.get("context"),
                )
                answers.append(answer)

            return questions, answers

        except json.JSONDecodeError as e:
            console.print(
                f"[yellow]Warning: Failed to parse LLM response for transcript {transcript.id}: {e}[/yellow]"
            )
            console.print(f"[dim]Response was: {response_text[:500]}...[/dim]")
            return [], []
        except Exception as e:
            console.print(
                f"[red]Error extracting from transcript {transcript.id}: {e}[/red]"
            )
            return [], []

    def _extract_from_email(
        self, email: ParsedEmail
    ) -> tuple[List[Question], List[AnswerCandidate]]:
        """Extract questions and answers from a single email.

        Args:
            email: Parsed email

        Returns:
            Tuple of (questions, answer_candidates)
        """
        # Build email text and anonymize if enabled
        from_addr = email.from_address
        subject = email.subject
        body = email.body_text

        if self.anonymize_enabled and self.anonymizer:
            from_addr = self.anonymizer.anonymize_text(from_addr)
            subject = self.anonymizer.anonymize_text(subject)
            body = self.anonymizer.anonymize_text(body)

        email_text = f"""From: {from_addr}
Subject: {subject}
Date: {email.date}

{body}"""

        # Determine if this is a customer question or agent response
        is_customer_email = not email.is_reply  # Simple heuristic

        prompt = f"""Analyze this customer service email and extract:
1. Questions asked (if this is from a customer)
2. Answers provided (if this is from a support agent)

Email type: {"Customer inquiry" if is_customer_email else "Support response"}

For each question, provide:
- The question text (paraphrased if needed for clarity)
- An urgency score (0.0-1.0)

For each answer, provide:
- The answer text (summarized if verbose)
- A confidence score (0.0-1.0)

Return your analysis as JSON in this exact format:
{{
  "questions": [
    {{"text": "...", "urgency": 0.7}}
  ],
  "answers": [
    {{"text": "...", "confidence": 0.9}}
  ]
}}

Email:
{email_text}"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            data = json.loads(response_text)

            # Create Question objects
            questions = []
            for q_data in data.get("questions", []):
                question = Question(
                    text=q_data["text"],
                    source_type=SourceType.EMAIL,
                    source_id=email.id,
                    source_excerpt=email.subject,
                    urgency_score=q_data.get("urgency", 0.5),
                    context=f"From: {email.from_address}\nSubject: {email.subject}",
                )
                questions.append(question)

            # Create AnswerCandidate objects
            answers = []
            for a_data in data.get("answers", []):
                answer = AnswerCandidate(
                    text=a_data["text"],
                    source_type=SourceType.EMAIL,
                    source_id=email.id,
                    confidence_score=a_data.get("confidence", 0.5),
                    context=f"Subject: {email.subject}",
                )
                answers.append(answer)

            return questions, answers

        except json.JSONDecodeError as e:
            console.print(
                f"[yellow]Warning: Failed to parse LLM response for email {email.id}: {e}[/yellow]"
            )
            console.print(f"[dim]Response was: {response_text[:500]}...[/dim]")
            return [], []
        except Exception as e:
            console.print(f"[red]Error extracting from email {email.id}: {e}[/red]")
            return [], []
