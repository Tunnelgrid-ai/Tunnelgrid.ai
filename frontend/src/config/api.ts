/**
 * API Configuration
 * Centralized configuration for all API endpoints
 */

export const API_CONFIG = {
  BASE_URL: 'https://dazzling-smile-production.up.railway.app',
  ENDPOINTS: {
    // Brand endpoints
    BRAND_SEARCH: '/api/brand-search',
    BRANDS_CREATE: '/api/brands/create',
    BRANDS_ANALYZE: '/api/brands/analyze',
    BRANDS_UPDATE: '/api/brands/update',
    
    // Audit endpoints
    AUDITS_CREATE: '/api/audits/create',
    AUDITS_MARK_SETUP_COMPLETE: '/api/audits',
    AUDITS_COMPLETE: '/api/audits/complete',
    
    // Analysis endpoints
    ANALYSIS_STATUS: '/api/analysis/status',
    ANALYSIS_START: '/api/analysis/start',
    ANALYSIS : '/api/analysis',
    ANALYSIS_RESULTS: '/api/analysis/results',
    ANALYSIS_COMPREHENSIVE_REPORT: '/api/analysis/comprehensive-report',
    
    // Topics endpoints
    TOPICS_GENERATE: '/api/topics/generate',
    TOPICS_FALLBACK: '/api/topics/fallback',
    TOPICS_HEALTH: '/api/topics/health',
    TOPICS_UPDATE: '/api/topics',
    
    // Questions endpoints
    QUESTIONS_GENERATE: '/api/questions/generate',
    QUESTIONS: '/api/questions',
    QUESTIONS_RETRY: '/api/questions/retry-failed-personas',
    
    // Studies endpoints
    STUDIES_CREATE: '/api/studies/create',
    STUDIES_GET: '/api/studies',
    
    // Strategic endpoints
    STRATEGIC_RECOMMENDATIONS: '/api/strategic/recommendations',
    
    // Products endpoints
    PRODUCTS_CREATE: '/api/products/create',
    
    // Personas endpoints
    PERSONAS_CREATE: '/api/personas/create',
    PERSONAS_GET: '/api/personas',
    PERSONAS_GENERATE: '/api/personas/generate',
    PERSONAS_STORE: '/api/personas/store',
    PERSONAS_UPDATE: '/api/personas',
    PERSONAS_BY_AUDIT: '/api/personas/by-audit',
    PERSONAS_FALLBACK: '/api/personas/fallback',
  }
};

/**
 * Helper function to build full API URLs
 */
export const buildApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

/**
 * Helper function to get endpoint URL
 */
export const getApiUrl = (endpointKey: keyof typeof API_CONFIG.ENDPOINTS): string => {
  return buildApiUrl(API_CONFIG.ENDPOINTS[endpointKey]);
};
