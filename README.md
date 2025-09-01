# DocumentLens

**Text Analysis & Academic Intelligence Microservice**

Transform text content into actionable insights through comprehensive linguistic analysis, writing quality assessment, and academic integrity checking.

## 🚀 Quick Start

```bash
# Raw deployment
./deploy.sh

# Or Docker deployment
docker-compose up -d

# API available at: http://localhost:8000
# Documentation: http://localhost:8000/docs (if DEBUG=true)
```

## 📊 API Endpoints

### Core Analysis (Clean Australian URLs)
- `GET /health` - Service health check
- `POST /text` - Text analysis (readability, quality, word frequency)
- `POST /academic` - Academic analysis (citations, DOI resolution, integrity)
- `POST /files` - File upload + analysis (PDF, DOCX, TXT, MD)

### Integration
- Root endpoint: `GET /` - Service info and available endpoints
- For presentations: Use [PresentationLens](https://github.com/michael-borck/presentation-lens)
- For recordings: Use [RecordingLens](https://github.com/michael-borck/recording-lens)

## 🎯 Use Cases

- **Text Analysis**: Readability, writing quality, word frequency for any text content
- **Academic Analysis**: Citation verification, DOI resolution, AI detection, integrity checking
- **Document Intelligence**: Extract and analyze text from PDFs and Word documents
- **Multi-Service Workflows**: Integrate with specialized analysis services

## 🏗️ Microservices Ecosystem

DocumentLens is part of a focused microservices architecture:

| Service | Purpose | Repository |
|---------|---------|------------|
| **DocumentLens** | Text analysis & academic intelligence | *This repo* |
| **PresentationLens** | Presentation design & structure analysis | [presentation-lens](https://github.com/michael-borck/presentation-lens) |
| **RecordingLens** | Student recordings (video/audio) analysis | [recording-lens](https://github.com/michael-borck/recording-lens) |
| **CodeLens** | Source code quality & analysis | [code-lens](https://github.com/michael-borck/code-lens) |
| **SubmissionLens** | Student submission router & frontend | [submission-lens](https://github.com/michael-borck/submission-lens) |

### Integration Pattern
```mermaid
graph LR
    A[Student Submission] --> B[SubmissionLens Frontend]
    B --> C{File Type Router}
    C -->|Text/PDF/DOCX| D[DocumentLens]
    C -->|PPTX| E[PresentationLens]
    C -->|Video/Audio| F[RecordingLens]
    C -->|Source Code| G[CodeLens]
    E --> D
    F --> D
    G --> D
    D --> H[Combined Feedback]
    H --> B
    B --> I[Student Dashboard]
```

## 🚀 Deployment

Two deployment options available:

### Raw/Native Deployment
```bash
git clone https://github.com/michael-borck/document-lens.git
cd document-lens
./deploy.sh  # Handles venv, dependencies, and production server
```

### Docker Deployment
```bash
git clone https://github.com/michael-borck/document-lens.git
cd document-lens
docker-compose up -d  # Simple deployment
# Or: docker-compose --profile production up -d  # With Nginx
```

## 📚 Documentation

- `DEPLOYMENT.md` - Complete VPS deployment guide (raw + Docker)
- `DOCUMENTLENS_SETUP.md` - Setup and usage instructions
- `.env.example` - Configuration template

---

*DocumentLens: Pure text intelligence at the heart of content analysis*
