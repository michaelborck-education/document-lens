# CiteSight - Academic Document Analyzer

An intelligent academic document analyzer that verifies citations, detects suspicious patterns, and analyzes writing quality. Built with React, TypeScript, and FastAPI.

## 🚀 Features

### Core Functionality
- **Multi-format Support**: PDF, DOCX, PPTX, TXT, MD, JSON
- **Citation Verification**: Checks references, URLs, and DOIs
- **Pattern Detection**: Identifies self-plagiarism, citation anomalies, and style inconsistencies
- **Writing Analysis**: Readability scores, passive voice detection, academic tone assessment
- **Privacy-First**: All processing happens in memory, no data persistence

### Analysis Capabilities
- ✅ Reference extraction and verification
- ✅ Broken URL detection with Wayback Machine fallback
- ✅ DOI resolution via CrossRef API
- ✅ Citation style detection (APA, MLA, Chicago)
- ✅ Readability metrics (Flesch scores)
- ✅ Writing quality assessment
- ✅ Word frequency and unique phrase analysis
- ✅ Multi-document comparison

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast builds and HMR
- **Zustand** for state management
- **Axios** for API communication
- **Recharts** for data visualization
- **React Dropzone** for file uploads

### Backend
- **FastAPI** for high-performance API
- **Pydantic** for data validation
- **PyPDF2/pdfplumber** for PDF processing
- **python-docx/python-pptx** for Office documents
- **textstat** for readability analysis
- **NLTK** for natural language processing

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🚧 Development

### Project Structure
```
cite-sight/
├── frontend/           # React + TypeScript application
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── hooks/      # Custom React hooks
│   │   ├── services/   # API integration
│   │   ├── store/      # State management
│   │   ├── types/      # TypeScript definitions
│   │   └── utils/      # Utility functions
│   └── package.json
├── backend/            # FastAPI application
│   ├── app/
│   │   ├── api/        # API routes
│   │   ├── core/       # Configuration
│   │   ├── services/   # Business logic
│   │   ├── analyzers/  # Document analysis
│   │   ├── models/     # Data models
│   │   └── utils/      # Utilities
│   └── requirements.txt
└── DEVELOPMENT_PLAN.md # Detailed development roadmap
```

### API Documentation
When running in development mode, API documentation is available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 🔒 Security Features

- **Rate Limiting**: Configurable per-endpoint limits
- **File Size Limits**: Default 10MB max file size
- **Input Sanitization**: All inputs validated and sanitized
- **CORS Configuration**: Restricted to allowed origins
- **Memory-Only Processing**: No files saved to disk

## 🐳 Docker Support (Coming Soon)

Docker configuration is in development. Once complete, you'll be able to run:
```bash
docker-compose up
```

## 📊 API Endpoints

### Main Endpoints
- `POST /api/analyze` - Analyze documents
- `GET /api/health` - Health check

### Request Example
```javascript
const formData = new FormData();
formData.append('files', document);
formData.append('citation_style', 'auto');
formData.append('check_urls', 'true');
formData.append('check_doi', 'true');

const response = await axios.post('http://localhost:8000/api/analyze', formData);
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with modern web technologies
- Privacy-first design philosophy
- Academic integrity at its core

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Note**: This project is under active development. See `DEVELOPMENT_PLAN.md` for the current status and roadmap.