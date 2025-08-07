"""
Configuration Management for AI Brand Analysis API

This module centralizes all configuration settings including:
- Environment variables
- API keys
- Database settings
- Service configurations
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in the project root (parent directory of backend)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

class Settings:
    """Application settings and configuration"""
    
    # Application metadata
    APP_NAME: str = "AI Brand Analysis API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Secure backend API for AI-powered consumer brand analysis"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database configuration (Supabase)
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # External API keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    LOGODEV_SECRET_KEY: Optional[str] = os.getenv("LOGODEV_SECRET_KEY")
    
    # AI Model configuration - groq
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "8000"))
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
    GROQ_TIMEOUT: float = float(os.getenv("GROQ_TIMEOUT", "60.0"))

    # AI model configuration - openai search models
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_SEARCH_MODEL: str = os.getenv("OPENAI_SEARCH_MODEL", "gpt-4o-search-preview")
    OPENAI_SEARCH_MAX_TOKENS: int = int(os.getenv("OPENAI_SEARCH_MAX_TOKENS", "8000"))
    OPENAI_SEARCH_TEMPERATURE: float = float(os.getenv("OPENAI_SEARCH_TEMPERATURE", "0.7"))
    OPENAI_SEARCH_TIMEOUT: float = float(os.getenv("OPENAI_SEARCH_TIMEOUT", "60.0"))

    # OpenAI Responses API configuration
    OPENAI_RESPONSES_MODEL: str = os.getenv("OPENAI_RESPONSES_MODEL", "gpt-4o")
    OPENAI_WEB_SEARCH_TOOL_VERSION: str = os.getenv("OPENAI_WEB_SEARCH_TOOL_VERSION", "web_search")
    OPENAI_SEARCH_CONTEXT_SIZE: str = os.getenv("OPENAI_SEARCH_CONTEXT_SIZE", "medium")

    # Web search options configuration
    OPENAI_SEARCH_USER_LOCATION_COUNTRY: Optional[str] = os.getenv("OPENAI_SEARCH_USER_LOCATION_COUNTRY", "US")
    OPENAI_SEARCH_USER_LOCATION_CITY: Optional[str] = os.getenv("OPENAI_SEARCH_USER_LOCATION_CITY")

    # CORS configuration
    CORS_ORIGINS: list = [
        "http://localhost:3000",    # React dev server
        "http://localhost:8080",    # Alternative dev port
        "http://localhost:8081",    # Vite dev server
        "http://localhost:8082",    # Vite dev server (fallback port)
        "http://localhost:8083",    # Vite dev server (fallback port)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080", 
        "http://127.0.0.1:8081",
        "http://127.0.0.1:8082",    # Fallback port
        "http://127.0.0.1:8083",    # Fallback port
        # Add production domains here
    ]
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
    RATE_LIMIT_PERIOD: str = os.getenv("RATE_LIMIT_PERIOD", "15minutes")
    
    # Security
    TRUSTED_HOSTS: list = ["*"]  # Configure properly for production
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def has_supabase_config(self) -> bool:
        """Check if Supabase is properly configured"""
        return bool(self.SUPABASE_URL and self.SUPABASE_SERVICE_ROLE_KEY)
    
    @property
    def has_groq_config(self) -> bool:
        """Check if Groq API is properly configured"""
        return bool(self.GROQ_API_KEY)
    
    @property
    def has_logodev_config(self) -> bool:
        """Check if Logo.dev API is properly configured"""
        return bool(self.LOGODEV_SECRET_KEY)
    
    @property
    def has_openai_config(self) -> bool:
        """Check if OpenAI API is properly configured"""
        return bool(self.OPENAI_API_KEY)
    
    @property
    def has_openai_websearch_config(self) -> bool:
        """Check if OpenAI web search is properly configured"""
        return bool(self.OPENAI_API_KEY and self.OPENAI_RESPONSES_MODEL)

# Global settings instance
settings = Settings()

# Validation function
def validate_configuration():
    """Validate that required configuration is present"""
    missing_config = []
    
    if not settings.has_supabase_config:
        missing_config.append("Supabase (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)")
    
    if not settings.has_groq_config:
        missing_config.append("Groq API (GROQ_API_KEY)")
    
    if not settings.has_logodev_config:
        missing_config.append("Logo.dev API (LOGODEV_SECRET_KEY)")

    if not settings.has_openai_config:
        missing_config.append("OpenAI API (OPENAI_API_KEY)")
    
    if missing_config:
        raise ValueError(f"Missing required configuration: {', '.join(missing_config)}")
    
    return True 