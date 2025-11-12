"""Data models for KB Processor."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Type of data source."""

    CALL_TRANSCRIPT = "call_transcript"
    EMAIL = "email"
    KB_ARTICLE = "kb_article"


class Article(BaseModel):
    """Intercom help center article."""

    id: str
    title: str
    body: str
    description: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Question(BaseModel):
    """Extracted customer question."""

    text: str
    source_type: SourceType
    source_id: str
    source_excerpt: Optional[str] = None
    timestamp: Optional[datetime] = None
    context: Optional[str] = None
    urgency_score: float = Field(default=0.5, ge=0.0, le=1.0)
    frequency: int = Field(default=1, ge=1)


class AnswerCandidate(BaseModel):
    """Potential answer extracted from agent responses."""

    text: str
    source_type: SourceType
    source_id: str
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0)
    context: Optional[str] = None


class KBMatch(BaseModel):
    """Match between a question and existing KB article."""

    question: Question
    article: Article
    similarity_score: float = Field(ge=0.0, le=1.0)
    is_good_match: bool
    notes: Optional[str] = None


class KnowledgeGap(BaseModel):
    """Identified gap in knowledge base."""

    question: Question
    best_match: Optional[KBMatch] = None
    answer_candidates: List[AnswerCandidate] = Field(default_factory=list)
    priority_score: float = Field(default=0.5, ge=0.0, le=1.0)
    theme: Optional[str] = None


class FAQCandidate(BaseModel):
    """Generated FAQ candidate to fill a knowledge gap."""

    question_text: str
    question_variants: List[str] = Field(default_factory=list)
    answer_text: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    source_references: List[str] = Field(default_factory=list)
    priority_score: float = Field(default=0.5, ge=0.0, le=1.0)
    notes: Optional[str] = None


class ProcessingReport(BaseModel):
    """Summary report of processing results."""

    generated_at: datetime = Field(default_factory=datetime.now)
    total_questions: int
    total_kb_articles: int
    good_matches: int
    knowledge_gaps: int
    faq_candidates: int
    top_themes: List[str] = Field(default_factory=list)
    coverage_percentage: float = Field(ge=0.0, le=100.0)
    recommendations: List[str] = Field(default_factory=list)
