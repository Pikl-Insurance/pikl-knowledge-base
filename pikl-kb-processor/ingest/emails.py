"""Email parser for processing customer emails."""

import email
from datetime import datetime
from email.header import decode_header
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel
from rich.console import Console
from rich.progress import track

console = Console()


class ParsedEmail(BaseModel):
    """Parsed email data."""

    id: str  # Generated from filename or message-id
    subject: str
    from_address: str
    to_address: Optional[str] = None
    date: Optional[datetime] = None
    body_text: str
    body_html: Optional[str] = None
    is_reply: bool = False
    thread_id: Optional[str] = None


class EmailParser:
    """Parser for email files (EML, MSG formats)."""

    def __init__(self):
        """Initialize email parser."""
        self.supported_extensions = [".eml", ".msg"]

    def parse_directory(self, directory: Path) -> List[ParsedEmail]:
        """Parse all email files in a directory.

        Args:
            directory: Path to directory containing email files

        Returns:
            List of ParsedEmail objects
        """
        if not directory.exists() or not directory.is_dir():
            console.print(f"[red]Error: Directory not found: {directory}[/red]")
            return []

        email_files = []
        for ext in self.supported_extensions:
            email_files.extend(directory.glob(f"**/*{ext}"))

        if not email_files:
            console.print(
                f"[yellow]No email files found in {directory}[/yellow]"
            )
            return []

        console.print(f"Found {len(email_files)} email files")

        parsed_emails = []
        for email_file in track(
            email_files, description="Parsing emails...", console=console
        ):
            try:
                parsed = self.parse_file(email_file)
                if parsed:
                    parsed_emails.append(parsed)
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Failed to parse {email_file.name}: {e}[/yellow]"
                )

        console.print(
            f"[green]Successfully parsed {len(parsed_emails)} emails[/green]"
        )
        return parsed_emails

    def parse_file(self, file_path: Path) -> Optional[ParsedEmail]:
        """Parse a single email file.

        Args:
            file_path: Path to email file

        Returns:
            ParsedEmail object or None if parsing fails
        """
        if file_path.suffix.lower() == ".eml":
            return self._parse_eml(file_path)
        elif file_path.suffix.lower() == ".msg":
            return self._parse_msg(file_path)
        else:
            console.print(
                f"[yellow]Unsupported file type: {file_path.suffix}[/yellow]"
            )
            return None

    def _parse_eml(self, file_path: Path) -> Optional[ParsedEmail]:
        """Parse EML format email.

        Args:
            file_path: Path to EML file

        Returns:
            ParsedEmail object or None if parsing fails
        """
        try:
            with open(file_path, "rb") as f:
                msg = email.message_from_binary_file(f)

            # Extract basic headers
            subject = self._decode_header(msg.get("Subject", ""))
            from_addr = self._decode_header(msg.get("From", ""))
            to_addr = self._decode_header(msg.get("To", ""))
            date_str = msg.get("Date")
            message_id = msg.get("Message-ID", str(file_path.stem))

            # Parse date
            date_obj = None
            if date_str:
                try:
                    date_obj = email.utils.parsedate_to_datetime(date_str)
                except Exception:
                    pass

            # Extract body
            body_text = ""
            body_html = None

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        try:
                            body_text = part.get_payload(decode=True).decode(
                                part.get_content_charset() or "utf-8", errors="ignore"
                            )
                        except Exception:
                            pass
                    elif content_type == "text/html":
                        try:
                            body_html = part.get_payload(decode=True).decode(
                                part.get_content_charset() or "utf-8", errors="ignore"
                            )
                        except Exception:
                            pass
            else:
                try:
                    body_text = msg.get_payload(decode=True).decode(
                        msg.get_content_charset() or "utf-8", errors="ignore"
                    )
                except Exception:
                    body_text = str(msg.get_payload())

            # Determine if it's a reply
            is_reply = (
                subject.lower().startswith("re:")
                or subject.lower().startswith("fwd:")
            )

            # Extract thread ID from In-Reply-To or References headers
            thread_id = msg.get("In-Reply-To") or msg.get("References")
            if thread_id and isinstance(thread_id, str):
                thread_id = thread_id.split()[0]  # Get first message ID

            return ParsedEmail(
                id=self._clean_message_id(message_id),
                subject=subject,
                from_address=from_addr,
                to_address=to_addr,
                date=date_obj,
                body_text=body_text.strip(),
                body_html=body_html,
                is_reply=is_reply,
                thread_id=self._clean_message_id(thread_id) if thread_id else None,
            )

        except Exception as e:
            console.print(f"[red]Error parsing {file_path}: {e}[/red]")
            return None

    def _parse_msg(self, file_path: Path) -> Optional[ParsedEmail]:
        """Parse MSG format email (Outlook).

        Note: This requires extract-msg package for full MSG support.
        For now, we'll return None and suggest converting to EML.

        Args:
            file_path: Path to MSG file

        Returns:
            ParsedEmail object or None
        """
        try:
            import extract_msg

            msg = extract_msg.Message(file_path)

            # Parse date
            date_obj = None
            if msg.date:
                try:
                    date_obj = datetime.fromisoformat(str(msg.date))
                except Exception:
                    pass

            is_reply = (
                str(msg.subject).lower().startswith("re:")
                or str(msg.subject).lower().startswith("fwd:")
            )

            return ParsedEmail(
                id=str(file_path.stem),
                subject=str(msg.subject or ""),
                from_address=str(msg.sender or ""),
                to_address=str(msg.to or ""),
                date=date_obj,
                body_text=str(msg.body or "").strip(),
                body_html=str(msg.htmlBody) if msg.htmlBody else None,
                is_reply=is_reply,
                thread_id=None,  # MSG format doesn't easily expose this
            )

        except ImportError:
            console.print(
                "[yellow]Warning: extract-msg not installed. Install with: pip install extract-msg[/yellow]"
            )
            console.print(
                f"[yellow]Skipping MSG file: {file_path.name}[/yellow]"
            )
            return None
        except Exception as e:
            console.print(f"[red]Error parsing MSG file {file_path}: {e}[/red]")
            return None

    def _decode_header(self, header_value: Optional[str]) -> str:
        """Decode email header value.

        Args:
            header_value: Raw header value

        Returns:
            Decoded string
        """
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        decoded_str = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    decoded_str += part.decode(encoding or "utf-8", errors="ignore")
                except Exception:
                    decoded_str += part.decode("utf-8", errors="ignore")
            else:
                decoded_str += str(part)

        return decoded_str.strip()

    def _clean_message_id(self, message_id: str) -> str:
        """Clean message ID by removing angle brackets.

        Args:
            message_id: Raw message ID

        Returns:
            Cleaned message ID
        """
        return message_id.strip("<>")
