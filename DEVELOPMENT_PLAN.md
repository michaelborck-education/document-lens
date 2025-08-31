# CiteSight Development Plan
## React + FastAPI Architecture Migration

### Project Overview
Converting CiteSight from a vanilla HTML/JS prototype to a modern React + FastAPI application with TypeScript, Docker support, and production-ready architecture.

### Progress Tracking
- ⬜ Not Started
- 🔄 In Progress  
- ✅ Completed
- ❌ Blocked

---

## Phase 1: Project Setup & Structure

### 1.1 Frontend Setup (React + TypeScript + Vite)
- ⬜ Initialize Vite project with React and TypeScript template
- ⬜ Configure TypeScript with strict mode settings
- ⬜ Set up ESLint and Prettier configuration
- ⬜ Install core dependencies:
  ```json
  {
    "react": "^18",
    "typescript": "^5",
    "axios": "^1.6",
    "zustand": "^4.4",
    "react-router-dom": "^6",
    "react-dropzone": "^14",
    "recharts": "^2.10",
    "react-wordcloud": "^1.2",
    "react-tabs": "^6"
  }
  ```
- ⬜ Set up CSS modules configuration
- ⬜ Configure path aliases in tsconfig.json

### 1.2 Backend Setup (FastAPI + Python)
- ⬜ Create backend directory structure
- ⬜ Set up Python virtual environment (3.11+)
- ⬜ Create requirements.txt with core dependencies:
  ```txt
  fastapi==0.109.0
  uvicorn==0.27.0
  python-multipart==0.0.6
  slowapi==0.1.9
  pydantic==2.5.0
  PyPDF2==3.0.1
  pdfplumber==0.10.3
  python-docx==1.1.0
  python-pptx==0.6.23
  textstat==0.7.3
  nltk==3.8.1
  scikit-learn==1.4.0
  requests==2.31.0
  httpx==0.26.0
  python-jose[cryptography]==3.3.0
  passlib[bcrypt]==1.7.4
  ```
- ⬜ Configure CORS middleware
- ⬜ Set up logging configuration
- ⬜ Create .env file for environment variables

---

## Phase 2: Core Backend Implementation

### 2.1 Document Processing Services
- ⬜ Create `services/document_processor.py`:
  - ⬜ PDF text extraction (PyPDF2/pdfplumber)
  - ⬜ DOCX text extraction (python-docx)
  - ⬜ PPTX text extraction (python-pptx)
  - ⬜ TXT/MD direct reading
  - ⬜ JSON parsing and extraction
  - ⬜ Memory-only processing (no file system writes)
  - ⬜ File validation and sanitization

### 2.2 Reference & Citation Services
- ⬜ Create `services/reference_extractor.py`:
  - ⬜ APA citation pattern regex
  - ⬜ MLA citation pattern regex
  - ⬜ Chicago style pattern regex
  - ⬜ Auto-detection of citation style
  - ⬜ In-text citation extraction
  - ⬜ Bibliography parsing

- ⬜ Create `services/url_verifier.py`:
  - ⬜ Async HTTP URL checking
  - ⬜ Retry logic with exponential backoff
  - ⬜ Timeout handling
  - ⬜ Status code validation

- ⬜ Create `services/doi_resolver.py`:
  - ⬜ CrossRef API integration
  - ⬜ DOI validation regex
  - ⬜ Metadata extraction
  - ⬜ Error handling for unresolved DOIs

- ⬜ Create `services/wayback_checker.py`:
  - ⬜ Wayback Machine API integration
  - ⬜ Snapshot retrieval for broken URLs
  - ⬜ Date-based snapshot selection

### 2.3 Analysis Services
- ⬜ Create `analyzers/readability.py`:
  - ⬜ Flesch Reading Ease calculation
  - ⬜ Flesch-Kincaid Grade Level
  - ⬜ SMOG index
  - ⬜ Gunning Fog index
  - ⬜ Word/sentence/paragraph counting

- ⬜ Create `analyzers/suspicious_patterns.py`:
  - ⬜ Self-plagiarism detection (fingerprinting)
  - ⬜ Future date detection in citations
  - ⬜ Citation stuffing detection
  - ⬜ Bibliography padding detection
  - ⬜ Style inconsistency detection
  - ⬜ Writing complexity changes

- ⬜ Create `analyzers/writing_quality.py`:
  - ⬜ Passive voice detection
  - ⬜ Sentence variety calculation
  - ⬜ Transition word counting
  - ⬜ Hedging language detection
  - ⬜ Academic tone scoring

- ⬜ Create `analyzers/word_analysis.py`:
  - ⬜ Word frequency analysis
  - ⬜ Unique word extraction
  - ⬜ N-gram generation (2-gram, 3-gram)
  - ⬜ TF-IDF calculation
  - ⬜ Keyword extraction

### 2.4 API Routes
- ⬜ Create `api/routes/analysis.py`:
  - ⬜ POST /api/analyze endpoint
  - ⬜ File upload handling
  - ⬜ Options parameter processing
  - ⬜ Progress tracking with WebSocket
  - ⬜ Result aggregation

- ⬜ Create `api/routes/health.py`:
  - ⬜ GET /api/health endpoint
  - ⬜ System status checks
  - ⬜ Version information

---

## Phase 3: Frontend Development

### 3.1 Core Components
- ⬜ Create `App.tsx`:
  - ⬜ Main layout structure
  - ⬜ Router configuration
  - ⬜ Global error boundary

- ⬜ Create `components/FileUpload.tsx`:
  - ⬜ Drag-and-drop zone (react-dropzone)
  - ⬜ File type validation
  - ⬜ Multiple file support
  - ⬜ File preview list
  - ⬜ Remove file functionality

- ⬜ Create `components/ProcessingOptions.tsx`:
  - ⬜ Citation style selector
  - ⬜ URL verification toggle
  - ⬜ DOI resolution toggle
  - ⬜ Wayback Machine toggle
  - ⬜ Plagiarism check toggle
  - ⬜ Processing mode selector (server/local)

- ⬜ Create `components/ProcessingProgress.tsx`:
  - ⬜ Progress bar component
  - ⬜ Status message display
  - ⬜ Cancel button
  - ⬜ Time estimation

### 3.2 Result Display Components
- ⬜ Create `components/ResultsTabs.tsx`:
  - ⬜ Tab navigation
  - ⬜ Active tab state
  - ⬜ Tab content rendering

- ⬜ Create `components/ReferenceResults.tsx`:
  - ⬜ Statistics display (total, broken, unresolved)
  - ⬜ Issues list with severity
  - ⬜ Export functionality
  - ⬜ Filter and search

- ⬜ Create `components/SuspiciousPatterns.tsx`:
  - ⬜ Pattern categorization
  - ⬜ Severity indicators
  - ⬜ Expandable details
  - ⬜ Visual highlighting

- ⬜ Create `components/DocumentAnalysis.tsx`:
  - ⬜ Readability metrics cards
  - ⬜ Score visualizations
  - ⬜ Interpretation guides
  - ⬜ Comparison charts

- ⬜ Create `components/WritingQuality.tsx`:
  - ⬜ Quality metrics display
  - ⬜ Improvement suggestions
  - ⬜ Progress indicators
  - ⬜ Detailed breakdowns

- ⬜ Create `components/WordCloud.tsx`:
  - ⬜ Interactive word cloud (react-wordcloud)
  - ⬜ Size-based on frequency
  - ⬜ Click interactions
  - ⬜ Color coding

- ⬜ Create `components/UniquePhrases.tsx`:
  - ⬜ N-gram display
  - ⬜ Frequency counts
  - ⬜ Filtering options
  - ⬜ Export capability

- ⬜ Create `components/DocumentComparison.tsx`:
  - ⬜ Side-by-side metrics
  - ⬜ Similarity scoring
  - ⬜ Diff highlighting
  - ⬜ Comparison charts

### 3.3 State Management & Services
- ⬜ Create `store/index.ts` (Zustand):
  - ⬜ File upload state
  - ⬜ Processing options state
  - ⬜ Analysis results state
  - ⬜ UI state (tabs, modals)
  - ⬜ Error state

- ⬜ Create `services/api.ts`:
  - ⬜ Axios instance configuration
  - ⬜ Request interceptors
  - ⬜ Response interceptors
  - ⬜ Error handling
  - ⬜ Retry logic

- ⬜ Create `hooks/useFileProcessor.ts`:
  - ⬜ File upload logic
  - ⬜ Progress tracking
  - ⬜ Error handling
  - ⬜ Result processing

- ⬜ Create `hooks/useAnalysis.ts`:
  - ⬜ Analysis triggering
  - ⬜ Result fetching
  - ⬜ State updates
  - ⬜ Cache management

### 3.4 Types & Utilities
- ⬜ Create `types/index.ts`:
  - ⬜ AnalysisResults interface
  - ⬜ ProcessingOptions interface
  - ⬜ FileUpload interface
  - ⬜ Pattern interfaces
  - ⬜ Issue interfaces

- ⬜ Create `utils/formatters.ts`:
  - ⬜ Number formatting
  - ⬜ Date formatting
  - ⬜ File size formatting
  - ⬜ Percentage formatting

- ⬜ Create `utils/validators.ts`:
  - ⬜ File type validation
  - ⬜ File size validation
  - ⬜ Option validation

---

## Phase 4: Advanced Features & Security

### 4.1 Security Implementation
- ⬜ Rate limiting setup:
  - ⬜ Configure slowapi
  - ⬜ Set limits per endpoint
  - ⬜ IP-based tracking
  - ⬜ Custom error messages

- ⬜ Input sanitization:
  - ⬜ File content sanitization
  - ⬜ Parameter validation
  - ⬜ XSS prevention
  - ⬜ SQL injection prevention (if DB added)

- ⬜ File security:
  - ⬜ Size limits (10MB default)
  - ⬜ Type validation
  - ⬜ Virus scanning (optional)
  - ⬜ Memory limits

### 4.2 Performance Optimization
- ⬜ Backend optimizations:
  - ⬜ Async processing
  - ⬜ Stream processing for large files
  - ⬜ Caching layer
  - ⬜ Database indexing (if added)

- ⬜ Frontend optimizations:
  - ⬜ Code splitting
  - ⬜ Lazy loading
  - ⬜ Memoization
  - ⬜ Virtual scrolling for long lists

### 4.3 Testing
- ⬜ Backend tests:
  - ⬜ Unit tests for services
  - ⬜ Integration tests for API
  - ⬜ Performance tests
  - ⬜ Security tests

- ⬜ Frontend tests:
  - ⬜ Component tests (React Testing Library)
  - ⬜ Hook tests
  - ⬜ E2E tests (Playwright/Cypress)
  - ⬜ Accessibility tests

---

## Phase 5: Docker & Deployment

### 5.1 Docker Configuration
- ⬜ Create `frontend/Dockerfile`:
  - ⬜ Multi-stage build
  - ⬜ Node optimization
  - ⬜ Nginx configuration
  - ⬜ Environment variables

- ⬜ Create `backend/Dockerfile`:
  - ⬜ Python slim image
  - ⬜ Dependency installation
  - ⬜ Gunicorn configuration
  - ⬜ Health check

- ⬜ Create `docker-compose.yml`:
  - ⬜ Service definitions
  - ⬜ Network configuration
  - ⬜ Volume mounts
  - ⬜ Environment variables

- ⬜ Create `nginx.conf`:
  - ⬜ Reverse proxy setup
  - ⬜ SSL configuration
  - ⬜ Rate limiting
  - ⬜ Caching headers

### 5.2 CI/CD Pipeline
- ⬜ GitHub Actions workflow:
  - ⬜ Linting checks
  - ⬜ Test execution
  - ⬜ Build verification
  - ⬜ Docker image creation
  - ⬜ Deployment trigger

### 5.3 Production Configuration
- ⬜ Environment configurations:
  - ⬜ Development settings
  - ⬜ Staging settings
  - ⬜ Production settings
  - ⬜ Secret management

- ⬜ Monitoring setup:
  - ⬜ Error tracking (Sentry)
  - ⬜ Performance monitoring
  - ⬜ Logging aggregation
  - ⬜ Health checks

---

## Implementation Notes

### Priority Order
1. Basic backend structure and document processing
2. Frontend setup with file upload
3. Core analysis features
4. UI polish and visualizations
5. Docker and deployment

### Key Decisions Made
- **Vite over Create React App**: Better performance and faster HMR
- **Zustand over Redux**: Simpler for this application scale
- **Memory-only processing**: Privacy-first approach
- **TypeScript strict mode**: Better type safety
- **Docker from start**: Easier deployment

### Risk Mitigation
- File size limits to prevent DoS
- Rate limiting on all endpoints
- Input sanitization throughout
- No data persistence (privacy)
- Comprehensive error handling

### Performance Targets
- < 2s for document upload and initial processing
- < 10s for full analysis of 50-page document
- < 100ms UI response time
- < 500ms API response time for simple queries

---

## Session Recovery Instructions

If the session crashes, to resume:
1. Check the last completed item in this file
2. Review any partially created files
3. Continue from the next unchecked item
4. Update this file as tasks are completed

## Current Status
- **Date Started**: 2024-08-30
- **Last Updated**: 2024-08-30  
- **Current Phase**: Phase 2 - Core Implementation in Progress
- **Completed**: 
  - ✅ React frontend initialized with Vite + TypeScript
  - ✅ FastAPI backend structure created
  - ✅ Core type definitions and schemas
  - ✅ Document processing service
  - ✅ Basic API routes and health endpoints
  - ✅ Reference extraction service
  - ✅ Readability analyzer
- **Next Steps**: Implement React components and complete analysis services

## Notes
- All features from the HTML prototype are preserved
- Additional features added for production readiness
- Privacy-first design with no data persistence
- Scalable architecture for future enhancements