# DocumentLens

**Multi-Modal Document Analysis Microservice**

Transform any content into actionable insights through comprehensive text analysis, academic integrity checking, and future multi-modal capabilities.

## 🚀 Quick Start

```bash
# Setup
./start.sh

# API available at: http://localhost:8000
# Documentation: http://localhost:8000/api/docs
```

## 📊 API Endpoints

### Current (MVP)
- `GET /api/health` - Service health check
- `POST /api/analyze` - Full analysis (backward compatibility)
- `POST /api/analyze/text` - Core text analysis only
- `POST /api/analyze/academic` - Academic features only

### Planned
- `POST /api/analyze/files` - File upload + analysis
- `POST /api/analyze/audio` - Audio transcription + analysis  
- `POST /api/analyze/video` - Video content + analysis

## 🎯 Use Cases

- **Text Analysis**: Readability, quality, word frequency for any content
- **Academic Analysis**: Citation verification, DOI resolution, integrity checking
- **Multi-Modal**: Future audio/video analysis integration

## 📚 Documentation

See `DOCUMENTLENS_SETUP.md` for complete setup and usage instructions.

---

*DocumentLens: See through your content*
