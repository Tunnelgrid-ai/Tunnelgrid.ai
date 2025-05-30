# Tunnelgrid.ai API Reference

## 🚀 Overview

This document provides a comprehensive reference for the Tunnelgrid.ai REST API. The API enables AI-powered brand analysis, persona generation, question creation, and topic generation.

**Base URL**: `http://localhost:8000`
**Documentation**: `http://localhost:8000/docs` (Interactive Swagger UI)
**ReDoc**: `http://localhost:8000/redoc`

## 🔐 Authentication

All API endpoints are currently public. Future versions may include API key authentication.

## 📊 Response Format

All API responses follow a consistent JSON format:

```json
{
  "success": true,
  "data": { /* Response data */ },
  "message": "Operation completed successfully"
}
```

Error responses:

```json
{
  "detail": "Error description",
  "status_code": 400
}
```

## 🏷️ Brand Management

### Search Brands

Search for brands using the Logo.dev API.

**Endpoint**: `GET /api/brands/search`

**Parameters**:
- `q` (required): Search query string (minimum 1 character)

**Example Request**:
```bash
curl "http://localhost:8000/api/brands/search?q=apple"
```

**Example Response**:
```json
[
  {
    "name": "Apple Inc.",
    "domain": "apple.com"
  },
  {
    "name": "Apple Bank",
    "domain": "applebank.com"
  }
]
```

**Error Responses**:
- `400`: Invalid query parameter
- `401`: Logo.dev API authentication failed
- `500`: Logo.dev API key not configured

---

### Create Brand

Insert a new brand into the database.

**Endpoint**: `POST /api/brands/create`

**Request Body**:
```json
{
  "brand_name": "Apple Inc.",
  "domain": "apple.com",
  "brand_description": "Technology company"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "brand_name": "Apple Inc.",
    "domain": "apple.com",
    "brand_description": "Technology company",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Brand created successfully"
}
```

---

### Analyze Brand

Generate AI-powered brand description and products.

**Endpoint**: `POST /api/brands/analyze`

**Request Body**:
```json
{
  "brand_name": "Apple Inc.",
  "domain": "apple.com"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "description": "Leading technology company known for innovative consumer electronics, software, and services.",
    "products": ["iPhone", "Mac", "iPad", "Apple Watch", "AirPods"]
  },
  "message": "Brand analysis completed"
}
```

## 👥 Persona Management

### Generate Personas

Create AI-powered customer personas for a brand.

**Endpoint**: `POST /api/personas/generate`

**Request Body**:
```json
{
  "brand_name": "Apple Inc.",
  "brand_description": "Technology company",
  "number_of_personas": 3
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "personas": [
      {
        "id": 1,
        "name": "Tech Enthusiast",
        "description": "Early adopters who love cutting-edge technology",
        "age_range": "25-40",
        "income_level": "High",
        "interests": ["Technology", "Innovation", "Gadgets"]
      }
    ]
  },
  "message": "Personas generated successfully"
}
```

---

### List Personas

Get all personas for a brand.

**Endpoint**: `GET /api/personas/`

**Parameters**:
- `brand_id` (optional): Filter by brand ID

**Example Response**:
```json
[
  {
    "id": 1,
    "name": "Tech Enthusiast",
    "description": "Early adopters who love cutting-edge technology",
    "brand_id": 1,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### Get Persona by ID

Get a specific persona by its ID.

**Endpoint**: `GET /api/personas/{id}`

**Example Response**:
```json
{
  "id": 1,
  "name": "Tech Enthusiast",
  "description": "Early adopters who love cutting-edge technology",
  "age_range": "25-40",
  "income_level": "High",
  "interests": ["Technology", "Innovation", "Gadgets"],
  "brand_id": 1,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## ❓ Question Management

### Generate Questions

Create AI-powered questions for personas.

**Endpoint**: `POST /api/questions/generate`

**Request Body**:
```json
{
  "persona_ids": [1, 2, 3],
  "questions_per_persona": 5
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "questions": [
      {
        "id": 1,
        "question": "What features matter most to you in a smartphone?",
        "persona_id": 1,
        "category": "Product Preferences"
      }
    ]
  },
  "message": "Questions generated successfully"
}
```

---

### List Questions

Get all questions, optionally filtered by persona.

**Endpoint**: `GET /api/questions/`

**Parameters**:
- `persona_id` (optional): Filter by persona ID

**Example Response**:
```json
[
  {
    "id": 1,
    "question": "What features matter most to you in a smartphone?",
    "persona_id": 1,
    "category": "Product Preferences",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

### Retry Failed Personas

Retry question generation for personas that previously failed.

**Endpoint**: `POST /api/questions/retry-failed-personas`

**Example Response**:
```json
{
  "success": true,
  "data": {
    "retried_personas": [1, 2],
    "total_questions_generated": 10
  },
  "message": "Failed personas retried successfully"
}
```

## 📝 Topic Management

### Generate Topics

Create AI-powered topics for a brand.

**Endpoint**: `POST /api/topics/generate`

**Request Body**:
```json
{
  "brand_name": "Apple Inc.",
  "brand_description": "Technology company",
  "number_of_topics": 5
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "topics": [
      {
        "title": "The Future of Mobile Technology",
        "description": "Exploring upcoming innovations in smartphones",
        "category": "Technology Trends"
      }
    ]
  },
  "message": "Topics generated successfully"
}
```

---

### Topics Health Check

Check the health of the topics service.

**Endpoint**: `GET /api/topics/health`

**Example Response**:
```json
{
  "status": "healthy",
  "service": "topics",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 📦 Product Management

### List Products

Get all products for a brand.

**Endpoint**: `GET /api/products/`

**Parameters**:
- `brand_id` (optional): Filter by brand ID

**Example Response**:
```json
[
  {
    "id": 1,
    "name": "iPhone",
    "description": "Smartphone",
    "brand_id": 1,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

## 📊 Audit Management

### List Audits

Get audit logs for tracking changes.

**Endpoint**: `GET /api/audits/`

**Example Response**:
```json
[
  {
    "id": 1,
    "action": "CREATE",
    "entity_type": "brand",
    "entity_id": 1,
    "timestamp": "2024-01-01T00:00:00Z"
  }
]
```

## 🏥 Health Checks

### Global Health Check

Check the overall health of the API and its dependencies.

**Endpoint**: `GET /health`

**Example Response**:
```json
{
  "status": "healthy",
  "services": {
    "api": "running",
    "supabase": "available",
    "groqcloud": "available",
    "logodev": "available"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "environment": "development"
}
```

---

### Root Endpoint

Get basic API information.

**Endpoint**: `GET /`

**Example Response**:
```json
{
  "message": "AI Brand Analysis API",
  "status": "running",
  "version": "1.0.0",
  "environment": "development",
  "docs": "/docs",
  "endpoints": {
    "topics": "/api/topics",
    "brands": "/api/brands",
    "products": "/api/products",
    "audits": "/api/audits",
    "personas": "/api/personas",
    "questions": "/api/questions"
  }
}
```

## 📚 Data Models

### Brand Model

```json
{
  "id": 1,
  "brand_name": "Apple Inc.",
  "domain": "apple.com",
  "brand_description": "Technology company",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Persona Model

```json
{
  "id": 1,
  "name": "Tech Enthusiast",
  "description": "Early adopters who love cutting-edge technology",
  "age_range": "25-40",
  "income_level": "High",
  "interests": ["Technology", "Innovation", "Gadgets"],
  "brand_id": 1,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Question Model

```json
{
  "id": 1,
  "question": "What features matter most to you in a smartphone?",
  "persona_id": 1,
  "category": "Product Preferences",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🚨 Error Handling

### Common Error Codes

- **400 Bad Request**: Invalid request parameters or body
- **401 Unauthorized**: Authentication failed (API keys)
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side error
- **503 Service Unavailable**: External service unavailable

### Error Response Format

```json
{
  "detail": "Specific error message",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔧 Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default**: 100 requests per minute per IP
- **AI Endpoints**: 10 requests per minute per IP (due to processing time)

Rate limit headers:
- `X-RateLimit-Limit`: Number of requests allowed
- `X-RateLimit-Remaining`: Number of requests remaining
- `X-RateLimit-Reset`: Time when rate limit resets

## 🧪 Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Search brands
curl "http://localhost:8000/api/brands/search?q=apple"

# Create brand
curl -X POST http://localhost:8000/api/brands/create \
  -H "Content-Type: application/json" \
  -d '{"brand_name": "Test Brand", "domain": "test.com", "brand_description": "Test description"}'
```

### Using Python

```python
import httpx

async def test_api():
    async with httpx.AsyncClient() as client:
        # Health check
        response = await client.get("http://localhost:8000/health")
        print(response.json())
        
        # Search brands
        response = await client.get("http://localhost:8000/api/brands/search?q=apple")
        print(response.json())
```

This API reference provides comprehensive documentation for all available endpoints in the Tunnelgrid.ai platform. 