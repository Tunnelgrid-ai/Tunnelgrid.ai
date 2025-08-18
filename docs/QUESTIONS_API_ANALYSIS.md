# Questions API - Complete Data Flow Analysis

## 🎯 **Payload Analysis: What Gets Sent**

### **Input Data Sources (From Previous Steps)**

#### **1. Brand & Product Data** (From `/api/brands/create` + `/api/brands/update`)
```json
{
  "auditId": "7913472f-838c-45a6-a62a-373cc31200d9",
  "brandName": "Haldiram Snacks Pvt",
  "brandDescription": "Haldiram Snacks Pvt. Ltd., established in 1937...",
  "brandDomain": "haldiram.com",
  "productName": "Namkeens and Bhujia"
}
```
**Database Storage**: `brand` table + `product` table + `audit` table

#### **2. Topics Data** (From `/api/topics/generate`)
```json
"topics": [
  {
    "id": "0b0eaf4d-a648-4e3c-bda4-08a8e31676c8",
    "name": "Favorite Indian Snack Brands", 
    "description": "General discussion about popular Indian snack brands..."
  }
  // 10 total topics (4 unbranded, 3 branded, 3 comparative)
]
```
**Database Storage**: `topics` table
- **Key Fields**: `topic_id`, `audit_id`, `topic_name`, `topic_category`, `visibility`

#### **3. Personas Data** (From `/api/personas/generate`)
```json
"personas": [
  {
    "id": "eb65c5b2-9f95-4a25-8c28-3b7dd429981d",
    "name": "Festive Celebrant",
    "description": "Indian families who prioritize traditional snacks...",
    "painPoints": ["Limited healthier snack options", "Difficulty finding authentic flavors"],
    "motivators": ["Authentic taste", "Convenience", "Variety of options"],
    "demographics": {
      "ageRange": "25-45",
      "gender": "Primarily female", 
      "location": "Urban and suburban families",
      "goals": ["Impress guests with unique snacks"]
    }
  }
  // 7 total personas
]
```
**Database Storage**: `personas` table (estimated based on pattern)

## 🔄 **Response Analysis: What Gets Generated**

### **Generated Questions Structure**
```json
[
  {
    "id": "a7be715b-9cf4-4a57-8464-396acb632345",
    "text": "best Indian snack brands for Diwali",
    "personaId": "eb65c5b2-9f95-4a25-8c28-3b7dd429981d", 
    "auditId": "7913472f-838c-45a6-a62a-373cc31200d9",
    "topicName": "Best Bhujia for Diwali Celebrations",
    "queryType": "unbranded"
  }
  // 70 total questions (10 per persona × 7 personas)
]
```

### **Question Distribution Analysis**

#### **By Query Type** (AI-Generated Categories)
- **Unbranded**: 28 questions (40%) - Generic brand research
- **Branded**: 21 questions (30%) - Direct Haldiram mentions  
- **Comparative**: 21 questions (30%) - Brand vs competitor

#### **By Persona** (7 personas × 10 questions each)
1. **Festive Celebrant**: 10 questions (Diwali focus)
2. **Health-Conscious Parent**: 11 questions (Kids health focus)
3. **Snack Enthusiast**: 9 questions (Variety focus)
4. **Busy Professional**: 10 questions (Convenience focus)
5. **Brand Loyalist**: 9 questions (Haldiram loyalty focus)
6. **Value Seeker**: 9 questions (Price/value focus)
7. **Foodie Explorer**: 10 questions (Authenticity focus)

**Total**: 68 questions generated

## 📊 **Database Storage Mapping**

### **Table: `queries`** (Where questions get stored)
```sql
CREATE TABLE queries (
  query_id VARCHAR(255) PRIMARY KEY,        -- "a7be715b-9cf4-4a57..."
  audit_id VARCHAR(255) NOT NULL,          -- "7913472f-838c-45a6..."  
  persona VARCHAR(255) NOT NULL,           -- "eb65c5b2-9f95-4a25..." (persona_id)
  query_text TEXT NOT NULL,               -- "best Indian snack brands for Diwali"
  query_type VARCHAR(50),                 -- "unbranded"/"branded"/"comparative"
  topic_name TEXT,                        -- "Best Bhujia for Diwali Celebrations"
  FOREIGN KEY (audit_id) REFERENCES audit(audit_id)
);
```

### **Critical Data Relationships for Report**

#### **For Comprehensive Report, We Need to JOIN:**

1. **audit** ← Core project
2. **brand** ← Brand information  
3. **product** ← Product details
4. **topics** ← Generated topics (with categories)
5. **personas** ← Generated personas (with demographics)
6. **queries** ← Generated questions
7. **analysis_jobs** ← Analysis status
8. **responses** ← AI model responses 
9. **brand_mentions** ← Brand visibility results
10. **citations** ← Source references

## 🎯 **What's Missing for Final Report**

### **Backend API Needed**: `/api/analysis/comprehensive-report/{audit_id}`

**Required Query** (Complex JOIN):
```sql
SELECT 
  -- Brand & Product Info
  b.brand_name, b.domain, b.description,
  p.product_name,
  
  -- Analysis Overview  
  aj.status, aj.total_queries, aj.completed_queries,
  
  -- Topic Breakdown
  COUNT(DISTINCT t.topic_id) as total_topics,
  COUNT(DISTINCT CASE WHEN t.topic_category = 'unbranded' THEN t.topic_id END) as unbranded_topics,
  COUNT(DISTINCT CASE WHEN t.topic_category = 'branded' THEN t.topic_id END) as branded_topics,
  COUNT(DISTINCT CASE WHEN t.topic_category = 'comparative' THEN t.topic_id END) as comparative_topics,
  
  -- Persona Breakdown
  COUNT(DISTINCT pe.persona_id) as total_personas,
  
  -- Questions Breakdown  
  COUNT(DISTINCT q.query_id) as total_questions,
  COUNT(DISTINCT CASE WHEN q.query_type = 'unbranded' THEN q.query_id END) as unbranded_questions,
  COUNT(DISTINCT CASE WHEN q.query_type = 'branded' THEN q.query_id END) as branded_questions,
  COUNT(DISTINCT CASE WHEN q.query_type = 'comparative' THEN q.query_id END) as comparative_questions,
  
  -- Response Analysis
  COUNT(DISTINCT r.response_id) as total_responses,
  COUNT(DISTINCT bm.mention_id) as total_brand_mentions,
  AVG(bm.sentiment_score) as avg_sentiment
  
FROM audit a
JOIN brand b ON a.brand_id = b.brand_id  
JOIN product p ON a.product_id = p.product_id
LEFT JOIN topics t ON a.audit_id = t.audit_id
LEFT JOIN personas pe ON a.audit_id = pe.audit_id  
LEFT JOIN queries q ON a.audit_id = q.audit_id
LEFT JOIN analysis_jobs aj ON a.audit_id = aj.audit_id
LEFT JOIN responses r ON q.query_id = r.query_id
LEFT JOIN brand_mentions bm ON r.response_id = bm.response_id
WHERE a.audit_id = ?
GROUP BY b.brand_name, b.domain, b.description, p.product_name, aj.status, aj.total_queries, aj.completed_queries;
```

## 🚀 **Next Steps**

1. **Implement Missing Backend API**: `/api/analysis/comprehensive-report/{audit_id}`
2. **Create Database Functions**: For complex aggregations 
3. **Frontend Integration**: Connect report page to new API
4. **Data Visualization**: Charts showing topic/persona/question breakdowns

The data structure is perfectly set up for comprehensive reporting - we just need the backend API to aggregate and serve it! 🎯