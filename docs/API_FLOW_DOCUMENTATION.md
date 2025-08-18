# Tunnelgrid.ai - Complete API Flow Documentation

## 🔄 **Overview**

This document traces every API call from frontend to backend throughout the entire brand analysis workflow. Perfect for new developers to understand the system flow.

## 📋 **Complete Workflow: 15 API Calls**

### **Phase 1: Brand Discovery & Creation (4 APIs)**

#### 1. **Brand Search** 
```
Frontend: BrandSearchPage.tsx (SearchBar component)
API: GET /api/brand-search?q={searchTerm}
Backend: routes/brands.py → search_brands()
Purpose: Search Logo.dev API for brand suggestions
Response: List of brands with name, domain, logo_url, etc.
```

#### 2. **Brand Creation**
```
Frontend: BrandSearchPage.tsx line 102
API: POST /api/brands/create
Payload: { brand_name, domain }
Backend: routes/brands.py → create_brand()
Purpose: Insert brand into Supabase 'brand' table
Response: { success: true, data: { brand_id: "uuid", ... } }
```

#### 3. **AI Brand Analysis** 
```
Frontend: BrandSearchPage.tsx line 124
API: POST /api/brands/analyze
Payload: { brand_name, domain }
Backend: routes/brands.py → analyze_brand()
Purpose: Uses OpenAI GPT-4o web search to research brand
AI Task: Generate description + product list
Response: { description: "...", product: ["Product1", "Product2", ...] }
```

#### 4. **Brand Update with Products**
```
Frontend: BrandSearchPage.tsx line 142
API: POST /api/brands/update
Payload: { brand_name, brand_description, product: [...] }
Backend: routes/brands.py → update_brand_with_products()
Purpose: Update brand description + create product records
Database: Updates 'brand' table, inserts into 'product' table
Response: { success: true, brand_id: "uuid", products_created: 5 }
```

### **Phase 2: Setup Wizard (7 APIs)**

#### 5. **Audit Creation** (Project Start)
```
Frontend: BrandInfoStep.tsx → auditService.createAudit()
API: POST /api/audits/create
Payload: { brand_id, product_id, user_id }
Backend: routes/audits.py → create_audit()
Purpose: Create project record in 'audit' table
Response: { audit_id: "b7587f68-6d61-4b8f-9917-95f42f29e148" }
Key: This audit_id links ALL subsequent data (topics, personas, questions)
```

#### 6. **Topics AI Generation**
```
Frontend: TopicsStep.tsx line 184 → groqService.generateTopics()
API: POST /api/topics/generate
Payload: { brandName, brandDomain, productName }
Backend: routes/topics.py → generate_topics()
AI Service: GroqCloud (Llama3-70B)
Purpose: Generate relevant topics for brand/product
Response: { topics: [{ name, description, category }], source: "ai" }
```

#### 7. **Topics Storage**
```
Frontend: TopicsStep.tsx line 196 → topicsService.storeTopics()
API: POST /api/topics/store
Payload: { auditId, topics: [...], source: "ai" }
Backend: routes/topics.py → store_topics()
Purpose: Save topics to database linked to audit_id
Database: Inserts into 'topics' table with audit_id foreign key
```

#### 8. **Personas AI Generation**
```
Frontend: PersonasStep.tsx → personasService.generatePersonas()
API: POST /api/personas/generate
Payload: { brandName, brandDescription, topics: [...], auditId }
Backend: routes/personas.py → generate_personas()
AI Service: GroqCloud (Llama3-70B)
Purpose: Create customer personas with demographics, pain points, motivators
Response: { personas: [{ type, description, characteristics }], source: "ai" }
```

#### 9. **Personas Storage**
```
Frontend: PersonasStep.tsx → personasService.storePersonas()
API: POST /api/personas/store
Payload: { auditId, personas: [...] }
Backend: routes/personas.py → store_personas()
Purpose: Save personas to database
Database: Inserts into 'personas' table
Example: Your logs show "Sneaker Collector", "Brand Loyalist", etc.
```

#### 10. **Questions AI Generation**
```
Frontend: QuestionsStep.tsx → questionService.generateQuestions()
API: POST /api/questions/generate
Payload: { brandName, personas: [...], topics: [...], auditId }
Backend: routes/questions.py → generate_questions()
AI Service: GroqCloud (Llama3-70B)
Purpose: Generate persona-specific questions about the brand
Response: { questions: [{ persona_id, question_text, intent }] }
```

#### 11. **Questions Storage**
```
Frontend: QuestionsStep.tsx → questionService.storeQuestions()
API: POST /api/questions/store
Payload: { auditId, questions: [...] }
Backend: routes/questions.py → store_questions()
Purpose: Save questions to database
Database: Inserts into 'questions' table linked to personas
```

### **Phase 3: Analysis Execution (4 APIs)**

#### 12. **Setup Completion**
```
Frontend: useWizardState.ts line 436 → auditService.markSetupComplete()
API: PUT /api/audits/{audit_id}/mark-setup-complete
Backend: routes/audits.py → mark_setup_complete()
Purpose: Mark audit as ready for AI analysis
Database: Updates audit status to "setup_complete"
```

#### 13. **Analysis Job Start** 
```
Frontend: useWizardState.ts line 452 → analysisService.startAnalysisJob()
API: POST /api/analysis/start
Payload: { audit_id }
Backend: routes/analysis.py → start_analysis()
Purpose: Start background AI analysis across multiple models
AI Models: ChatGPT, Claude, Perplexity
Process: Queries each AI model with every generated question
Response: { job_id, total_queries, estimated_completion_time }
```

#### 14. **Analysis Progress Tracking**
```
Frontend: Real-time polling → analysisService.getAnalysisStatus()
API: GET /api/analysis/status/{job_id}
Backend: routes/analysis.py → get_analysis_status()
Purpose: Track analysis progress
Response: { status, completed_queries, total_queries, progress_percentage }
```

#### 15. **Analysis Results Retrieval** 
```
Frontend: analysisService.getAnalysisResults()
API: GET /api/analysis/results/{audit_id}
Backend: routes/analysis.py → get_analysis_results()
Purpose: Get comprehensive analysis results
Response: Complete brand analysis data for report generation
```

## 🏗️ **Data Flow Architecture**

```
Brand Search → Brand Creation → AI Analysis → Brand Update
     ↓
Audit Creation (Project Start)
     ↓
Topics Generation → Topics Storage
     ↓
Personas Generation → Personas Storage  
     ↓
Questions Generation → Questions Storage
     ↓
Setup Complete → Analysis Start → Progress Tracking → Results
     ↓
Comprehensive Report Generation
```

## 🔑 **Key Concepts**

### **Audit ID**: The Central Identifier
- Every analysis project gets a unique `audit_id` 
- Example from your logs: `b7587f68-6d61-4b8f-9917-95f42f29e148`
- Links all data: topics, personas, questions, analysis results
- Think of it as a "project ID" for the entire brand analysis

### **AI Model Integration**
- **GroqCloud (Llama3-70B)**: Topics, personas, questions generation
- **OpenAI GPT-4o**: Initial brand research with web search
- **ChatGPT/Claude/Perplexity**: Final analysis queries (via OpenAI API)

### **Database Relationships**
```
audit (parent)
├── brand_id (foreign key)
├── product_id (foreign key)  
├── user_id (foreign key)
└── audit_id (primary key)
    ├── topics (audit_id FK)
    ├── personas (audit_id FK)
    ├── questions (audit_id FK, persona_id FK)
    ├── analysis_jobs (audit_id FK)
    └── analysis_results (audit_id FK)
```

## 🎯 **Your Next Task: Report Feature**

The comprehensive report page exists but needs connection to real data:

### **Current State**
- Frontend: `ComprehensiveReportPage.tsx` exists with mock data
- Service: `analysisService.getComprehensiveReport()` partially implemented
- Route: `/reports/{reportId}` works with demo data

### **What You Need to Implement**
1. **Backend API**: Complete `GET /api/analysis/results/{audit_id}` 
2. **Data Processing**: Transform raw analysis results into report format
3. **Frontend Integration**: Connect real data to existing report components
4. **Navigation**: Add link from analysis completion to report page

The foundation is all there - you just need to connect the final pieces!