"""
Database client setup and management

This module provides a centralized Supabase client instance
for database operations across the application.
"""

from supabase import create_client, Client
from typing import Optional
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Global Supabase client instance
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Get or create the Supabase client instance.
    
    Returns:
        Client: Configured Supabase client
        
    Raises:
        ValueError: If Supabase configuration is missing
    """
    global _supabase_client
    
    if _supabase_client is None:
        if not settings.has_supabase_config:
            raise ValueError(
                "Supabase configuration missing. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY"
            )
        
        try:
            _supabase_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
            logger.info("✅ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    return _supabase_client

def test_database_connection() -> bool:
    """
    Test the database connection by performing a simple query.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        client = get_supabase_client()
        # Simple test query - check if we can connect
        result = client.table("brand").select("brand_id").limit(1).execute()
        logger.info("✅ Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

# Convenience alias for the client
supabase = get_supabase_client 