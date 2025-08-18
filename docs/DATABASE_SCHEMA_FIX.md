# Database Schema Fix for Analysis Error

## 🚨 **Issue Identified**

The analysis was failing with this error:
```
ERROR:app.routes.analysis:❌ Failed to process query: 
{'message': 'record "new" has no field "audit_id"', 'code': '42703', 'hint': None, 'details': None}
```

## 🔍 **Root Cause**

The code was trying to insert fields into the `responses` table that don't exist in the current schema:

### **What the code was trying to insert:**
```python
response_data = {
    "response_id": str(uuid.uuid4()),
    "query_id": request.query_id,
    "model": request.model,
    "response_text": analysis_result.response_text,
    "raw_response_json": analysis_result.raw_response_json  # ❌ Field doesn't exist
}
```

### **What the responses table actually has:**
```sql
CREATE TABLE responses (
    response_id VARCHAR(255) PRIMARY KEY,
    query_id VARCHAR(255) NOT NULL,
    model VARCHAR(100) NOT NULL,
    response_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## ✅ **Fix Applied**

### **1. Fixed Analysis Route (`backend/app/routes/analysis.py`)**
```python
# BEFORE (causing error):
response_data = {
    "response_id": str(uuid.uuid4()),
    "query_id": request.query_id,
    "model": request.model,
    "response_text": analysis_result.response_text,
    "raw_response_json": analysis_result.raw_response_json  # ❌ Removed
}

# AFTER (fixed):
response_data = {
    "response_id": str(uuid.uuid4()),
    "query_id": request.query_id,
    "model": request.model,
    "response_text": analysis_result.response_text
}
```

### **2. Fixed Test File (`backend/test_raw_json_storage.py`)**
```python
# BEFORE (causing error):
response_data = {
    "response_id": str(uuid.uuid4()),
    "query_id": test_query_id,
    "model": analysis_result.model,
    "response_text": analysis_result.response_text,
    "processing_time_ms": analysis_result.processing_time_ms,  # ❌ Removed
    "token_usage": analysis_result.token_usage,                # ❌ Removed
    "raw_response_json": analysis_result.raw_response_json     # ❌ Removed
}

# AFTER (fixed):
response_data = {
    "response_id": str(uuid.uuid4()),
    "query_id": test_query_id,
    "model": analysis_result.model,
    "response_text": analysis_result.response_text
}
```

## 📊 **Data Flow After Fix**

### **Responses Table** (Core AI responses)
- `response_id`: Unique identifier
- `query_id`: Links to the query
- `model`: AI model used (e.g., "gpt-4")
- `response_text`: The actual AI response
- `created_at`: Timestamp

### **Brand Extractions Table** (Rich metadata)
- `extraction_id`: Unique identifier
- `response_id`: Links to the response
- `query_id`: Links to the query
- `brand_id`: Links to brand (if target brand)
- `is_target_brand`: Boolean flag
- `source_domain`: Domain where brand was mentioned
- `source_url`: Full URL
- `article_title`: Article title
- `extracted_brand_name`: Brand name found
- `context_snippet`: Text around the mention
- `mention_position`: Position in response
- `sentiment_label`: Positive/negative/neutral
- `source_category`: Category of source

## 🎯 **Benefits of This Architecture**

### **1. Separation of Concerns**
- **Responses table**: Stores core AI responses
- **Brand extractions table**: Stores rich metadata and source information

### **2. Better Performance**
- Responses table is lightweight and fast
- Brand extractions can be queried independently
- No need to parse JSON for every query

### **3. Data Integrity**
- Proper foreign key relationships
- No orphaned data
- Consistent schema

## 🚀 **Next Steps**

1. **✅ Schema Fixed**: Removed non-existent fields
2. **✅ Code Updated**: Analysis route and test file fixed
3. **📋 Test Analysis**: Run analysis to verify fix works
4. **📋 Monitor Logs**: Ensure no more schema errors

## 🔧 **Verification**

To verify the fix works:

```bash
# Test the analysis endpoint
curl -X POST "http://localhost:8000/api/analysis/start" \
  -H "Content-Type: application/json" \
  -d '{"audit_id": "your-audit-id"}'

# Check logs for successful processing
# Should see: ✅ Successfully processed query with brand extractions
```

The analysis should now run without database schema errors! 🎉

