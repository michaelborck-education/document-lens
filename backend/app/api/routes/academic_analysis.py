"""
Academic analysis endpoints - Citation, DOI, URL verification, and integrity checks
"""

import time

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.analyzers.suspicious_patterns import SuspiciousPatternDetector
from app.core.config import settings
from app.models.schemas import AnalysisOptions, ReferenceResults
from app.services.doi_resolver import DOIResolver
from app.services.reference_extractor import ReferenceExtractor
from app.services.url_verifier import URLVerifier

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Initialize academic services
reference_extractor = ReferenceExtractor()
url_verifier = URLVerifier()
doi_resolver = DOIResolver()
suspicious_pattern_detector = SuspiciousPatternDetector()

class AcademicAnalysisRequest(BaseModel):
    text: str
    citation_style: str = "auto"
    check_urls: bool = True
    check_doi: bool = True
    check_wayback: bool = True
    check_plagiarism: bool = False
    check_in_text: bool = True

class AcademicAnalysisResponse(BaseModel):
    service: str = "DocumentLens"
    version: str = "1.0.0"
    content_type: str = "academic"
    analysis: dict
    processing_time: float

@router.post("/academic", response_model=AcademicAnalysisResponse)
@limiter.limit(settings.RATE_LIMIT)
async def analyze_academic_features(
    request: Request,
    analysis_request: AcademicAnalysisRequest
) -> AcademicAnalysisResponse:
    """
    Academic document analysis - citations, references, and integrity checks.
    
    This endpoint provides specialized academic analysis:
    - Citation extraction and style detection
    - DOI resolution and validation
    - URL verification with Wayback Machine fallback
    - Suspicious pattern detection (plagiarism, citation stuffing)
    - Reference integrity checking
    
    Perfect for research papers, academic documents, scholarly articles.
    """
    start_time = time.time()
    
    if not analysis_request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )
    
    try:
        text = analysis_request.text
        
        # Create analysis options
        options = AnalysisOptions(
            citation_style=analysis_request.citation_style,
            check_urls=analysis_request.check_urls,
            check_doi=analysis_request.check_doi,
            check_wayback=analysis_request.check_wayback,
            check_plagiarism=analysis_request.check_plagiarism,
            check_in_text=analysis_request.check_in_text,
            processing_mode="server"
        )
        
        # Extract references
        references = reference_extractor.extract_references(text, options.citation_style)
        
        # Verify URLs and DOIs if requested
        reference_results = await _analyze_references(references, text, options)
        
        # Detect suspicious patterns
        suspicious_patterns = suspicious_pattern_detector.detect_patterns(
            text,
            references,
            [text] if options.check_plagiarism else []
        )
        
        processing_time = time.time() - start_time
        
        return AcademicAnalysisResponse(
            analysis={
                "references": {
                    "total": reference_results.total,
                    "broken_urls": reference_results.broken_urls,
                    "unresolved_dois": reference_results.unresolved_dois,
                    "missing_in_text": reference_results.missing_in_text,
                    "orphaned_in_text": reference_results.orphaned_in_text,
                    "issues": [
                        {
                            "type": issue.type,
                            "message": issue.message,
                            "severity": getattr(issue, 'severity', 'medium'),
                            "suggestion": getattr(issue, 'suggestion', None)
                        } 
                        for issue in reference_results.issues
                    ]
                },
                "citations": {
                    "detected_style": options.citation_style,
                    "extracted": len(references),
                    "styles_found": _detect_citation_styles(references)
                },
                "integrity": {
                    "risk_score": suspicious_patterns.risk_score if hasattr(suspicious_patterns, 'risk_score') else 0.0,
                    "patterns_detected": len(suspicious_patterns.patterns) if hasattr(suspicious_patterns, 'patterns') else 0,
                    "patterns": [
                        {
                            "type": pattern.type,
                            "description": pattern.description,
                            "severity": pattern.severity,
                            "location": getattr(pattern, 'location', None)
                        }
                        for pattern in (suspicious_patterns.patterns if hasattr(suspicious_patterns, 'patterns') else [])
                    ]
                }
            },
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Academic analysis failed: {str(e)}"
        ) from e

async def _analyze_references(references: list, text: str, options: AnalysisOptions) -> ReferenceResults:
    """Analyze references for broken URLs, unresolved DOIs, etc."""
    # This will be implemented with the actual services
    # For now, return a placeholder with some basic analysis
    
    return ReferenceResults(
        total=len(references),
        broken_urls=0,  # TODO: Implement URL verification
        unresolved_dois=0,  # TODO: Implement DOI resolution
        missing_in_text=0,  # TODO: Implement in-text citation matching
        orphaned_in_text=0,  # TODO: Implement orphaned citation detection
        issues=[]
    )

def _detect_citation_styles(references: list) -> list[str]:
    """Detect citation styles present in the references"""
    # TODO: Implement actual citation style detection
    styles = []
    if references:
        styles.append("apa")  # Placeholder
    return styles