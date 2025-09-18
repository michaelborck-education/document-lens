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

# N-gram response
class Ngram(BaseModel):
    phrase: str
    count: int

class NgramResponse(BaseModel):
    n: int
    top_ngrams: list[Ngram] = Field(default_factory=list)

# NER response models
class NEREntity(BaseModel):
    text: str
    label: str
    start_char: int
    end_char: int

class NERResponse(BaseModel):
    entities: list[NEREntity] = Field(default_factory=list)

# Keyword search models
class KeywordMatch(BaseModel):
    document: str
    context: str
    start_char: int
    end_char: int

class KeywordSearchResponse(BaseModel):
    keyword: str
    matches: list[KeywordMatch] = Field(default_factory=list)

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


# Batch processing models
class BatchJobStatus(BaseModel):
    """Status information for a batch job"""
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    progress_percentage: float = 0.0
    current_status: Literal["created", "running", "paused", "completed", "failed", "cancelled"] = "created"
    estimated_completion: str | None = None

class BatchJobCreate(BaseModel):
    """Request model for creating a new batch job"""
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    analysis_type: Literal["text", "academic", "full"] = Field(default="full")
    analysis_options: dict[str, Any] = Field(default_factory=dict)
    priority: Literal["low", "normal", "high"] = Field(default="normal")
    max_retries: int = Field(default=3, ge=0, le=10)

class BatchJobResponse(BaseModel):
    """Response model for batch job information"""
    id: str
    name: str
    description: str | None
    created_at: str
    updated_at: str
    status: BatchJobStatus
    analysis_type: str
    analysis_options: dict[str, Any]
    priority: str
    max_retries: int
    result_count: int = 0

class BatchItemCreate(BaseModel):
    """Request model for adding items to a batch job"""
    job_id: str
    items: list[dict[str, Any]] = Field(..., min_items=1, max_items=1000)

class BatchItemStatus(BaseModel):
    """Status of an individual batch item"""
    id: str
    job_id: str
    status: Literal["pending", "processing", "completed", "failed", "skipped"] = "pending"
    input_data: dict[str, Any]
    result_data: dict[str, Any] | None = None
    error_message: str | None = None
    retry_count: int = 0
    created_at: str
    processed_at: str | None = None
    processing_time: float | None = None

class BatchExportRequest(BaseModel):
    """Request model for exporting batch results"""
    job_id: str
    export_format: Literal["jsonl", "csv", "parquet"] = "jsonl"
    include_metadata: bool = True
    filter_status: list[str] | None = None  # Filter by item status

class BatchExportResponse(BaseModel):
    """Response model for batch export"""
    download_url: str
    export_format: str
    file_size_bytes: int
    item_count: int
    created_at: str
    expires_at: str
