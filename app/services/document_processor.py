"""
Document processing service for text extraction from various file formats
"""

import io
import json
from typing import Any

from fastapi import HTTPException

# Import libraries for different file types
try:
    import PyPDF2
    from PyPDF2 import PdfReader
except ImportError:
    PyPDF2 = None  # type: ignore[assignment]
    PdfReader = None  # type: ignore[misc,assignment]

try:
    from pdfplumber.pdf import PDF as PDFPlumberPDF  # noqa: N811
except ImportError:
    PDFPlumberPDF = None  # type: ignore[assignment, misc]

try:
    from docx import Document
except ImportError:
    Document = None

try:
    from pptx import Presentation
except ImportError:
    Presentation = None

class DocumentProcessor:
    """Handles text extraction from various document formats"""

    def __init__(self) -> None:
        self.pdf_available = PdfReader is not None
        self.docx_available = Document is not None
        self.pptx_available = Presentation is not None

    async def extract_text(self, content: bytes, content_type: str, filename: str) -> str:
        """
        Extract text from document based on content type

        Args:
            content: Raw file content as bytes
            content_type: MIME type of the file
            filename: Name of the file (for error reporting)

        Returns:
            Extracted text as string
        """
        try:
            if content_type == "application/pdf":
                return await self._extract_from_pdf(content, filename)
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return await self._extract_from_docx(content, filename)
            elif content_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                raise ValueError(
                    "PPTX files are no longer supported in DocumentLens. "
                    "Please use PresentationLens service for presentation analysis. "
                    "See: https://github.com/michael-borck/presentation-lens"
                )
            elif content_type in ["text/plain", "text/markdown"]:
                return await self._extract_from_text(content, filename)
            elif content_type == "application/json":
                return await self._extract_from_json(content, filename)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")

        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to extract text from {filename}: {e!s}"
            ) from e

    async def _extract_from_pdf(self, content: bytes, filename: str) -> str:
        """Extract text from PDF file"""
        if not PyPDF2:
            raise ImportError("PyPDF2 not available. Please install with: pip install PyPDF2")

        text_parts = []

        try:
            # Try with PyPDF2 first
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            for page in pdf_reader.pages:
                text = page.extract_text()
                if text.strip():
                    text_parts.append(text)

            # If PyPDF2 didn't extract much text, try pdfplumber
            if len("".join(text_parts)) < 100 and PDFPlumberPDF is not None:
                pdf_file.seek(0)
                with PDFPlumberPDF(pdf_file) as pdf:
                    text_parts = []
                    for page in pdf.pages:  # type: ignore[assignment]
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)

        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {e!s}") from e

        if not text_parts:
            raise ValueError("No text could be extracted from PDF")

        return "\n\n".join(text_parts)

    async def _extract_from_docx(self, content: bytes, filename: str) -> str:
        """Extract text from DOCX file"""
        if not Document:
            raise ImportError("python-docx not available. Please install with: pip install python-docx")

        try:
            doc_file = io.BytesIO(content)
            doc = Document(doc_file)

            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)

            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text_parts.append(cell.text)

        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {e!s}") from e

        if not text_parts:
            raise ValueError("No text could be extracted from DOCX")

        return "\n\n".join(text_parts)

    # PPTX processing removed - use PresentationLens service instead
    # See: https://github.com/michael-borck/presentation-lens

    async def _extract_from_text(self, content: bytes, filename: str) -> str:
        """Extract text from plain text or markdown file"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']

            for encoding in encodings:
                try:
                    text = content.decode(encoding)
                    return text
                except UnicodeDecodeError:
                    continue

            # If all encodings fail, use utf-8 with error handling
            return content.decode('utf-8', errors='replace')

        except Exception as e:
            raise ValueError(f"Failed to decode text file: {e!s}") from e

    async def _extract_from_json(self, content: bytes, filename: str) -> str:
        """Extract text from JSON file"""
        try:
            text = content.decode('utf-8')
            data = json.loads(text)

            # Extract text recursively from JSON structure
            extracted_texts: list[str] = []
            self._extract_text_from_json_recursive(data, extracted_texts)

            if not extracted_texts:
                raise ValueError("No text content found in JSON")

            return "\n\n".join(extracted_texts)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e!s}") from e
        except Exception as e:
            raise ValueError(f"Failed to process JSON: {e!s}") from e

    def _extract_text_from_json_recursive(self, obj: dict | list, texts: list[str]) -> None:
        """Recursively extract text from JSON object"""
        if isinstance(obj, dict):
            for _key, value in obj.items():
                if isinstance(value, str) and len(value.strip()) > 10:
                    texts.append(value.strip())
                elif isinstance(value, dict | list):
                    self._extract_text_from_json_recursive(value, texts)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, str) and len(item.strip()) > 10:
                    texts.append(item.strip())
                elif isinstance(item, dict | list):
                    self._extract_text_from_json_recursive(item, texts)

    def validate_file_size(self, content: bytes, max_size: int) -> bool:
        """Validate file size"""
        return len(content) <= max_size

    async def extract_metadata(self, content: bytes, content_type: str, filename: str) -> dict[str, Any]:
        """
        Extract metadata from document

        Args:
            content: Raw file content
            content_type: MIME type of the file
            filename: Name of the file

        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {
            "filename": filename,
            "size": len(content),
            "content_type": content_type
        }

        try:
            if content_type == "application/pdf":
                metadata.update(self._extract_pdf_metadata(content))
            elif content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                metadata.update(self._extract_docx_metadata(content))
            elif content_type in ["application/vnd.openxmlformats-officedocument.presentationml.presentation", "application/vnd.ms-powerpoint"]:
                metadata.update(self._extract_pptx_metadata(content))
            else:
                # For text files, just basic info
                if content_type.startswith("text/"):
                    try:
                        text = content.decode('utf-8')
                        metadata["lines"] = len(text.splitlines())
                        metadata["characters"] = len(text)
                    except UnicodeDecodeError:
                        metadata["encoding_error"] = True

        except Exception as e:
            metadata["extraction_error"] = str(e)

        return metadata

    def _extract_pdf_metadata(self, content: bytes) -> dict[str, Any]:
        """Extract metadata from PDF"""
        metadata = {}

        if self.pdf_available:
            try:
                pdf_file = io.BytesIO(content)
                reader = PdfReader(pdf_file)

                metadata["pages"] = len(reader.pages)

                if reader.metadata:
                    doc_info = reader.metadata
                    metadata["title"] = str(doc_info.get("/Title", "")).strip()
                    metadata["author"] = str(doc_info.get("/Author", "")).strip()
                    metadata["subject"] = str(doc_info.get("/Subject", "")).strip()
                    metadata["creator"] = str(doc_info.get("/Creator", "")).strip()
                    metadata["producer"] = str(doc_info.get("/Producer", "")).strip()

                    # Handle dates
                    creation_date = doc_info.get("/CreationDate")
                    if creation_date:
                        metadata["creation_date"] = str(creation_date)

                    mod_date = doc_info.get("/ModDate")
                    if mod_date:
                        metadata["modification_date"] = str(mod_date)

            except Exception as e:
                metadata["pdf_metadata_error"] = str(e)

        return metadata

    def _extract_docx_metadata(self, content: bytes) -> dict[str, Any]:
        """Extract metadata from DOCX"""
        metadata = {}

        if self.docx_available:
            try:
                docx_file = io.BytesIO(content)
                doc = Document(docx_file)

                # Count elements
                metadata["paragraphs"] = len(doc.paragraphs)
                metadata["tables"] = len(doc.tables)

                # Core properties
                if hasattr(doc, 'core_properties'):
                    props = doc.core_properties
                    metadata["title"] = str(props.title or "")
                    metadata["author"] = str(props.author or "")
                    metadata["subject"] = str(props.subject or "")
                    metadata["keywords"] = str(props.keywords or "")
                    metadata["comments"] = str(props.comments or "")

                    if props.created:
                        metadata["creation_date"] = props.created.isoformat()
                    if props.modified:
                        metadata["modification_date"] = props.modified.isoformat()

            except Exception as e:
                metadata["docx_metadata_error"] = str(e)

        return metadata

    def _extract_pptx_metadata(self, content: bytes) -> dict[str, Any]:
        """Extract metadata from PPTX"""
        metadata = {}

        if self.pptx_available:
            try:
                pptx_file = io.BytesIO(content)
                prs = Presentation(pptx_file)

                metadata["slides"] = int(len(prs.slides))

                # Core properties
                if hasattr(prs, 'core_properties'):
                    props = prs.core_properties
                    metadata["title"] = str(props.title or "")
                    metadata["author"] = str(props.author or "")
                    metadata["subject"] = str(props.subject or "")
                    metadata["keywords"] = str(props.keywords or "")
                    metadata["comments"] = str(props.comments or "")

                    if props.created:
                        metadata["creation_date"] = props.created.isoformat()
                    if props.modified:
                        metadata["modification_date"] = props.modified.isoformat()

            except Exception as e:
                metadata["pptx_metadata_error"] = str(e)

        return metadata
