# Perplexity API Integration Implementation Plan

## Overview
This document outlines the implementation plan for integrating Perplexity API into the existing AI brand analysis system, enabling concurrent analysis across multiple LLM services (OpenAI, Perplexity, and Gemini).

## Current System Architecture
- **Frontend**: React/TypeScript with enhanced loading screen for multi-service progress tracking
- **Backend**: FastAPI with modular AI service architecture
- **Database**: PostgreSQL with analysis job tracking
- **Current Services**: OpenAI GPT-4o integration

## Phase 1: Backend Infrastructure (Week 1)

### 1.1 Service Architecture Updates
- [ ] Create `PerplexityService` class in `backend/app/services/perplexity_service.py`
- [ ] Implement base `LLMService` abstract class for common functionality
- [ ] Update `ai_analysis.py` to support concurrent multi-service execution
- [ ] Add service factory pattern for dynamic service selection

### 1.2 Configuration & Environment Setup
- [ ] Add `PERPLEXITY_API_KEY` to environment variables
- [ ] Update `backend/app/core/config.py` with Perplexity settings
- [ ] Add Perplexity API configuration validation
- [ ] Create service configuration management system

### 1.3 Database Schema Updates
- [ ] Add `service_type` column to analysis tables
- [ ] Create migration for service-specific tracking
- [ ] Update analysis job status tracking for multi-service support
- [ ] Add service-specific metrics tables

## Phase 2: Perplexity Service Implementation (Week 2)

### 2.1 Core Perplexity Service
```python
# backend/app/services/perplexity_service.py
class PerplexityService:
    """Service for Perplexity API integration"""
    
    BASE_URL = "https://api.perplexity.ai/chat/completions"
    
    async def analyze_brand_perception(self, request: AIAnalysisRequest) -> AIAnalysisResponse:
        # Implementation for Perplexity API calls
        # Handle response parsing and citation extraction
        # Return standardized AIAnalysisResponse
```

### 2.2 API Integration Features
- [ ] Implement Perplexity chat completions API
- [ ] Add web search capabilities for real-time data
- [ ] Handle Perplexity-specific response format
- [ ] Implement citation extraction from Perplexity responses
- [ ] Add brand mention detection and sentiment analysis

### 2.3 Response Processing
- [ ] Parse Perplexity's structured response format
- [ ] Extract citations from Perplexity's web search results
- [ ] Handle Perplexity's unique annotation system
- [ ] Implement fallback parsing for unstructured responses

## Phase 3: Multi-Service Orchestration (Week 3)

### 3.1 Concurrent Execution Engine
```python
# backend/app/services/multi_service_orchestrator.py
class MultiServiceOrchestrator:
    """Orchestrates concurrent analysis across multiple LLM services"""
    
    async def run_concurrent_analysis(self, audit_id: str, services: List[LLMServiceType]):
        # Execute analysis across all specified services concurrently
        # Track individual service progress
        # Aggregate and combine results
```

### 3.2 Service Coordination
- [ ] Implement async task management for concurrent API calls
- [ ] Add service-specific error handling and retry logic
- [ ] Create progress tracking for individual services
- [ ] Implement result aggregation and deduplication

### 3.3 Job Management Updates
- [ ] Update analysis job creation to support multiple services
- [ ] Modify status tracking to include service-specific progress
- [ ] Implement service-specific error recovery
- [ ] Add service performance metrics collection

## Phase 4: Frontend Integration (Week 4)

### 4.1 Enhanced UI Components
- [ ] Update analysis loading screen with service-specific progress bars
- [ ] Add service selection interface in brand setup wizard
- [ ] Create service comparison view in results
- [ ] Implement service-specific error display

### 4.2 Service Configuration UI
```typescript
// frontend/src/components/setup/ServiceSelectionStep.tsx
interface ServiceSelectionProps {
  selectedServices: LLMServiceType[];
  onServiceToggle: (service: LLMServiceType) => void;
}
```

### 4.3 Results Display Updates
- [ ] Create service-specific result sections
- [ ] Add service comparison charts
- [ ] Implement service confidence scoring
- [ ] Create aggregated insights view

## Phase 5: Testing & Quality Assurance (Week 5)

### 5.1 Unit Testing
- [ ] Test Perplexity service integration
- [ ] Validate multi-service orchestration
- [ ] Test error handling and recovery
- [ ] Verify response parsing accuracy

### 5.2 Integration Testing
- [ ] End-to-end multi-service analysis flow
- [ ] Performance testing with concurrent services
- [ ] Load testing with multiple concurrent jobs
- [ ] API rate limiting and quota management

### 5.3 User Acceptance Testing
- [ ] Test service selection workflow
- [ ] Validate progress tracking accuracy
- [ ] Test error scenarios and recovery
- [ ] Verify result quality and consistency

## Phase 6: Performance Optimization (Week 6)

### 6.1 Caching & Optimization
- [ ] Implement response caching for repeated queries
- [ ] Add intelligent service routing based on query type
- [ ] Optimize concurrent execution patterns
- [ ] Implement request batching for efficiency

### 6.2 Monitoring & Analytics
- [ ] Add service performance monitoring
- [ ] Implement cost tracking per service
- [ ] Create service quality metrics
- [ ] Add real-time service health monitoring

## Technical Implementation Details

### Perplexity API Configuration
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # Existing OpenAI config
    OPENAI_API_KEY: str
    
    # New Perplexity config
    PERPLEXITY_API_KEY: str
    PERPLEXITY_MODEL: str = "llama-3.1-sonar-small-128k-online"
    PERPLEXITY_MAX_TOKENS: int = 4000
    PERPLEXITY_TEMPERATURE: float = 0.7
    
    # Gemini config (future)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
```

### Service Factory Pattern
```python
# backend/app/services/service_factory.py
class LLMServiceFactory:
    """Factory for creating LLM service instances"""
    
    @staticmethod
    def create_service(service_type: LLMServiceType) -> BaseLLMService:
        if service_type == LLMServiceType.OPENAI:
            return OpenAIService()
        elif service_type == LLMServiceType.PERPLEXITY:
            return PerplexityService()
        elif service_type == LLMServiceType.GEMINI:
            return GeminiService()
        else:
            raise ValueError(f"Unsupported service type: {service_type}")
```

### Concurrent Analysis Implementation
```python
# backend/app/services/analysis_orchestrator.py
class AnalysisOrchestrator:
    async def run_multi_service_analysis(
        self, 
        audit_id: str, 
        services: List[LLMServiceType]
    ) -> AnalysisResults:
        # Create tasks for each service
        tasks = []
        for service in services:
            task = self._run_service_analysis(audit_id, service)
            tasks.append(task)
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate and combine results
        return self._aggregate_results(results)
```

## API Endpoints to Update

### 1. Analysis Job Creation
```python
# POST /api/analysis/start
{
    "audit_id": "uuid",
    "services": ["openai", "perplexity", "gemini"]
}
```

### 2. Job Status Response
```python
# GET /api/analysis/status/{job_id}
{
    "job_id": "uuid",
    "status": "running",
    "progress_percentage": 65.5,
    "service_statuses": [
        {
            "service": "openai",
            "status": "completed",
            "progress_percentage": 100.0,
            "completed_queries": 50,
            "total_queries": 50
        },
        {
            "service": "perplexity",
            "status": "running",
            "progress_percentage": 30.0,
            "completed_queries": 15,
            "total_queries": 50
        }
    ]
}
```

## Risk Mitigation

### 1. API Rate Limiting
- Implement exponential backoff for rate limit errors
- Add service-specific rate limit tracking
- Create fallback mechanisms for service failures

### 2. Cost Management
- Track API usage per service
- Implement cost limits and alerts
- Add service selection based on cost efficiency

### 3. Quality Assurance
- Implement response quality scoring
- Add service-specific validation
- Create result consistency checks

## Success Metrics

### 1. Performance Metrics
- Analysis completion time reduction
- Service availability and uptime
- API response time optimization

### 2. Quality Metrics
- Citation accuracy improvement
- Brand mention detection enhancement
- User satisfaction scores

### 3. Cost Metrics
- Per-query cost optimization
- Service efficiency ratios
- Overall analysis cost reduction

## Future Enhancements

### 1. Advanced Features
- Service-specific prompt optimization
- Dynamic service selection based on query type
- Real-time service performance adaptation

### 2. Additional Services
- Anthropic Claude integration
- Local model support (Ollama)
- Custom model endpoint support

### 3. Analytics & Insights
- Service performance analytics
- Query optimization recommendations
- Cost-benefit analysis tools

## Implementation Timeline

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Backend Infrastructure | Service architecture, config updates, database migrations |
| 2 | Perplexity Service | Core service implementation, API integration, response processing |
| 3 | Multi-Service Orchestration | Concurrent execution, service coordination, job management |
| 4 | Frontend Integration | UI updates, service selection, results display |
| 5 | Testing & QA | Unit tests, integration tests, user acceptance testing |
| 6 | Performance Optimization | Caching, monitoring, analytics implementation |

## Conclusion

This implementation plan provides a comprehensive roadmap for integrating Perplexity API into the existing AI brand analysis system. The phased approach ensures minimal disruption to existing functionality while adding powerful new capabilities for multi-service analysis.

The enhanced system will provide users with more comprehensive and reliable brand analysis results through the combination of multiple AI services, while maintaining the existing user experience and adding new features for service selection and progress tracking. 