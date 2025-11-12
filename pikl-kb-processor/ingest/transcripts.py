"""Transcript parser for processing call transcripts."""

import json
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd
from pydantic import BaseModel
from rich.console import Console
from rich.progress import track

console = Console()


class TranscriptTurn(BaseModel):
    """A single turn in a conversation transcript."""

    speaker: str  # "customer", "agent", etc.
    text: str
    timestamp: Optional[Union[str, int, float]] = None  # Accept string, int, or float
    confidence: Optional[float] = None


class ParsedTranscript(BaseModel):
    """Parsed call transcript data."""

    id: str  # Unique identifier for this transcript
    turns: List[TranscriptTurn]
    metadata: dict = {}  # Additional metadata (duration, date, customer_id, etc.)


class TranscriptParser:
    """Parser for call transcript files (JSON, CSV formats)."""

    def __init__(self):
        """Initialize transcript parser."""
        self.supported_extensions = [".json", ".jsonl", ".csv"]

    def parse_directory(self, directory: Path) -> List[ParsedTranscript]:
        """Parse all transcript files in a directory.

        Args:
            directory: Path to directory containing transcript files

        Returns:
            List of ParsedTranscript objects
        """
        if not directory.exists() or not directory.is_dir():
            console.print(f"[red]Error: Directory not found: {directory}[/red]")
            return []

        transcript_files = []
        for ext in self.supported_extensions:
            transcript_files.extend(directory.glob(f"**/*{ext}"))

        if not transcript_files:
            console.print(
                f"[yellow]No transcript files found in {directory}[/yellow]"
            )
            return []

        console.print(f"Found {len(transcript_files)} transcript files")

        parsed_transcripts = []
        for transcript_file in track(
            transcript_files, description="Parsing transcripts...", console=console
        ):
            try:
                parsed = self.parse_file(transcript_file)
                if parsed:
                    parsed_transcripts.append(parsed)
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Failed to parse {transcript_file.name}: {e}[/yellow]"
                )

        console.print(
            f"[green]Successfully parsed {len(parsed_transcripts)} transcripts[/green]"
        )
        return parsed_transcripts

    def parse_file(self, file_path: Path) -> Optional[ParsedTranscript]:
        """Parse a single transcript file.

        Args:
            file_path: Path to transcript file

        Returns:
            ParsedTranscript object or None if parsing fails
        """
        suffix = file_path.suffix.lower()

        if suffix == ".json":
            return self._parse_json(file_path)
        elif suffix == ".jsonl":
            return self._parse_jsonl(file_path)
        elif suffix == ".csv":
            return self._parse_csv(file_path)
        else:
            console.print(
                f"[yellow]Unsupported file type: {file_path.suffix}[/yellow]"
            )
            return None

    def _parse_json(self, file_path: Path) -> Optional[ParsedTranscript]:
        """Parse JSON format transcript.

        Expected format:
        {
            "id": "call_123",
            "turns": [
                {"speaker": "customer", "text": "...", "timestamp": "00:00:12"},
                {"speaker": "agent", "text": "...", "timestamp": "00:00:25"}
            ],
            "metadata": {...}
        }

        Args:
            file_path: Path to JSON file

        Returns:
            ParsedTranscript object or None if parsing fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle different JSON structures
            if isinstance(data, dict):
                # Standard format
                transcript_id = data.get("id", file_path.stem)
                turns_data = data.get("turns", data.get("conversation", []))
                metadata = data.get("metadata", {})
            elif isinstance(data, list):
                # Array of turns
                transcript_id = file_path.stem
                turns_data = data
                metadata = {}
            else:
                console.print(
                    f"[yellow]Unexpected JSON structure in {file_path.name}[/yellow]"
                )
                return None

            # Parse turns
            turns = []
            for turn_data in turns_data:
                try:
                    turn = TranscriptTurn(
                        speaker=turn_data.get("speaker", "unknown"),
                        text=turn_data.get("text", ""),
                        timestamp=turn_data.get("timestamp"),
                        confidence=turn_data.get("confidence"),
                    )
                    turns.append(turn)
                except Exception as e:
                    console.print(f"[yellow]Warning: Skipping invalid turn: {e}[/yellow]")
                    continue

            if not turns:
                console.print(f"[yellow]No valid turns found in {file_path.name}[/yellow]")
                return None

            return ParsedTranscript(
                id=transcript_id,
                turns=turns,
                metadata=metadata,
            )

        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON in {file_path}: {e}[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Error parsing {file_path}: {e}[/red]")
            return None

    def _parse_jsonl(self, file_path: Path) -> Optional[ParsedTranscript]:
        """Parse JSONL format transcript (one turn per line).

        Expected format (each line):
        {"speaker": "customer", "text": "...", "timestamp": "00:00:12"}

        Args:
            file_path: Path to JSONL file

        Returns:
            ParsedTranscript object or None if parsing fails
        """
        try:
            turns = []
            metadata = {}

            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        turn_data = json.loads(line)

                        # Check if this is metadata line
                        if turn_data.get("type") == "metadata":
                            metadata.update(turn_data.get("data", {}))
                            continue

                        turn = TranscriptTurn(
                            speaker=turn_data.get("speaker", "unknown"),
                            text=turn_data.get("text", ""),
                            timestamp=turn_data.get("timestamp"),
                            confidence=turn_data.get("confidence"),
                        )
                        turns.append(turn)
                    except json.JSONDecodeError:
                        console.print(
                            f"[yellow]Warning: Invalid JSON on line {line_num}[/yellow]"
                        )
                        continue
                    except Exception as e:
                        console.print(
                            f"[yellow]Warning: Error parsing line {line_num}: {e}[/yellow]"
                        )
                        continue

            if not turns:
                console.print(f"[yellow]No valid turns found in {file_path.name}[/yellow]")
                return None

            return ParsedTranscript(
                id=file_path.stem,
                turns=turns,
                metadata=metadata,
            )

        except Exception as e:
            console.print(f"[red]Error parsing {file_path}: {e}[/red]")
            return None

    def _parse_csv(self, file_path: Path) -> Optional[ParsedTranscript]:
        """Parse CSV format transcript.

        Expected columns: speaker, text, timestamp (optional), confidence (optional)

        Args:
            file_path: Path to CSV file

        Returns:
            ParsedTranscript object or None if parsing fails
        """
        try:
            df = pd.read_csv(file_path)

            # Check required columns
            if "speaker" not in df.columns or "text" not in df.columns:
                console.print(
                    f"[red]CSV must have 'speaker' and 'text' columns: {file_path.name}[/red]"
                )
                return None

            turns = []
            for _, row in df.iterrows():
                try:
                    turn = TranscriptTurn(
                        speaker=str(row["speaker"]),
                        text=str(row["text"]),
                        timestamp=str(row["timestamp"]) if "timestamp" in row and pd.notna(row["timestamp"]) else None,
                        confidence=float(row["confidence"]) if "confidence" in row and pd.notna(row["confidence"]) else None,
                    )
                    turns.append(turn)
                except Exception as e:
                    console.print(f"[yellow]Warning: Skipping invalid row: {e}[/yellow]")
                    continue

            if not turns:
                console.print(f"[yellow]No valid turns found in {file_path.name}[/yellow]")
                return None

            return ParsedTranscript(
                id=file_path.stem,
                turns=turns,
                metadata={},
            )

        except Exception as e:
            console.print(f"[red]Error parsing CSV {file_path}: {e}[/red]")
            return None

    def get_full_text(self, transcript: ParsedTranscript) -> str:
        """Get full conversation text from transcript.

        Args:
            transcript: ParsedTranscript object

        Returns:
            Full conversation as formatted string
        """
        lines = []
        for turn in transcript.turns:
            timestamp = f"[{turn.timestamp}] " if turn.timestamp else ""
            lines.append(f"{timestamp}{turn.speaker}: {turn.text}")
        return "\n".join(lines)

    def get_customer_questions(self, transcript: ParsedTranscript) -> List[str]:
        """Extract customer questions from transcript.

        Args:
            transcript: ParsedTranscript object

        Returns:
            List of customer utterances that appear to be questions
        """
        questions = []
        for turn in transcript.turns:
            if turn.speaker.lower() in ["customer", "caller", "user"]:
                text = turn.text.strip()
                # Simple heuristic: contains question mark or starts with question word
                if "?" in text or any(
                    text.lower().startswith(q)
                    for q in ["what", "how", "why", "when", "where", "who", "can", "could", "would", "is", "are", "do", "does"]
                ):
                    questions.append(text)
        return questions

    def get_agent_responses(self, transcript: ParsedTranscript) -> List[str]:
        """Extract agent responses from transcript.

        Args:
            transcript: ParsedTranscript object

        Returns:
            List of agent utterances
        """
        responses = []
        for turn in transcript.turns:
            if turn.speaker.lower() in ["agent", "representative", "support", "operator"]:
                responses.append(turn.text.strip())
        return responses
