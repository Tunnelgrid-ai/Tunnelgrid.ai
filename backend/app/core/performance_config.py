"""
Performance Configuration for AI Analysis

This module contains configurable settings for optimizing the performance
of AI analysis operations, including batch sizes, delays, and concurrency limits.
"""

import os
from typing import Optional

class PerformanceConfig:
    """Configuration for analysis performance optimization"""
    
    # Batch processing settings
    ANALYSIS_BATCH_SIZE = int(os.getenv('ANALYSIS_BATCH_SIZE', '10'))
    BATCH_DELAY_SECONDS = float(os.getenv('BATCH_DELAY_SECONDS', '0.5'))
    
    # Concurrency settings
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '20'))
    
    # Rate limiting settings
    REQUESTS_PER_MINUTE = int(os.getenv('REQUESTS_PER_MINUTE', '60'))
    
    # Timeout settings
    REQUEST_TIMEOUT_SECONDS = int(os.getenv('REQUEST_TIMEOUT_SECONDS', '30'))
    
    # Retry settings
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY_SECONDS = float(os.getenv('RETRY_DELAY_SECONDS', '1.0'))
    
    @classmethod
    def get_optimal_batch_size(cls, total_queries: int) -> int:
        """Calculate optimal batch size based on total queries"""
        if total_queries <= 10:
            return min(total_queries, cls.ANALYSIS_BATCH_SIZE)
        elif total_queries <= 50:
            return min(15, cls.ANALYSIS_BATCH_SIZE)
        else:
            return cls.ANALYSIS_BATCH_SIZE
    
    @classmethod
    def get_batch_delay(cls, batch_number: int, total_batches: int) -> float:
        """Calculate delay between batches (can be dynamic)"""
        # Reduce delay for later batches to speed up processing
        if batch_number > total_batches * 0.7:  # Last 30% of batches
            return cls.BATCH_DELAY_SECONDS * 0.5
        return cls.BATCH_DELAY_SECONDS
    
    @classmethod
    def print_config(cls):
        """Print current performance configuration"""
        print("🚀 Performance Configuration:")
        print(f"   Batch Size: {cls.ANALYSIS_BATCH_SIZE}")
        print(f"   Batch Delay: {cls.BATCH_DELAY_SECONDS}s")
        print(f"   Max Concurrent: {cls.MAX_CONCURRENT_REQUESTS}")
        print(f"   Requests/Min: {cls.REQUESTS_PER_MINUTE}")
        print(f"   Timeout: {cls.REQUEST_TIMEOUT_SECONDS}s")
        print(f"   Max Retries: {cls.MAX_RETRIES}")

# Environment variable documentation
"""
Environment Variables for Performance Tuning:

ANALYSIS_BATCH_SIZE: Number of concurrent API calls per batch (default: 10)
BATCH_DELAY_SECONDS: Delay between batches in seconds (default: 0.5)
MAX_CONCURRENT_REQUESTS: Maximum concurrent requests (default: 20)
REQUESTS_PER_MINUTE: Rate limit for API calls (default: 60)
REQUEST_TIMEOUT_SECONDS: Timeout for individual requests (default: 30)
MAX_RETRIES: Maximum retry attempts for failed requests (default: 3)
RETRY_DELAY_SECONDS: Delay between retries (default: 1.0)

Example usage:
export ANALYSIS_BATCH_SIZE=15
export BATCH_DELAY_SECONDS=0.3
export MAX_CONCURRENT_REQUESTS=25
""" 