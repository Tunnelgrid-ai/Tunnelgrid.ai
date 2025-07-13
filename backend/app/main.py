"""
AI BRAND ANALYSIS - CONSOLIDATED FASTAPI BACKEND

PURPOSE: Unified backend API for AI-powered brand analysis platform

FEATURES:
- Brand search via Logo.dev API
- AI-powered brand analysis via GroqCloud  
- AI-powered topics generation via GroqCloud
- Product and audit management
- Supabase database integration
- Rate limiting and security
- CORS configuration for frontend
- Comprehensive error handling
- Centralized configuration management

ARCHITECTURE:
Frontend (React) → FastAPI Backend → (Logo.dev/GroqCloud/Supabase) → Backend → Frontend
"""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import logging

# Import core modules
from .core.config import settings, validate_configuration
from .core.database import test_database_connection
from .models.common import HealthResponse

# Import route modules
from .routes.topics import router as topics_router, limiter
from .routes.brands import router as brands_router
from .routes.products import router as products_router
from .routes.audits import router as audits_router
from .routes.personas import router as personas_router
from .routes.questions import router as questions_router
from .routes.analysis import router as analysis_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LIFESPAN: Application startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management with enhanced startup checks
    """
    # Startup
    logger.info("🚀 AI Brand Analysis Backend starting up...")
    logger.info(f"📍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🏠 Host: {settings.HOST}:{settings.PORT}")
    
    # Configuration validation
    try:
        validate_configuration()
        logger.info("✅ Configuration validation passed")
    except ValueError as e:
        logger.warning(f"⚠️ Configuration warning: {e}")
    
    # Service status checks
    services_status = {
        "supabase": "✅ Available" if settings.has_supabase_config else "❌ Not configured",
        "groqcloud": "✅ Available" if settings.has_groq_config else "❌ Not configured", 
        "logodev": "✅ Available" if settings.has_logodev_config else "❌ Not configured",
        "openai_search": "✅ Available" if settings.has_openai_config else "❌ Not configured"
    }
    
    for service, status in services_status.items():
        logger.info(f"🔗 {service.title()}: {status}")
    
    # Test database connection
    if settings.has_supabase_config:
        db_connected = test_database_connection()
        if db_connected:
            logger.info("✅ Database connection successful")
        else:
            logger.warning("⚠️ Database connection failed")
    
    logger.info("🎯 All services initialized. Ready to serve requests!")
    
    yield
    
    # Shutdown  
    logger.info("🛑 AI Brand Analysis Backend shutting down...")

# CREATE FASTAPI APP
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# SECURITY MIDDLEWARE
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.TRUSTED_HOSTS
)

# CORS MIDDLEWARE: Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# RATE LIMITING: Global setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ROUTES: Include API routes with proper prefixes
app.include_router(
    topics_router, 
    prefix="/api/topics", 
    tags=["topics"]
)

app.include_router(
    brands_router,
    prefix="/api/brands",
    tags=["brands"]
)

app.include_router(
    products_router,
    prefix="/api/products", 
    tags=["products"]
)

app.include_router(
    audits_router,
    prefix="/api/audits",
    tags=["audits"]
)

app.include_router(
    personas_router,
    prefix="/api/personas",
    tags=["personas"]
)

app.include_router(
    questions_router,
    prefix="/api/questions",
    tags=["questions"]
)

app.include_router(
    analysis_router,
    prefix="/api/analysis",
    tags=["analysis"]
)

# ROOT ENDPOINT
@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": settings.APP_NAME,
        "status": "running",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "endpoints": {
            "topics": "/api/topics",
            "brands": "/api/brands", 
            "products": "/api/products",
            "audits": "/api/audits",
            "personas": "/api/personas",
            "questions": "/api/questions",
            "analysis": "/api/analysis"
        }
    }

# HEALTH CHECK ENDPOINT  
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Global health check endpoint with service status
    """
    services = {
        "api": "running",
        "supabase": "available" if settings.has_supabase_config else "unavailable",
        "groqcloud": "available" if settings.has_groq_config else "unavailable",
        "logodev": "available" if settings.has_logodev_config else "unavailable",
        "openai_search": "available" if settings.has_openai_config else "unavailable"
    }
    
    return HealthResponse(
        status="healthy",
        services=services,
        timestamp=datetime.utcnow().isoformat(),
        environment=settings.ENVIRONMENT
    )

# LEGACY ENDPOINTS: For backward compatibility
@app.get("/test-supabase")
async def test_supabase():
    """
    Legacy endpoint for testing Supabase connection
    """
    try:
        from .core.database import get_supabase_client
        supabase = get_supabase_client()
        data = supabase.table("brand").select("*").limit(5).execute()
        return {"status": "success", "data": data.data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Brand search legacy endpoint
@app.get("/api/brand-search")
async def legacy_brand_search(q: str):
    """Legacy brand search endpoint - redirects to new structure"""
    from .routes.brands import search_brands
    return await search_brands(q)

# Brand creation legacy endpoints  
@app.post("/api/insert-brand")
async def legacy_insert_brand(request: Request):
    """Legacy brand insert endpoint - redirects to new structure"""
    from .routes.brands import create_brand
    from .models.brands import BrandInsertRequest
    
    data = await request.json()
    brand_request = BrandInsertRequest(
        brand_name=data.get("brand_name"),
        domain=data.get("domain"),
        brand_description=data.get("brand_description")
    )
    return await create_brand(brand_request)

@app.post("/api/brand-llama")
async def legacy_brand_llama(request: Request):
    """Legacy brand analysis endpoint - redirects to new structure"""
    from .routes.brands import analyze_brand
    from .models.brands import BrandLlamaRequest
    
    data = await request.json()
    brand_request = BrandLlamaRequest(
        brand_name=data.get("brand_name"),
        domain=data.get("domain")
    )
    return await analyze_brand(brand_request)

@app.post("/api/update-brand-product")
async def legacy_update_brand_product(request: Request):
    """Legacy brand update endpoint - redirects to new structure"""
    from .routes.brands import update_brand_with_products
    from .models.brands import BrandUpdateRequest
    
    data = await request.json()
    update_request = BrandUpdateRequest(
        brand_name=data.get("brand_name"),
        brand_description=data.get("brand_description"),
        product=data.get("product", [])
    )
    return await update_brand_with_products(update_request)

@app.post("/api/create-product")
async def legacy_create_product(request: Request):
    """Legacy product creation endpoint - redirects to new structure"""
    from .routes.products import create_product
    from .models.products import ProductCreateRequest
    
    data = await request.json()
    product_request = ProductCreateRequest(
        brand_id=data.get("brand_id"),
        product_name=data.get("product_name")
    )
    return await create_product(product_request)

@app.post("/api/create-audit")
async def legacy_create_audit(request: Request):
    """Legacy audit creation endpoint - redirects to new structure"""
    from .routes.audits import create_audit
    from .models.audits import AuditCreateRequest
    
    data = await request.json()
    audit_request = AuditCreateRequest(
        brand_id=data.get("brand_id"),
        product_id=data.get("product_id"),
        user_id=data.get("user_id")
    )
    return await create_audit(audit_request)

# ERROR HANDLERS
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """
    Custom 404 handler
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found", 
            "detail": f"Path {request.url.path} not found",
            "available_endpoints": [
                "/api/topics", "/api/brands", "/api/products", "/api/audits", "/api/personas", "/api/questions",
                "/health", "/docs"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """
    Custom 500 handler
    """
    logger.error(f"Internal server error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error", 
            "detail": "Something went wrong. Please try again later."
        }
    )

# DEVELOPMENT SERVER
if __name__ == "__main__":
    # Development configuration
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 