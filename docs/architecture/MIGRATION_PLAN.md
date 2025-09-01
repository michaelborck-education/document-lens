# Migration Plan: DocumentLens Microservice Separation

## Overview

This document outlines the step-by-step migration plan to transform DocumentLens from a monolithic service handling multiple content types into a focused text analysis microservice, while extracting presentation and media functionality into dedicated services.

## Current State Analysis

### What DocumentLens Currently Handles:
- ✅ **Text Analysis**: Readability, writing quality, word frequency
- ✅ **Academic Analysis**: Citation checking, DOI resolution, integrity detection  
- ⚠️ **PPTX Processing**: Basic text extraction only (no presentation-specific analysis)
- ❌ **Audio/Video**: Planned but not implemented
- ✅ **Document Processing**: PDF, DOCX text extraction

### Migration Goals:
1. **DocumentLens**: Pure text analysis excellence
2. **PresentationLens**: Extract PPTX functionality + presentation-specific analysis
3. **MediaLens**: New service for audio/video processing
4. **Clean Integration**: Seamless service communication

## Migration Phases

## Phase 1: Documentation & Planning ✅

**Status**: Completed
- [x] Create comprehensive service specifications
- [x] Define API contracts and integration patterns
- [x] Document microservices architecture
- [x] Plan orchestration strategies

**Deliverables**:
- `docs/future-services/PRESENTATION-LENS.md`
- `docs/future-services/MEDIA-LENS.md` 
- `docs/future-services/ORCHESTRATOR.md`
- `docs/architecture/MICROSERVICES_ARCHITECTURE.md`

## Phase 2: DocumentLens Cleanup (Current Phase)

**Objective**: Remove non-text functionality and focus on text analysis excellence

### Step 2.1: Remove PPTX Handling
- [ ] Remove PPTX processing from `app/services/document_processor.py`
- [ ] Remove `python-pptx` dependency from requirements
- [ ] Update API documentation to remove PPTX references
- [ ] Add deprecation notice for PPTX endpoints

### Step 2.2: Update README and Documentation
- [ ] Remove audio/video references from README
- [ ] Update API documentation for text-only focus
- [ ] Add links to future PresentationLens and MediaLens services
- [ ] Update examples to show text-focused usage

### Step 2.3: Add Integration Placeholders
- [ ] Create client stubs for future service integration
- [ ] Add configuration for service discovery
- [ ] Implement graceful degradation for missing services

### Step 2.4: Enhance Text Analysis Focus
- [ ] Optimize text processing performance
- [ ] Add more text-specific analysis features
- [ ] Improve academic integrity detection
- [ ] Enhance multi-language support

**Estimated Duration**: 1-2 weeks
**Risk Level**: Low (removing unused functionality)

## Phase 3: PresentationLens Development

**Objective**: Create presentation-specific analysis service

### Step 3.1: Project Setup
- [ ] Create new `presentation-lens` repository
- [ ] Set up FastAPI project structure
- [ ] Configure development environment and dependencies
- [ ] Set up CI/CD pipeline

### Step 3.2: Core PPTX Processing
- [ ] Extract PPTX processing logic from DocumentLens
- [ ] Implement enhanced text extraction with slide structure
- [ ] Add metadata extraction (slide count, template detection)
- [ ] Implement basic design metrics

### Step 3.3: Presentation-Specific Analysis
- [ ] Implement 5x5 rule compliance checking
- [ ] Add 10-20-30 rule assessment  
- [ ] Create visual balance analysis
- [ ] Build accessibility compliance checking

### Step 3.4: DocumentLens Integration
- [ ] Implement DocumentLens client for text analysis
- [ ] Create result combination logic
- [ ] Add error handling and fallback strategies
- [ ] Test end-to-end integration

### Step 3.5: Advanced Features
- [ ] Template and brand compliance detection
- [ ] Speaker notes analysis
- [ ] Chart and image analysis
- [ ] Batch processing capabilities

**Estimated Duration**: 4-6 weeks
**Risk Level**: Medium (new service development)

## Phase 4: MediaLens Development

**Objective**: Create audio/video analysis service

### Step 4.1: Project Setup & Core Infrastructure
- [ ] Create new `media-lens` repository
- [ ] Set up FastAPI with async processing
- [ ] Configure FFmpeg and audio/video processing tools
- [ ] Set up ML model infrastructure

### Step 4.2: Audio Processing Foundation
- [ ] Implement high-quality transcription (Whisper integration)
- [ ] Add speaker diarization capabilities
- [ ] Create audio quality assessment
- [ ] Build speech pace and clarity analysis

### Step 4.3: Video Processing Foundation  
- [ ] Implement key frame extraction
- [ ] Add scene change detection
- [ ] Create visual quality assessment
- [ ] Build accessibility compliance checking

### Step 4.4: DocumentLens Integration
- [ ] Implement transcript extraction and formatting
- [ ] Create DocumentLens client integration
- [ ] Add combined result generation
- [ ] Test multimedia content analysis pipeline

### Step 4.5: Advanced Features
- [ ] Real-time streaming analysis
- [ ] Batch processing optimization
- [ ] Custom model training capabilities
- [ ] Multi-language support

**Estimated Duration**: 6-8 weeks
**Risk Level**: High (complex multimedia processing)

## Phase 5: Orchestration Implementation

**Objective**: Create seamless multi-service coordination

### Step 5.1: Frontend Orchestration Logic
- [ ] Implement service discovery and routing
- [ ] Create progressive analysis UI components
- [ ] Add intelligent service selection
- [ ] Build result combination and caching

### Step 5.2: Backend Orchestration Service (Optional)
- [ ] Create lightweight orchestration API
- [ ] Implement caching and result aggregation
- [ ] Add workflow management
- [ ] Build analytics and monitoring

### Step 5.3: Error Handling & Resilience
- [ ] Implement circuit breaker patterns
- [ ] Add graceful degradation strategies
- [ ] Create retry and fallback mechanisms
- [ ] Build comprehensive monitoring

**Estimated Duration**: 3-4 weeks
**Risk Level**: Medium (integration complexity)

## Phase 6: Testing & Validation

**Objective**: Ensure system reliability and performance

### Step 6.1: Individual Service Testing
- [ ] Unit tests for each service (>90% coverage)
- [ ] Integration tests for service interactions
- [ ] Performance testing and optimization
- [ ] Security testing and vulnerability assessment

### Step 6.2: End-to-End Testing
- [ ] Multi-service workflow testing
- [ ] Error scenario testing
- [ ] Load testing with realistic traffic
- [ ] User acceptance testing

### Step 6.3: Migration Testing
- [ ] Backward compatibility verification
- [ ] Data migration validation (if needed)
- [ ] Rollback procedure testing
- [ ] Performance comparison (before/after)

**Estimated Duration**: 2-3 weeks  
**Risk Level**: Low (validation and quality assurance)

## Phase 7: Deployment & Cutover

**Objective**: Deploy new architecture to production

### Step 7.1: Staged Rollout
- [ ] Deploy PresentationLens to staging
- [ ] Deploy MediaLens to staging  
- [ ] Deploy updated DocumentLens
- [ ] Test complete system integration

### Step 7.2: Production Deployment
- [ ] Blue-green deployment of all services
- [ ] Monitor system health and performance
- [ ] Gradual traffic migration
- [ ] Monitor user experience metrics

### Step 7.3: Legacy Cleanup
- [ ] Remove deprecated endpoints
- [ ] Clean up unused code and dependencies
- [ ] Update documentation and examples
- [ ] Archive old deployment artifacts

**Estimated Duration**: 1-2 weeks
**Risk Level**: Medium (production deployment)

## Detailed Implementation Steps

### Phase 2.1: Remove PPTX Processing

**Files to Modify:**

1. **`app/services/document_processor.py`**:
```python
# Remove these lines:
- from pptx import Presentation
- elif content_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
-     return await self._extract_from_pptx(content, filename)
- async def _extract_from_pptx(self, content: bytes, filename: str) -> str:
-     # ... entire method implementation
```

2. **`requirements.txt`**:
```diff
- python-pptx>=0.6.21
```

3. **`app/api/routes/analysis.py`** or relevant endpoints:
```python
# Add deprecation warning for PPTX files
if file.content_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
    raise HTTPException(
        status_code=400,
        detail="PPTX files are no longer supported in DocumentLens. "
               "Please use PresentationLens service for presentation analysis. "
               "See: https://github.com/user/presentation-lens"
    )
```

4. **`README.md`**:
```markdown
# DocumentLens - Text Analysis Microservice

**Focused Text Intelligence & Academic Analysis**

## What's Changed
DocumentLens now focuses exclusively on text analysis excellence. For other content types:
- **Presentations**: Use [PresentationLens](https://github.com/user/presentation-lens)
- **Audio/Video**: Use [MediaLens](https://github.com/user/media-lens)  
- **Code**: Use [CodeLens](https://github.com/user/code-lens)

## Supported Content
- Plain text analysis
- PDF text extraction and analysis
- DOCX document analysis
- Academic integrity checking
- Citation and reference validation
```

### Phase 2.2: Add Service Integration Framework

**Create `app/clients/` directory structure:**

```python
# app/clients/service_client.py
from abc import ABC, abstractmethod
import httpx
from typing import Dict, Any

class ServiceClient(ABC):
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={'Authorization': f'Bearer {api_key}'}
        )
    
    @abstractmethod
    async def analyze(self, content: str) -> Dict[str, Any]:
        pass

# app/clients/presentation_lens_client.py
class PresentationLensClient(ServiceClient):
    async def extract_and_analyze_text(self, file_content: bytes) -> Dict[str, Any]:
        """Extract text from presentation and get DocumentLens analysis"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/extract/text",
                files={"presentation_file": file_content}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"PresentationLens unavailable: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"PresentationLens error: {str(e)}"}
```

### Phase 2.3: Configuration Management

**Add service configuration:**

```python
# app/core/config.py additions
class ServiceConfig:
    PRESENTATION_LENS_URL: str = "http://presentation-lens:8001"
    MEDIA_LENS_URL: str = "http://media-lens:8002"
    CODE_LENS_URL: str = "http://code-lens:8003"
    
    SERVICE_API_KEYS: Dict[str, str] = {
        "presentation-lens": "service-key-123",
        "media-lens": "service-key-456", 
        "code-lens": "service-key-789"
    }
```

## Risk Mitigation Strategies

### 1. Backward Compatibility
**Risk**: Breaking existing API clients
**Mitigation**:
- Implement deprecation warnings before removal
- Provide migration guide and timelines
- Offer proxy endpoints during transition period
- Version API endpoints clearly

### 2. Service Dependencies
**Risk**: Circular dependencies or tight coupling
**Mitigation**:
- Use async message queues for heavy operations
- Implement circuit breakers for external calls
- Design for graceful degradation
- Create comprehensive integration tests

### 3. Data Consistency
**Risk**: Inconsistent results across services
**Mitigation**:
- Standardize response formats across services
- Implement result validation and correlation
- Use distributed tracing for debugging
- Create comprehensive test suites

### 4. Performance Degradation
**Risk**: Network latency from service calls
**Mitigation**:
- Implement intelligent caching strategies
- Use connection pooling and keep-alive
- Optimize service communication protocols
- Monitor and alert on performance metrics

## Success Criteria

### Technical Metrics
- [ ] DocumentLens response time < 2 seconds for text analysis
- [ ] PresentationLens processing time < 30 seconds for typical presentations
- [ ] MediaLens transcription accuracy > 95%
- [ ] Overall system availability > 99.5%
- [ ] Cross-service integration latency < 5 seconds

### Business Metrics  
- [ ] No degradation in user satisfaction scores
- [ ] Maintained or improved analysis accuracy
- [ ] Successful handling of 10,000+ requests/day
- [ ] Zero data loss during migration
- [ ] Developer onboarding time < 2 hours

### Quality Metrics
- [ ] Test coverage > 90% for all services
- [ ] Zero critical security vulnerabilities
- [ ] API documentation completeness > 95%
- [ ] Mean time to resolution (MTTR) < 4 hours
- [ ] Deployment success rate > 98%

## Rollback Plans

### Emergency Rollback
If critical issues arise during migration:

1. **Immediate Actions**:
   - Restore previous DocumentLens version
   - Redirect traffic to backup systems
   - Notify users of temporary service restoration

2. **Root Cause Analysis**:
   - Identify the specific failure point
   - Assess data integrity and user impact
   - Document lessons learned

3. **Recovery Strategy**:
   - Fix identified issues in staging
   - Re-test complete workflow
   - Implement additional monitoring
   - Plan revised migration timeline

### Graceful Rollback
For planned rollback during testing:

1. **Service-by-Service Rollback**:
   - Start with newest services (MediaLens)
   - Move to PresentationLens
   - Finally revert DocumentLens changes

2. **Data Migration Reversal**:
   - Restore any moved configuration
   - Re-enable deprecated endpoints
   - Update documentation to reflect rollback

## Timeline Summary

| Phase | Duration | Dependencies | Risk Level |
|-------|----------|-------------|------------|
| Phase 1: Documentation | ✅ Complete | None | Low |
| Phase 2: DocumentLens Cleanup | 1-2 weeks | None | Low |
| Phase 3: PresentationLens | 4-6 weeks | Phase 2 | Medium |
| Phase 4: MediaLens | 6-8 weeks | Phase 2 | High |
| Phase 5: Orchestration | 3-4 weeks | Phases 3,4 | Medium |
| Phase 6: Testing | 2-3 weeks | Phase 5 | Low |
| Phase 7: Deployment | 1-2 weeks | Phase 6 | Medium |

**Total Estimated Timeline**: 17-25 weeks (4-6 months)

## Next Steps

1. **Begin Phase 2**: Start DocumentLens cleanup
2. **Set up Repositories**: Create GitHub repos for PresentationLens and MediaLens
3. **Team Assignment**: Assign developers to each service
4. **Infrastructure Planning**: Plan deployment and monitoring infrastructure
5. **Stakeholder Communication**: Keep users informed of migration progress

---

**This migration plan ensures a systematic, low-risk transition to a scalable microservices architecture while maintaining service quality and user satisfaction throughout the process.**