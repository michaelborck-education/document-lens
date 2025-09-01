"""
Text analysis endpoints - Core text metrics without academic features
"""

import time

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.analyzers.readability import ReadabilityAnalyzer
from app.analyzers.word_analysis import WordAnalyzer
from app.analyzers.writing_quality import WritingQualityAnalyzer
from app.core.config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Initialize text analyzers only
readability_analyzer = ReadabilityAnalyzer()
writing_quality_analyzer = WritingQualityAnalyzer()
word_analyzer = WordAnalyzer()

class TextAnalysisRequest(BaseModel):
    text: str
    options: dict = {}

class TextAnalysisResponse(BaseModel):
    service: str = "DocumentLens"
    version: str = "1.0.0"
    content_type: str = "text"
    analysis: dict
    processing_time: float

@router.post("/text", response_model=TextAnalysisResponse)
@limiter.limit(settings.RATE_LIMIT)
async def analyze_text_only(
    request: Request,
    analysis_request: TextAnalysisRequest
) -> TextAnalysisResponse:
    """
    Core text analysis - readability, quality, and word metrics only.

    This endpoint provides essential text analysis without academic features:
    - Readability scores (Flesch, Flesch-Kincaid)
    - Writing quality metrics (passive voice, sentence variety)
    - Word analysis (frequency, n-grams, vocabulary richness)

    Perfect for blogs, articles, general writing assessment.
    """
    start_time = time.time()

    if not analysis_request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )

    try:
        text = analysis_request.text

        # Core text analysis
        document_analysis = readability_analyzer.analyze(text)
        writing_quality = writing_quality_analyzer.analyze(text)
        word_analysis = word_analyzer.analyze(text)

        processing_time = time.time() - start_time

        return TextAnalysisResponse(
            analysis={
                "text_metrics": {
                    "word_count": document_analysis.word_count,
                    "sentence_count": document_analysis.sentence_count,
                    "paragraph_count": document_analysis.paragraph_count,
                    "avg_words_per_sentence": document_analysis.avg_words_per_sentence
                },
                "readability": {
                    "flesch_score": document_analysis.flesch_score,
                    "flesch_kincaid_grade": document_analysis.flesch_kincaid_grade,
                    "interpretation": _interpret_readability(document_analysis.flesch_score)
                },
                "writing_quality": {
                    "passive_voice_percentage": writing_quality.passive_voice_percentage,
                    "sentence_variety": writing_quality.sentence_variety,
                    "academic_tone": writing_quality.academic_tone,
                    "transition_words": writing_quality.transition_words,
                    "hedging_language": writing_quality.hedging_language
                },
                "word_analysis": {
                    "unique_words": word_analysis.unique_words if hasattr(word_analysis, 'unique_words') else 0,
                    "vocabulary_richness": word_analysis.vocabulary_richness if hasattr(word_analysis, 'vocabulary_richness') else 0.0,
                    "top_words": word_analysis.top_words if hasattr(word_analysis, 'top_words') else [],
                    "bigrams": word_analysis.bigrams if hasattr(word_analysis, 'bigrams') else [],
                    "trigrams": word_analysis.trigrams if hasattr(word_analysis, 'trigrams') else []
                }
            },
            processing_time=processing_time
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Text analysis failed: {e!s}"
        ) from e

def _interpret_readability(flesch_score: float) -> str:
    """Interpret Flesch Reading Ease score"""
    if flesch_score >= 90:
        return "Very Easy (5th grade level)"
    elif flesch_score >= 80:
        return "Easy (6th grade level)"
    elif flesch_score >= 70:
        return "Fairly Easy (7th grade level)"
    elif flesch_score >= 60:
        return "Standard (8th-9th grade level)"
    elif flesch_score >= 50:
        return "Fairly Difficult (10th-12th grade level)"
    elif flesch_score >= 30:
        return "Difficult (College level)"
    else:
        return "Very Difficult (Graduate level)"
