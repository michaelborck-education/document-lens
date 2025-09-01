# Orchestrator: Multi-Service Coordination & Frontend Integration

## Overview

The **Orchestrator** is the coordination layer that enables seamless integration between multiple analysis services in the DocumentLens ecosystem. Rather than a separate backend service, it's designed as intelligent frontend logic with optional lightweight backend components for caching and workflow management.

## Architecture Decision: Frontend-First Approach

### Why Frontend Orchestration?

**Benefits of Frontend-Based Coordination:**
- **Reduced Latency**: Direct service communication without additional hops
- **Simplified Architecture**: Fewer moving parts and failure points  
- **Better User Experience**: Progressive loading and real-time feedback
- **Cost Effective**: No additional infrastructure for orchestration layer
- **Client Control**: Users can choose which analyses to run

**When Backend Orchestration Makes Sense:**
- Complex workflows requiring server-side state management
- Heavy caching requirements across multiple users
- Rate limiting and quota management across services
- Advanced analytics requiring data aggregation

### Hybrid Approach Recommendation

**Primary**: Frontend orchestration with intelligent service selection
**Secondary**: Lightweight backend for caching, analytics, and complex workflows

## Frontend Orchestration Patterns

### 1. File Type Detection & Service Routing

```javascript
// Intelligent service selection based on file type
class ServiceOrchestrator {
    async analyzeContent(file, options = {}) {
        const fileType = this.detectFileType(file);
        const analysisFlow = this.determineAnalysisFlow(fileType, options);
        
        return await this.executeFlow(analysisFlow, file);
    }
    
    detectFileType(file) {
        const extension = file.name.split('.').pop().toLowerCase();
        const mimeType = file.type;
        
        const typeMap = {
            // Text documents
            'txt': 'text',
            'docx': 'document', 
            'pdf': 'document',
            
            // Presentations  
            'pptx': 'presentation',
            'ppt': 'presentation',
            
            // Media files
            'mp4': 'video',
            'avi': 'video', 
            'mp3': 'audio',
            'wav': 'audio',
            
            // Code files
            'js': 'code',
            'py': 'code',
            'java': 'code'
        };
        
        return typeMap[extension] || 'unknown';
    }
    
    determineAnalysisFlow(fileType, options) {
        const flows = {
            'text': [
                { service: 'document-lens', endpoint: '/api/analyze/text' }
            ],
            'presentation': [
                { service: 'presentation-lens', endpoint: '/api/analyze/presentation' },
                { service: 'document-lens', endpoint: '/api/analyze/text', 
                  input: 'extracted_text' }
            ],
            'video': [
                { service: 'media-lens', endpoint: '/api/analyze/media' },
                { service: 'document-lens', endpoint: '/api/analyze/text',
                  input: 'extracted_content.text_for_analysis' }
            ],
            'code': [
                { service: 'code-lens', endpoint: '/api/analyze/code' }
            ]
        };
        
        return flows[fileType] || flows['text'];
    }
}
```

### 2. Progressive Analysis with Real-time Updates

```javascript
class ProgressiveAnalyzer {
    async analyzeWithProgress(file, onProgress) {
        const flow = this.orchestrator.determineAnalysisFlow(file);
        const results = {};
        
        for (let i = 0; i < flow.length; i++) {
            const step = flow[i];
            
            // Update progress
            onProgress({
                step: i + 1,
                totalSteps: flow.length,
                currentService: step.service,
                status: 'processing'
            });
            
            try {
                // Execute analysis step
                const stepResult = await this.executeStep(step, file, results);
                results[step.service] = stepResult;
                
                // Update with intermediate results
                onProgress({
                    step: i + 1,
                    totalSteps: flow.length,
                    currentService: step.service,
                    status: 'completed',
                    intermediateResults: results
                });
                
            } catch (error) {
                // Handle graceful degradation
                onProgress({
                    step: i + 1,
                    totalSteps: flow.length,
                    currentService: step.service,
                    status: 'error',
                    error: error.message,
                    partialResults: results
                });
            }
        }
        
        return this.combineResults(results);
    }
}
```

### 3. Parallel Processing for Independent Analyses

```javascript
class ParallelOrchestrator {
    async analyzeInParallel(file, analysisTypes) {
        const promises = [];
        
        // Identify independent analyses that can run simultaneously
        const independentAnalyses = this.identifyIndependentSteps(analysisTypes);
        const dependentAnalyses = this.identifyDependentSteps(analysisTypes);
        
        // Start independent analyses immediately
        for (const analysis of independentAnalyses) {
            promises.push(this.executeAnalysis(analysis, file));
        }
        
        // Wait for required dependencies
        const independentResults = await Promise.allSettled(promises);
        
        // Execute dependent analyses with results from previous step
        const dependentResults = await this.executeDependentAnalyses(
            dependentAnalyses, 
            file, 
            independentResults
        );
        
        return this.mergeResults(independentResults, dependentResults);
    }
    
    identifyIndependentSteps(analysisTypes) {
        // Analyses that don't depend on other service outputs
        return analysisTypes.filter(type => 
            ['presentation-design', 'video-quality', 'audio-quality'].includes(type)
        );
    }
    
    identifyDependentSteps(analysisTypes) {
        // Analyses that need text extraction from other services
        return analysisTypes.filter(type =>
            ['text-quality', 'readability', 'academic-integrity'].includes(type)
        );
    }
}
```

## Result Combination Strategies

### 1. Intelligent Result Merging

```javascript
class ResultCombiner {
    combineAnalysisResults(results) {
        const combined = {
            overall_score: this.calculateOverallScore(results),
            detailed_results: results,
            combined_insights: this.generateCombinedInsights(results),
            recommendations: this.prioritizeRecommendations(results)
        };
        
        return combined;
    }
    
    calculateOverallScore(results) {
        const weights = {
            'document-lens': 0.4,     // Text quality is core
            'presentation-lens': 0.3,  // Design matters for presentations
            'media-lens': 0.2,        // Audio/video quality
            'code-lens': 0.4          // Code quality is critical for code
        };
        
        let totalScore = 0;
        let totalWeight = 0;
        
        for (const [service, result] of Object.entries(results)) {
            if (weights[service] && result.overall_score) {
                totalScore += result.overall_score * weights[service];
                totalWeight += weights[service];
            }
        }
        
        return totalWeight > 0 ? Math.round(totalScore / totalWeight) : 0;
    }
    
    generateCombinedInsights(results) {
        const insights = [];
        
        // Cross-service insights
        if (results['presentation-lens'] && results['document-lens']) {
            const designScore = results['presentation-lens'].design_scores?.overall || 0;
            const textScore = results['document-lens'].readability?.flesch_score || 0;
            
            if (designScore > 85 && textScore > 80) {
                insights.push({
                    type: 'excellence',
                    message: 'Outstanding presentation with excellent design and highly readable content'
                });
            } else if (designScore < 60 && textScore > 85) {
                insights.push({
                    type: 'improvement',
                    message: 'Great content quality - focus on improving visual design'
                });
            }
        }
        
        if (results['media-lens'] && results['document-lens']) {
            const speechClarity = results['media-lens'].audio_analysis?.clarity_score || 0;
            const textComplexity = results['document-lens'].readability?.grade_level || 0;
            
            if (speechClarity < 70 && textComplexity > 12) {
                insights.push({
                    type: 'warning',
                    message: 'Complex content with unclear audio - consider simplifying language or improving audio quality'
                });
            }
        }
        
        return insights;
    }
}
```

### 2. Recommendation Prioritization

```javascript
class RecommendationEngine {
    prioritizeRecommendations(results) {
        const allRecommendations = this.extractAllRecommendations(results);
        const prioritized = this.scoreRecommendations(allRecommendations);
        
        return {
            critical: prioritized.filter(r => r.priority === 'critical'),
            high: prioritized.filter(r => r.priority === 'high'),  
            medium: prioritized.filter(r => r.priority === 'medium'),
            low: prioritized.filter(r => r.priority === 'low')
        };
    }
    
    scoreRecommendations(recommendations) {
        return recommendations.map(rec => {
            let priority = 'low';
            
            // Accessibility issues are critical
            if (rec.category === 'accessibility') {
                priority = 'critical';
            }
            // Academic integrity issues are critical
            else if (rec.category === 'integrity' && rec.impact > 0.8) {
                priority = 'critical';
            }
            // High-impact improvements are high priority
            else if (rec.impact > 0.6) {
                priority = 'high';
            }
            // Medium-impact improvements
            else if (rec.impact > 0.3) {
                priority = 'medium';
            }
            
            return { ...rec, priority };
        });
    }
}
```

## Caching & Performance Optimization

### 1. Frontend Caching Strategy

```javascript
class CacheManager {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }
    
    async getCachedResult(file, analysisType) {
        const key = this.generateCacheKey(file, analysisType);
        const cached = this.cache.get(key);
        
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.result;
        }
        
        return null;
    }
    
    setCachedResult(file, analysisType, result) {
        const key = this.generateCacheKey(file, analysisType);
        this.cache.set(key, {
            result,
            timestamp: Date.now()
        });
        
        // Clean up old entries periodically
        this.cleanupCache();
    }
    
    generateCacheKey(file, analysisType) {
        // Hash based on file content and analysis type
        return `${file.name}-${file.size}-${file.lastModified}-${analysisType}`;
    }
}
```

### 2. Backend Caching Service (Optional)

```python
# Lightweight caching service
from fastapi import FastAPI
from redis import Redis

app = FastAPI()
redis_client = Redis(host='localhost', port=6379, db=0)

@app.post("/api/cache/store")
async def store_result(file_hash: str, analysis_type: str, result: dict):
    """Store analysis result with TTL"""
    key = f"analysis:{file_hash}:{analysis_type}"
    redis_client.setex(key, 300, json.dumps(result))  # 5 min TTL
    return {"status": "cached"}

@app.get("/api/cache/retrieve")
async def retrieve_result(file_hash: str, analysis_type: str):
    """Retrieve cached analysis result"""
    key = f"analysis:{file_hash}:{analysis_type}"
    result = redis_client.get(key)
    
    if result:
        return {"status": "hit", "result": json.loads(result)}
    else:
        return {"status": "miss"}
```

## Error Handling & Graceful Degradation

### 1. Service Failure Management

```javascript
class ErrorHandler {
    async handleServiceFailure(service, error, partialResults) {
        const fallbackStrategies = {
            'presentation-lens': {
                fallback: 'document-lens',
                message: 'Presentation analysis unavailable, using text analysis only'
            },
            'media-lens': {
                fallback: null,
                message: 'Media analysis unavailable, manual transcription recommended'  
            },
            'document-lens': {
                fallback: 'basic-metrics',
                message: 'Advanced text analysis unavailable, showing basic metrics'
            }
        };
        
        const strategy = fallbackStrategies[service];
        
        if (strategy.fallback) {
            // Attempt fallback analysis
            try {
                const fallbackResult = await this.executeFallback(
                    strategy.fallback, 
                    partialResults
                );
                
                return {
                    success: true,
                    result: fallbackResult,
                    warnings: [strategy.message]
                };
            } catch (fallbackError) {
                return this.handleTotalFailure(service, [error, fallbackError]);
            }
        } else {
            return {
                success: false,
                partialResults,
                error: strategy.message
            };
        }
    }
}
```

### 2. Progressive Enhancement

```javascript
class ProgressiveAnalyzer {
    async analyzeWithFallbacks(file) {
        const results = {};
        const errors = [];
        
        // Core analysis (most important)
        try {
            results.core = await this.documentLens.analyzeText(file);
        } catch (error) {
            errors.push({ service: 'document-lens', error });
            results.core = this.getBasicTextMetrics(file);
        }
        
        // Enhanced analysis (nice to have)
        try {
            if (this.isPresentationFile(file)) {
                results.enhanced = await this.presentationLens.analyze(file);
            } else if (this.isMediaFile(file)) {
                results.enhanced = await this.mediaLens.analyze(file);
            }
        } catch (error) {
            errors.push({ service: 'enhanced', error });
            // Continue without enhanced analysis
        }
        
        return {
            results,
            errors,
            completeness: this.calculateCompleteness(results, errors)
        };
    }
}
```

## User Interface Integration

### 1. Analysis Progress UI

```jsx
function AnalysisProgress({ file, onComplete }) {
    const [progress, setProgress] = useState({ step: 0, totalSteps: 0 });
    const [results, setResults] = useState({});
    
    useEffect(() => {
        const orchestrator = new ServiceOrchestrator();
        
        orchestrator.analyzeWithProgress(file, (progressUpdate) => {
            setProgress(progressUpdate);
            
            if (progressUpdate.intermediateResults) {
                setResults(progressUpdate.intermediateResults);
            }
            
            if (progressUpdate.step === progressUpdate.totalSteps) {
                onComplete(progressUpdate.finalResults);
            }
        });
    }, [file]);
    
    return (
        <div className="analysis-progress">
            <ProgressBar 
                current={progress.step} 
                total={progress.totalSteps} 
            />
            <ServiceStatus 
                currentService={progress.currentService}
                status={progress.status}
            />
            <IntermediateResults results={results} />
        </div>
    );
}
```

### 2. Service Selection Interface

```jsx
function AnalysisSelector({ file, onAnalyze }) {
    const [selectedServices, setSelectedServices] = useState([]);
    const availableServices = getAvailableServices(file);
    
    return (
        <div className="service-selector">
            <h3>Choose Analysis Types:</h3>
            {availableServices.map(service => (
                <ServiceOption
                    key={service.id}
                    service={service}
                    selected={selectedServices.includes(service.id)}
                    onChange={(selected) => 
                        toggleService(service.id, selected)
                    }
                />
            ))}
            <AnalyzeButton 
                onClick={() => onAnalyze(selectedServices)}
                disabled={selectedServices.length === 0}
            />
        </div>
    );
}
```

## Deployment Architecture

### Frontend Deployment
```dockerfile
# React/Vue/Angular frontend with orchestration logic
FROM node:18-alpine
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Include service discovery and configuration
COPY service-config.json ./build/
EXPOSE 3000
CMD ["npm", "start"]
```

### Backend Caching Service (Optional)
```dockerfile
# Lightweight caching and analytics service
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "cache_service:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Service Discovery & Configuration

### 1. Dynamic Service Discovery

```javascript
class ServiceDiscovery {
    constructor() {
        this.services = new Map();
        this.healthCheckInterval = 30000; // 30 seconds
    }
    
    async discoverServices() {
        const serviceConfig = await fetch('/api/services/config');
        const services = await serviceConfig.json();
        
        for (const service of services) {
            await this.registerService(service);
        }
        
        // Start health monitoring
        this.startHealthChecks();
    }
    
    async registerService(serviceConfig) {
        this.services.set(serviceConfig.name, {
            ...serviceConfig,
            status: 'unknown',
            lastHealthCheck: null
        });
        
        // Initial health check
        await this.checkServiceHealth(serviceConfig.name);
    }
    
    async checkServiceHealth(serviceName) {
        const service = this.services.get(serviceName);
        if (!service) return;
        
        try {
            const response = await fetch(`${service.baseUrl}/health`, {
                timeout: 5000
            });
            
            service.status = response.ok ? 'healthy' : 'unhealthy';
            service.lastHealthCheck = Date.now();
        } catch (error) {
            service.status = 'unhealthy';
            service.lastHealthCheck = Date.now();
        }
    }
}
```

## Analytics & Monitoring

### 1. Usage Analytics

```javascript
class AnalyticsCollector {
    trackAnalysis(fileType, services, duration, success) {
        const event = {
            timestamp: Date.now(),
            fileType,
            services,
            duration,
            success,
            userId: this.getCurrentUserId()
        };
        
        // Send to analytics service
        this.sendAnalytics('analysis_completed', event);
    }
    
    trackServiceFailure(service, error, context) {
        const event = {
            timestamp: Date.now(),
            service,
            error: error.message,
            context,
            userId: this.getCurrentUserId()
        };
        
        this.sendAnalytics('service_failure', event);
    }
}
```

---

**The Orchestrator approach provides a flexible, performant, and user-friendly way to coordinate multiple analysis services while maintaining the ability to scale into more sophisticated backend orchestration as needs grow.**