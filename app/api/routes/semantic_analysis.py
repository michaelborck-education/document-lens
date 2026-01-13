"""Semantic analysis endpoints: domain mapping, structural mismatch, sentiment."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.analyzers.domain_mapper import DomainMapper
from app.analyzers.sentiment_analyzer import GranularSentimentAnalyzer
from app.analyzers.structural_mismatch import StructuralMismatchAnalyzer
from app.core.config import settings
from app.models.schemas import (
    DomainMappingResponse,
    GranularSentimentResponse,
    StructuralMismatchResponse,
)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Initialize analyzers at module level (efficient for PyInstaller)
domain_mapper = DomainMapper()
mismatch_analyzer = StructuralMismatchAnalyzer()
sentiment_analyzer = GranularSentimentAnalyzer()


# ===== Request Models =====
class DomainMappingRequest(BaseModel):
    """Request for domain mapping analysis."""

    text: str
    domains: list[str]


class StructuralMismatchRequest(BaseModel):
    """Request for structural mismatch detection."""

    text: str
    domains: list[str]
    threshold: float = 0.3  # Dislocation threshold


class SentimentAnalysisRequest(BaseModel):
    """Request for granular sentiment analysis."""

    text: str


# ===== Endpoints =====
@router.post("/domain-mapping", response_model=DomainMappingResponse)
@limiter.limit(settings.RATE_LIMIT)
async def analyze_domain_mapping(
    request: Request, req: DomainMappingRequest
) -> DomainMappingResponse:
    """
    Map document sections to user-defined domains using semantic similarity.

    Uses sentence-transformers (all-MiniLM-L6-v2) to calculate cosine similarity
    between detected section headers and provided domains.

    Example domains: ["Teaching", "Research", "Service", "Administration"]
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if not req.domains or len(req.domains) < 2:
        raise HTTPException(
            status_code=400,
            detail="Must provide at least 2 domains for mapping"
        )

    try:
        result = domain_mapper.analyze(req.text, req.domains)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Domain mapping failed: {e!s}"
        ) from e


@router.post("/structural-mismatch", response_model=StructuralMismatchResponse)
@limiter.limit(settings.RATE_LIMIT)
async def analyze_structural_mismatch(
    request: Request, req: StructuralMismatchRequest
) -> StructuralMismatchResponse:
    """
    Detect thematic dislocation of sentences within sections.

    Compares the semantic domain of each sentence vs its parent section.
    If a sentence maps to a different domain (e.g., "Research") than its
    parent section (e.g., "Operations"), calculates a dislocation_score.

    Higher scores indicate content that may be misplaced or "stuffed" into
    the wrong section for keyword optimization purposes.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if not req.domains or len(req.domains) < 2:
        raise HTTPException(
            status_code=400,
            detail="Must provide at least 2 domains for analysis"
        )

    if not 0.0 <= req.threshold <= 1.0:
        raise HTTPException(
            status_code=400,
            detail="Threshold must be between 0.0 and 1.0"
        )

    try:
        result = mismatch_analyzer.analyze(req.text, req.domains, req.threshold)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Structural mismatch analysis failed: {e!s}"
        ) from e


@router.post("/sentiment", response_model=GranularSentimentResponse)
@limiter.limit(settings.RATE_LIMIT)
async def analyze_sentiment(
    request: Request, req: SentimentAnalysisRequest
) -> GranularSentimentResponse:
    """
    Multi-level sentiment analysis: sentence, paragraph, and section levels.

    Returns sentiment scores simultaneously at all three levels:
    - Sentence-level: Individual sentence sentiment
    - Paragraph-level: Aggregated from sentences
    - Section-level: Aggregated from paragraphs
    - Document-level: Overall sentiment

    Each level includes positive/negative/neutral scores and a compound score (-1 to 1).
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        result = sentiment_analyzer.analyze(req.text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sentiment analysis failed: {e!s}"
        ) from e
