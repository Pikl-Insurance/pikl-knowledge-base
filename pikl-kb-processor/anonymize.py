"""PII anonymization for transcripts and emails."""

import re
from typing import Dict, List, Set

from rich.console import Console

console = Console()


class PIIAnonymizer:
    """Anonymize PII in text while maintaining context."""

    def __init__(self):
        """Initialize anonymizer with patterns."""
        # Mapping to track replacements for consistency
        self.name_map: Dict[str, str] = {}
        self.email_map: Dict[str, str] = {}
        self.policy_map: Dict[str, str] = {}

        # Counters for generating placeholder names
        self.name_counter = 0
        self.email_counter = 0
        self.policy_counter = 0

        # Regex patterns for PII detection
        self.patterns = {
            # Email addresses
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',

            # Phone numbers (various formats)
            "phone": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',

            # UK/AU phone with intl codes
            "intl_phone": r'\+(?:44|61|27)\s?\d{2,4}\s?\d{3,4}\s?\d{3,4}',

            # Policy numbers (common patterns)
            "policy_ref": r'\b[A-Z]{2,4}[-\s]?[0-9X]{2,4}[-\s]?[A-Z0-9]{2,4}[-\s]?[0-9]{2}\b',

            # Credit cards (basic pattern)
            "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',

            # SSN/TFN
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',

            # Driver's license (varies by region, basic pattern)
            "license": r'\b[A-Z]{1,2}\d{6,8}\b',

            # Addresses - street numbers with street names
            "address": r'\b\d{1,5}\s+(?:[A-Z][a-z]+\s+){1,3}(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Court|Ct|Boulevard|Blvd)\b',

            # Postal codes (UK, AU formats)
            "postal_code": r'\b[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}\b|\b\d{4}\b',

            # Dates (potential DOB)
            "date": r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',
        }

    def anonymize_text(self, text: str) -> str:
        """Anonymize PII in text.

        Args:
            text: Text potentially containing PII

        Returns:
            Anonymized text
        """
        if not text:
            return text

        anonymized = text

        # 1. Anonymize emails (do this first to avoid interfering with other patterns)
        anonymized = self._anonymize_emails(anonymized)

        # 2. Anonymize policy references
        anonymized = self._anonymize_policies(anonymized)

        # 3. Anonymize phone numbers
        anonymized = self._anonymize_phones(anonymized)

        # 4. Anonymize credit cards
        anonymized = re.sub(self.patterns["credit_card"], "[REDACTED_CARD]", anonymized)

        # 5. Anonymize SSN/TFN
        anonymized = re.sub(self.patterns["ssn"], "[REDACTED_ID]", anonymized)

        # 6. Anonymize addresses
        anonymized = re.sub(self.patterns["address"], "[REDACTED_ADDRESS]", anonymized)

        # 7. Anonymize postal codes
        anonymized = re.sub(self.patterns["postal_code"], "[REDACTED_POSTCODE]", anonymized)

        # 8. Anonymize license numbers
        anonymized = re.sub(self.patterns["license"], "[REDACTED_LICENSE]", anonymized)

        # 9. Anonymize dates (be careful not to remove timestamps)
        anonymized = self._anonymize_dates(anonymized)

        # 10. Anonymize names (do this last as it's the most complex)
        anonymized = self._anonymize_names(anonymized)

        return anonymized

    def _anonymize_emails(self, text: str) -> str:
        """Anonymize email addresses consistently."""
        def replace_email(match):
            email = match.group(0)
            if email not in self.email_map:
                self.email_counter += 1
                self.email_map[email] = f"customer{self.email_counter}@example.com"
            return self.email_map[email]

        return re.sub(self.patterns["email"], replace_email, text)

    def _anonymize_policies(self, text: str) -> str:
        """Anonymize policy reference numbers consistently."""
        def replace_policy(match):
            policy = match.group(0)
            if policy not in self.policy_map:
                self.policy_counter += 1
                self.policy_map[policy] = f"POL-{self.policy_counter:04d}"
            return self.policy_map[policy]

        return re.sub(self.patterns["policy_ref"], replace_policy, text)

    def _anonymize_phones(self, text: str) -> str:
        """Anonymize phone numbers."""
        text = re.sub(self.patterns["phone"], "[REDACTED_PHONE]", text)
        text = re.sub(self.patterns["intl_phone"], "[REDACTED_PHONE]", text)
        return text

    def _anonymize_dates(self, text: str) -> str:
        """Anonymize specific dates while keeping relative time references."""
        # Don't remove things like "today", "yesterday", "next week"
        # Only remove specific dates
        def replace_date(match):
            date = match.group(0)
            # Keep if it looks like a year only
            if re.match(r'^\d{4}$', date):
                return date
            return "[REDACTED_DATE]"

        return re.sub(self.patterns["date"], replace_date, text)

    def _anonymize_names(self, text: str) -> str:
        """Anonymize person names (heuristic approach).

        This is challenging as names can be common words. We use a conservative
        approach focusing on obvious name patterns.
        """
        # Pattern: Capitalized words that might be names
        # We'll look for title + name patterns: Mr./Mrs./Ms. + Name
        title_pattern = r'\b(?:Mr\.?|Mrs\.?|Ms\.?|Miss|Dr\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'

        def replace_name(match):
            name = match.group(1)
            if name not in self.name_map:
                self.name_counter += 1
                # Generate plausible placeholder names
                placeholder_names = [
                    "Smith", "Johnson", "Williams", "Brown", "Jones",
                    "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"
                ]
                self.name_map[name] = placeholder_names[self.name_counter % len(placeholder_names)]

            title = match.group(0).split()[0]
            return f"{title} {self.name_map[name]}"

        return re.sub(title_pattern, replace_name, text)

    def get_stats(self) -> Dict[str, int]:
        """Get anonymization statistics.

        Returns:
            Dictionary of anonymization counts
        """
        return {
            "names_anonymized": len(self.name_map),
            "emails_anonymized": len(self.email_map),
            "policies_anonymized": len(self.policy_map),
        }


def anonymize_transcript(transcript: dict, anonymizer: PIIAnonymizer) -> dict:
    """Anonymize PII in a transcript.

    Args:
        transcript: Transcript dictionary
        anonymizer: PIIAnonymizer instance

    Returns:
        Anonymized transcript
    """
    anonymized = transcript.copy()

    # Anonymize each turn
    if "turns" in anonymized:
        anonymized["turns"] = []
        for turn in transcript["turns"]:
            anonymized_turn = turn.copy()
            if "text" in anonymized_turn:
                anonymized_turn["text"] = anonymizer.anonymize_text(turn["text"])
            anonymized["turns"].append(anonymized_turn)

    return anonymized


def anonymize_email(email: dict, anonymizer: PIIAnonymizer) -> dict:
    """Anonymize PII in an email.

    Args:
        email: Email dictionary
        anonymizer: PIIAnonymizer instance

    Returns:
        Anonymized email
    """
    anonymized = email.copy()

    # Anonymize subject
    if "subject" in anonymized:
        anonymized["subject"] = anonymizer.anonymize_text(email["subject"])

    # Anonymize body
    if "body_text" in anonymized:
        anonymized["body_text"] = anonymizer.anonymize_text(email["body_text"])

    # Anonymize sender/recipient (email addresses handled by pattern)
    if "from_address" in anonymized:
        anonymized["from_address"] = anonymizer.anonymize_text(email["from_address"])

    if "to_address" in anonymized:
        anonymized["to_address"] = anonymizer.anonymize_text(email["to_address"])

    return anonymized


if __name__ == "__main__":
    # Test the anonymizer
    anonymizer = PIIAnonymizer()

    test_text = """
    Hello, this is John Smith from john.smith@example.com.
    My policy number is GLDX-02HQ-01 and my phone is 555-123-4567.
    I live at 123 Main Street, and my card ending in 1234-5678-9012-3456.
    My DOB is 01/15/1980.
    """

    print("Original:")
    print(test_text)
    print("\nAnonymized:")
    print(anonymizer.anonymize_text(test_text))
    print("\nStats:")
    print(anonymizer.get_stats())
