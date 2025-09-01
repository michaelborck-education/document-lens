"""
Pydantic schemas for CiteSight API
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


# Request models
class AnalysisOptions(BaseModel):
    citation_style: Literal["auto", "apa", "mla", "chicago"] = Field(default="auto")
    check_urls: bool = Field(default=True)
    check_doi: bool = Field(default=True)
    check_wayback: bool = Field(default=True)
    check_plagiarism: bool = Field(default=True)
    check_in_text: bool = Field(default=True)
    processing_mode: Literal["server", "local"] = Field(default="server")

# Result models
class Pattern(BaseModel):
    text: str
    severity: Literal["high", "medium", "low"]

class Issue(BaseModel):
    type: Literal["error", "warning"]
    title: str
    details: str

class WordFrequency(BaseModel):
    word: str
    count: int
    size: int

class PhraseCount(BaseModel):
    phrase: str
    count: int

class DocumentComparison(BaseModel):
    name: str
    word_count: int
    readability: float
    references: int
    issues: int

class SuspiciousPatterns(BaseModel):
    self_plagiarism: list[str] = Field(default_factory=list)
    citation_anomalies: list[str] = Field(default_factory=list)
    style_inconsistencies: list[str] = Field(default_factory=list)
    ai_indicators: dict[str, Any] = Field(default_factory=dict)
    integrity_score: float = Field(default=100.0)
    all_issues: list[str] = Field(default_factory=list)

class ReferenceResults(BaseModel):
    total: int
    broken_urls: int
    unresolved_dois: int
    missing_in_text: int
    orphaned_in_text: int
    issues: list[Issue] = Field(default_factory=list)

class DocumentAnalysis(BaseModel):
    word_count: int
    sentence_count: int
    avg_words_per_sentence: float
    paragraph_count: int
    flesch_score: float
    flesch_kincaid_grade: float

class WritingQuality(BaseModel):
    passive_voice_percentage: float
    sentence_variety: float
    transition_words: float
    hedging_language: float
    academic_tone: float

class WordAnalysis(BaseModel):
    most_frequent: list[WordFrequency] = Field(default_factory=list)
    unique_words: list[str] = Field(default_factory=list)
    unique_phrases: list[PhraseCount] = Field(default_factory=list)

class AnalysisResults(BaseModel):
    references: ReferenceResults
    suspicious_patterns: SuspiciousPatterns
    document_analysis: DocumentAnalysis
    writing_quality: WritingQuality
    word_analysis: WordAnalysis
    comparison: list[DocumentComparison] | None = None
    processing_time: float
    file_count: int

# Response models
class ApiResponse(BaseModel):
    status: Literal["success", "error"]
    message: str | None = None
    data: dict | None = None

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float

class ErrorResponse(BaseModel):
    error: str
    details: str | None = None
    code: int | None = None
