"""Configuration management for KB Processor."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
# Try .env.local first (for local development), then fall back to .env
load_dotenv('.env.local')
load_dotenv()  # This won't override existing variables


class Config(BaseModel):
    """Application configuration."""

    # API Keys
    anthropic_api_key: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    intercom_access_token: str = Field(
        default_factory=lambda: os.getenv("INTERCOM_ACCESS_TOKEN", "")
    )

    # Model Configuration
    llm_model: str = Field(
        default_factory=lambda: os.getenv("LLM_MODEL", "claude-sonnet-4-5-20250929")
    )
    embedding_model: str = Field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
    )

    # Processing Configuration
    batch_size: int = Field(default_factory=lambda: int(os.getenv("BATCH_SIZE", "10")))
    similarity_threshold: float = Field(
        default_factory=lambda: float(os.getenv("SIMILARITY_THRESHOLD", "0.75"))
    )

    # Paths
    db_path: Path = Field(
        default_factory=lambda: Path(os.getenv("DB_PATH", "./data/kb_processor.db"))
    )
    data_dir: Path = Field(default=Path("./data"))
    reports_dir: Path = Field(default=Path("./reports"))

    def validate_api_keys(self) -> None:
        """Validate that required API keys are set."""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        if not self.intercom_access_token:
            raise ValueError("INTERCOM_ACCESS_TOKEN not set in environment")

    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()
