# PresentationLens: Presentation Analysis Microservice

## Service Overview

**PresentationLens** is a specialized microservice focused on analyzing presentation effectiveness, design quality, and content structure. It extracts text content for DocumentLens analysis while providing presentation-specific insights that pure text analysis cannot capture.

## Core Purpose

Transform presentation files (PPTX, PDF slides, etc.) into actionable insights about:
- **Design Quality**: Visual balance, consistency, professional appearance
- **Content Structure**: Information hierarchy, slide flow, message clarity
- **Presentation Effectiveness**: Adherence to proven presentation principles
- **Accessibility**: Readability, contrast, alternative text coverage

## Key Features

### 1. Design Rule Analysis

#### 5x5 Rule Compliance
- Maximum 5 bullet points per slide
- Maximum 5 words per bullet point
- Slide-by-slide compliance scoring
- Suggestions for content reduction

#### 10-20-30 Rule (Guy Kawasaki)
- Maximum 10 slides for pitch presentations
- Minimum 20-point font size
- Maximum 30-minute presentation time (estimated)
- Rule applicability detection and scoring

#### Visual Balance Assessment
- Text-to-whitespace ratio analysis
- Image placement and sizing optimization
- Color scheme consistency evaluation
- Font variety and hierarchy analysis

### 2. Content Structure Analysis

#### Slide Flow & Narrative
- Logical progression detection
- Story arc analysis (problem → solution → results)
- Transition effectiveness between slides
- Call-to-action identification and placement

#### Information Hierarchy
- Title and subtitle structure consistency
- Bullet point depth and organization
- Visual emphasis patterns (bold, italic, size)
- Information density per slide

#### Speaker Notes Integration
- Notes-to-slide content ratio
- Redundancy vs complementary content analysis
- Speaker preparation indicators
- Presentation mode optimization suggestions

### 3. Presentation-Specific Metrics

#### Engagement Factors
- Slide variety (text, images, charts, videos)
- Interactive element detection
- Animation and transition usage analysis
- Audience participation opportunities

#### Professional Quality
- Corporate template compliance
- Brand consistency (colors, fonts, logos)
- Image quality and resolution analysis
- Chart and diagram effectiveness

#### Accessibility Compliance
- Alt text coverage for images
- Color contrast ratios (WCAG compliance)
- Font readability (size, contrast)
- Screen reader compatibility

## API Design

### Core Endpoints

```python
# Analyze presentation file
POST /api/analyze/presentation
Content-Type: multipart/form-data
Body: presentation_file, options

Response:
{
    "presentation_analysis": {
        "design_scores": {
            "five_x_five_compliance": 85.2,
            "ten_twenty_thirty_score": 92.0,
            "visual_balance_score": 78.5,
            "consistency_score": 88.3
        },
        "content_structure": {
            "slide_flow_score": 91.2,
            "information_hierarchy": 82.7,
            "narrative_strength": 75.4
        },
        "accessibility": {
            "alt_text_coverage": 45.2,
            "color_contrast_score": 88.9,
            "readability_score": 92.1
        },
        "slide_details": [
            {
                "slide_number": 1,
                "type": "title_slide",
                "issues": ["Font size below 20pt", "No alt text for logo"],
                "suggestions": ["Increase title font to 24pt", "Add logo description"]
            }
        ]
    },
    "extracted_text": "Full text content for DocumentLens analysis",
    "metadata": {
        "total_slides": 15,
        "estimated_duration": "18 minutes",
        "presentation_type": "business_pitch",
        "template_detected": "corporate_blue"
    }
}
```

### Integration Endpoints

```python
# Extract text only (for DocumentLens integration)
POST /api/extract/text
Content-Type: multipart/form-data
Body: presentation_file

Response:
{
    "text_content": "Extracted text...",
    "slide_structure": [
        {"slide": 1, "title": "Introduction", "content": "..."},
        {"slide": 2, "title": "Problem Statement", "content": "..."}
    ]
}

# Quick design assessment
POST /api/assess/design
Content-Type: multipart/form-data
Body: presentation_file

Response:
{
    "overall_score": 82.4,
    "quick_wins": [
        "Reduce bullet points on slide 3",
        "Increase font size on slides 7-9",
        "Add alt text to 8 images"
    ],
    "major_issues": [
        "Slides 12-15 violate 5x5 rule",
        "Color contrast issues on slide 6"
    ]
}
```

### Batch Processing

```python
# Analyze multiple presentations
POST /api/batch/analyze
Content-Type: application/json
Body: {
    "presentations": [
        {"url": "s3://bucket/pres1.pptx", "id": "quarterly_review"},
        {"url": "s3://bucket/pres2.pptx", "id": "product_launch"}
    ],
    "comparison_mode": true
}

Response:
{
    "batch_id": "batch_12345",
    "status": "processing",
    "results_webhook": "https://callback.example.com/results"
}
```

## Technology Stack

### Core Technologies
- **FastAPI**: Web framework for REST API
- **python-pptx**: PPTX file processing and manipulation
- **Pillow (PIL)**: Image processing and analysis
- **OpenCV**: Advanced image analysis and computer vision
- **scikit-image**: Image analysis algorithms
- **python-docx**: DOCX processing for exported presentations

### Analysis Libraries
- **colorthief**: Color palette extraction
- **webcolors**: Color contrast calculations
- **matplotlib**: Chart and visualization analysis
- **pandas**: Data analysis for batch processing
- **numpy**: Numerical computations

### Optional Enhancements
- **tensorflow/pytorch**: ML-based design quality scoring
- **tesseract (pytesseract)**: OCR for image text extraction
- **face_recognition**: Speaker image analysis
- **spacy**: Advanced text analysis integration

## Project Structure

```
presentation-lens/
├── app/
│   ├── analyzers/
│   │   ├── design_analyzer.py          # 5x5, 10-20-30, visual balance
│   │   ├── content_analyzer.py         # Structure, flow, hierarchy  
│   │   ├── accessibility_analyzer.py   # WCAG compliance, alt text
│   │   └── template_analyzer.py        # Brand consistency, templates
│   ├── extractors/
│   │   ├── pptx_extractor.py          # PPTX text and metadata extraction
│   │   ├── pdf_extractor.py           # PDF slide processing
│   │   └── image_extractor.py         # Image analysis and OCR
│   ├── api/
│   │   ├── routes/
│   │   │   ├── analysis.py            # Main analysis endpoints
│   │   │   ├── extraction.py          # Text extraction endpoints  
│   │   │   └── batch.py               # Batch processing
│   │   └── models/
│   │       ├── requests.py            # Request schemas
│   │       └── responses.py           # Response schemas
│   ├── services/
│   │   ├── presentation_processor.py  # Core presentation processing
│   │   ├── design_scorer.py          # Design rule scoring
│   │   └── document_lens_client.py   # DocumentLens integration
│   └── utils/
│       ├── image_utils.py            # Image processing utilities
│       ├── color_utils.py            # Color analysis utilities
│       └── text_utils.py             # Text processing helpers
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│       └── sample_presentations/
├── docs/
│   ├── api/
│   └── examples/
└── requirements.txt
```

## Integration with DocumentLens

### Workflow Pattern
1. **PresentationLens** receives PPTX file
2. Extracts text content and slide structure
3. Performs presentation-specific analysis
4. Calls **DocumentLens** `/api/analyze/text` with extracted text
5. Combines presentation metrics with text analysis
6. Returns comprehensive presentation report

### Text Extraction Enhancement
```python
# Enhanced text extraction with context
{
    "text_content": "Full extracted text...",
    "structured_content": {
        "slide_1": {
            "title": "Introduction",
            "bullets": ["Point 1", "Point 2"],
            "speaker_notes": "Remember to emphasize...",
            "images": [{"alt_text": "Company logo", "has_text": false}]
        }
    }
}
```

### Combined Analysis Result
```python
{
    "presentation_analysis": {
        "design_scores": {...},
        "content_structure": {...}
    },
    "text_analysis": {
        "readability": {...},
        "writing_quality": {...},
        "word_analysis": {...}
    },
    "combined_insights": {
        "overall_effectiveness": 84.2,
        "key_strengths": [
            "Excellent readability (Flesch: 85)",
            "Strong visual design (Design: 88)",
            "Good narrative flow"
        ],
        "improvement_areas": [
            "Reduce jargon in slides 5-7",
            "Increase font size on slide 12",
            "Add missing alt text"
        ]
    }
}
```

## Deployment Considerations

### Infrastructure Requirements
- **CPU**: Medium (image processing, text analysis)
- **Memory**: 2-4GB (presentations can be large)
- **Storage**: Temporary file processing space
- **Network**: Fast DocumentLens communication

### Scalability
- Horizontal scaling for batch processing
- File processing can be CPU intensive
- Consider async task queue (Celery/RQ) for large files

### Security
- Secure file upload handling
- Temporary file cleanup
- Content scanning for malicious files
- Rate limiting for API endpoints

## Success Metrics

### Technical Metrics
- Processing time < 30 seconds for typical presentations
- Accuracy of design rule detection > 90%
- API response time < 2 seconds for quick assessments
- DocumentLens integration latency < 5 seconds

### User Value Metrics
- Improvement in presentation effectiveness scores
- Reduction in common design mistakes
- Increased accessibility compliance
- User satisfaction with suggestions

## Development Phases

### Phase 1: Core PPTX Processing
- Basic text extraction from PPTX files
- Simple design rule checking (5x5, font sizes)
- DocumentLens integration for text analysis
- Basic API endpoints

### Phase 2: Advanced Design Analysis
- Visual balance and consistency scoring
- Template and brand compliance detection
- Image analysis and alt text checking
- Color contrast and accessibility

### Phase 3: Content Intelligence
- Slide flow and narrative analysis
- Speaker notes integration
- Presentation type detection
- Advanced suggestion engine

### Phase 4: Batch & Enterprise Features
- Batch processing capabilities
- Template library and comparison
- Team collaboration features
- Analytics and reporting dashboards

## Migration from DocumentLens

### Current PPTX Code Location
The existing PPTX processing logic is in:
- `app/services/document_processor.py` (lines 130-160)
- Basic text extraction only
- No presentation-specific analysis

### Migration Steps
1. **Extract Current Logic**: Copy PPTX extraction code as base
2. **Enhance Processing**: Add presentation-specific analyzers
3. **Create New Service**: Set up FastAPI service structure
4. **Update DocumentLens**: Remove PPTX handling, add integration
5. **Test Integration**: Ensure seamless text analysis pipeline

### Backward Compatibility
During migration, DocumentLens can:
- Redirect PPTX requests to PresentationLens
- Proxy responses to maintain API compatibility
- Gradually migrate clients to new endpoints

---

**PresentationLens** will transform how users create and analyze presentations, providing actionable insights that go far beyond simple text analysis while seamlessly integrating with the DocumentLens ecosystem for comprehensive content intelligence.