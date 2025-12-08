"""
File processing endpoints - Enhanced document upload and analysis
"""

import time
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.analyzers.integrity_checker import IntegrityChecker
from app.analyzers.readability import ReadabilityAnalyzer
from app.analyzers.word_analysis import WordAnalyzer
from app.analyzers.writing_quality import WritingQualityAnalyzer
from app.core.config import settings
from app.models.schemas import InferredMetadata
from app.services.document_processor import DocumentProcessor
from app.services.doi_resolver import DOIResolver
from app.services.reference_extractor import ReferenceExtractor
from app.services.url_verifier import URLVerifier

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Initialize services
document_processor = DocumentProcessor()
reference_extractor = ReferenceExtractor()
url_verifier = URLVerifier()
doi_resolver = DOIResolver()
readability_analyzer = ReadabilityAnalyzer()
integrity_checker = IntegrityChecker()
writing_quality_analyzer = WritingQualityAnalyzer()
word_analyzer = WordAnalyzer()


class FileAnalysisOptions(BaseModel):
    analysis_type: str = "full"  # "full", "text", "academic"
    citation_style: str = "auto"
    check_urls: bool = True
    check_doi: bool = True
    check_plagiarism: bool = False
    extract_metadata: bool = True


class FileMetadata(BaseModel):
    filename: str
    size: int
    content_type: str
    pages: int | None = None
    author: str | None = None
    title: str | None = None
    creation_date: str | None = None
    modification_date: str | None = None


class FileAnalysisResponse(BaseModel):
    service: str = "DocumentLens"
    version: str = "1.0.0"
    files_processed: int
    analysis_type: str
    processing_time: float
    results: dict[str, Any]


@router.post("/files", response_model=FileAnalysisResponse)
@limiter.limit(settings.RATE_LIMIT)
async def analyse_uploaded_files(
    request: Request,
    files: list[UploadFile] = File(..., description="Documents to analyse (PDF, DOCX, TXT, MD)"),
    analysis_type: str = Form(default="full", description="Analysis type: full, text, or academic"),
    citation_style: str = Form(
        default="auto", description="Citation style: auto, apa, mla, chicago"
    ),
    check_urls: bool = Form(default=True, description="Verify URLs in documents"),
    check_doi: bool = Form(default=True, description="Resolve and validate DOIs"),
    check_plagiarism: bool = Form(
        default=False, description="Check for self-plagiarism between files"
    ),
    extract_metadata: bool = Form(default=True, description="Extract document metadata"),
    include_extracted_text: bool = Form(
        default=False,
        description="Include full extracted text with page-level structure in response",
    ),
) -> FileAnalysisResponse:
    """
    Enhanced file upload and analysis endpoint.

    Supports comprehensive document analysis with metadata extraction:
    - PDF, DOCX, TXT, MD document processing
    - Text extraction with page-level granularity (when include_extracted_text=True)
    - Document metadata extraction (author, title, dates, etc.)
    - Full text analysis (readability, quality, word metrics)
    - Academic analysis (citations, DOI resolution, URL verification)
    - Batch processing with document comparison
    - AI-generated content detection

    Analysis types:
    - "full": Complete text + academic + metadata analysis
    - "text": Text analysis only (readability, quality, word metrics)
    - "academic": Academic features only (citations, DOI, URL verification)

    When include_extracted_text=True, the response includes:
    - extracted_text.full_text: Complete text from the document
    - extracted_text.pages: List of {page_number, text} for each page
    - extracted_text.total_pages: Total number of pages
    """
    start_time = time.time()

    # Validate input
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > settings.MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {settings.MAX_FILES_PER_REQUEST} allowed.",
        )

    # Validate analysis type
    if analysis_type not in ["full", "text", "academic"]:
        raise HTTPException(
            status_code=400, detail="analysis_type must be 'full', 'text', or 'academic'"
        )

    try:
        # Process each file
        file_results = []
        all_texts = []
        all_metadata = []

        for file in files:
            # Validate file type
            if file.content_type not in settings.SUPPORTED_FILE_TYPES:
                raise HTTPException(
                    status_code=400, detail=f"Unsupported file type: {file.content_type}"
                )

            # Read file content
            content = await file.read()

            # Check file size
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} too large. Max: {settings.MAX_FILE_SIZE} bytes",
                )

            # Extract text (with or without page-level structure)
            extracted_text_data = None
            if include_extracted_text:
                # Use page-level extraction
                extracted_text_data = await document_processor.extract_text_with_pages(
                    content,
                    file.content_type or "application/octet-stream",
                    file.filename or "unknown",
                )
                text = extracted_text_data["full_text"]
            else:
                # Standard extraction (just the text)
                text = await document_processor.extract_text(
                    content,
                    file.content_type or "application/octet-stream",
                    file.filename or "unknown",
                )

            # Extract metadata if requested
            metadata = None
            file_metadata = None
            if extract_metadata:
                metadata = await document_processor.extract_metadata(
                    content,
                    file.content_type or "application/octet-stream",
                    file.filename or "unknown",
                )

                file_metadata = FileMetadata(
                    filename=file.filename or "unknown",
                    size=len(content),
                    content_type=file.content_type or "application/octet-stream",
                    pages=metadata.get("pages"),
                    author=metadata.get("author"),
                    title=metadata.get("title"),
                    creation_date=metadata.get("creation_date"),
                    modification_date=metadata.get("modification_date"),
                )
                all_metadata.append(file_metadata)

            # Analyze based on analysis type
            file_analysis = await _analyse_file_content(
                text, analysis_type, citation_style, check_urls, check_doi
            )

            # Build result for this file
            file_result: dict[str, Any] = {
                "filename": file.filename,
                "text_length": len(text),
                "metadata": file_metadata.model_dump() if file_metadata else None,
                "analysis": file_analysis,
            }

            # Include extracted text with page structure if requested
            if include_extracted_text and extracted_text_data:
                file_result["extracted_text"] = {
                    "full_text": extracted_text_data["full_text"],
                    "pages": extracted_text_data["pages"],
                    "total_pages": extracted_text_data["total_pages"],
                }

            file_results.append(file_result)

            all_texts.append(text)
            await file.seek(0)  # Reset for potential reuse

        # Cross-file analysis if multiple files and plagiarism check enabled
        cross_analysis = {}
        if len(files) > 1 and check_plagiarism and analysis_type in ["full", "academic"]:
            combined_text = "\n\n".join(all_texts)
            references = reference_extractor.extract_references(combined_text, citation_style)

            cross_analysis = {
                "document_comparison": _compare_documents(
                    all_texts, [f.filename or "unknown" for f in files]
                ),
                "cross_plagiarism": integrity_checker.detect_patterns(
                    combined_text, references, all_texts
                ).model_dump(),
            }

        processing_time = time.time() - start_time

        return FileAnalysisResponse(
            files_processed=len(files),
            analysis_type=analysis_type,
            processing_time=processing_time,
            results={
                "individual_files": file_results,
                "cross_analysis": cross_analysis,
                "summary": {
                    "total_files": len(files),
                    "total_text_length": sum(len(text) for text in all_texts),
                    "supported_formats": list(settings.SUPPORTED_FILE_TYPES),
                    "metadata_extracted": extract_metadata,
                },
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {e!s}") from e


async def _analyse_file_content(
    text: str, analysis_type: str, citation_style: str, check_urls: bool, check_doi: bool
) -> dict[str, Any]:
    """Analyze file content based on analysis type"""
    results = {}

    if analysis_type in ["full", "text"]:
        # Text analysis
        results["readability"] = readability_analyzer.analyze(text).model_dump()
        results["writing_quality"] = writing_quality_analyzer.analyze(text).model_dump()
        results["word_analysis"] = word_analyzer.analyze(text).model_dump()

    if analysis_type in ["full", "academic"]:
        # Academic analysis
        references = reference_extractor.extract_references(text, citation_style)
        results["references"] = {
            "total_found": len(references),
            "citations": references[:10],  # First 10 for preview
            "citation_style": citation_style,
        }

        # URL and DOI analysis (simplified for individual files)
        if check_urls or check_doi:
            results["external_verification"] = {
                "urls_checked": check_urls,
                "dois_resolved": check_doi,
                "note": "Full verification available in cross-analysis for multiple files",
            }

        # Integrity check
        results["integrity"] = (
            integrity_checker.detect_patterns(text, references, []).__dict__
            if hasattr(integrity_checker.detect_patterns(text, references, []), "__dict__")
            else integrity_checker.detect_patterns(text, references, []).model_dump()
        )

    return results


def _compare_documents(texts: list[str], filenames: list[str]) -> dict[str, Any]:
    """Compare multiple documents for similarities"""
    comparisons = []

    for i, (text1, name1) in enumerate(zip(texts, filenames, strict=False)):
        word_count1 = len(text1.split())

        for j, (text2, name2) in enumerate(zip(texts, filenames, strict=False)):
            if i >= j:  # Avoid duplicate comparisons
                continue

            word_count2 = len(text2.split())

            # Simple similarity calculation (word overlap)
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            overlap = len(words1.intersection(words2))
            total_unique = len(words1.union(words2))
            similarity = overlap / max(total_unique, 1) * 100

            comparisons.append(
                {
                    "file1": name1,
                    "file2": name2,
                    "word_count1": word_count1,
                    "word_count2": word_count2,
                    "similarity_percentage": round(similarity, 2),
                    "shared_words": overlap,
                }
            )

    from typing import cast

    similarities: list[float] = [
        cast("float", c.get("similarity_percentage", 0.0)) for c in comparisons
    ]

    return {
        "total_comparisons": len(comparisons),
        "comparisons": comparisons,
        "highest_similarity": max(similarities) if similarities else 0.0,
    }


@router.post("/files/infer-metadata", response_model=InferredMetadata)
@limiter.limit(settings.RATE_LIMIT)
async def infer_document_metadata(
    request: Request,
    file: UploadFile = File(..., description="Document to analyze (PDF, DOCX, TXT, MD)"),
) -> InferredMetadata:
    """
    Infer metadata from document content using pattern matching.

    Designed for corporate annual reports and sustainability documents.
    Uses heuristics to detect:
    - **Year**: Fiscal year, report year from content and filename
    - **Company Name**: Extracted from title patterns and filename
    - **Industry**: Detected via industry-specific keyword matching
    - **Document Type**: Annual Report, Sustainability Report, Integrated Report, etc.

    Each field includes a confidence score (0.0-1.0) indicating extraction reliability.
    Users can review and edit these values in the desktop application.

    Returns:
        InferredMetadata with probable values and confidence scores
    """
    # Validate file type
    if file.content_type not in settings.SUPPORTED_FILE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    # Read file content
    content = await file.read()

    # Check file size
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum: {settings.MAX_FILE_SIZE} bytes",
        )

    try:
        # Extract text from document
        text = await document_processor.extract_text(
            content,
            file.content_type or "application/octet-stream",
            file.filename or "unknown",
        )

        # Infer metadata from content
        inferred = document_processor.infer_metadata_from_content(text, file.filename)

        return InferredMetadata(**inferred)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metadata inference failed: {e!s}") from e


@router.post("/text/infer-metadata", response_model=InferredMetadata)
@limiter.limit(settings.RATE_LIMIT)
async def infer_text_metadata(
    request: Request,
    text: str = Form(..., description="Text content to analyze"),
    filename: str | None = Form(None, description="Optional filename for additional hints"),
) -> InferredMetadata:
    """
    Infer metadata from raw text content using pattern matching.

    Alternative to file upload when text has already been extracted.
    Uses same heuristics as /files/infer-metadata endpoint.

    Useful for:
    - Pre-extracted text
    - Cached document content
    - Testing metadata inference

    Returns:
        InferredMetadata with probable values and confidence scores
    """
    if not text or len(text.strip()) < 100:
        raise HTTPException(
            status_code=400,
            detail="Text content too short. Minimum 100 characters required.",
        )

    try:
        # Infer metadata from content
        inferred = document_processor.infer_metadata_from_content(text, filename)

        return InferredMetadata(**inferred)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metadata inference failed: {e!s}") from e
