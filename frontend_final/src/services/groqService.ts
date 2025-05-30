/**
 * TOPICS GENERATION SERVICE - SECURE BACKEND INTEGRATION
 * 
 * PURPOSE: Frontend service for AI-powered topics generation via secure backend
 * 
 * SECURITY BENEFITS:
 * - No API keys exposed in frontend code
 * - All AI calls routed through secure backend
 * - Rate limiting handled server-side
 * - Consistent error handling and fallbacks
 * 
 * ARCHITECTURE:
 * Frontend Service → Backend API → GroqCloud → Backend → Frontend
 */

import { Topic } from '../types/brandTypes';

// CONFIGURATION: Backend API settings
const API_CONFIG = {
  BASE_URL: import.meta.env.DEV ? '' : 'http://127.0.0.1:8000',  // Use proxy in dev, direct in prod
  ENDPOINTS: {
    GENERATE: '/api/topics/generate',
    FALLBACK: '/api/topics/fallback',
    HEALTH: '/api/topics/health'
  },
  TIMEOUT: 35000, // Slightly longer than backend timeout
};

// INTERFACES: API request/response types
export interface GenerateTopicsRequest {
  brandName: string;
  brandDomain: string;
  productName: string;
  industry?: string;
  additionalContext?: string;
}

export interface GenerateTopicsApiResponse {
  success: boolean;
  topics?: Topic[];
  source: 'ai' | 'fallback';
  processingTime?: number;
  tokenUsage?: number;
  reason?: string;
  error?: string;
}

interface GenerateTopicsResponse {
  success: boolean;
  topics: Topic[];
  source: 'ai' | 'fallback';
  processingTime: number;
  tokenUsage?: number;
  reason?: string;
}

interface HealthResponse {
  status: string;
  services: {
    groqapi: string;
    fallback: string;
  };
  timestamp: string;
}

/**
 * MAIN FUNCTION: Generate Topics via Backend
 * 
 * Calls secure backend API instead of directly calling GroqCloud
 */
export async function generateTopics(
  brandName: string,
  brandDomain: string,
  productName: string,
  industry?: string,
  additionalContext?: string
): Promise<Topic[]> {
  
  try {
    console.log('🤖 Requesting topics from backend API...');
    
    // Prepare request payload
    const requestPayload: GenerateTopicsRequest = {
      brandName: brandName.trim(),
      brandDomain: brandDomain.trim(),
      productName: productName.trim(),
      industry: industry?.trim() || undefined,
      additionalContext: additionalContext?.trim() || undefined
    };

    // Call backend API
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.GENERATE}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestPayload),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    // Handle response
    if (!response.ok) {
      // For non-2xx responses, try to get error details
      try {
        const errorData = await response.json();
        throw new Error(errorData.error || `Backend API error: ${response.status}`);
      } catch {
        throw new Error(`Backend API error: ${response.status}`);
      }
    }

    const data: GenerateTopicsResponse = await response.json();

    // Log results
    console.log(`✅ Topics received from backend:`, {
      source: data.source,
      count: data.topics.length,
      processingTime: data.processingTime,
      tokenUsage: data.tokenUsage,
      reason: data.reason
    });

    // Return topics (backend handles all fallback logic)
    return data.topics;

  } catch (error) {
    console.error('❌ Error calling backend topics API:', error);
    
    // Final fallback: Try to get fallback topics from backend
    try {
      console.log('🔄 Attempting to get fallback topics from backend...');
      
      const fallbackResponse = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.FALLBACK}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (fallbackResponse.ok) {
        const fallbackData: GenerateTopicsResponse = await fallbackResponse.json();
        console.log('✅ Retrieved fallback topics from backend');
        return fallbackData.topics;
      }
    } catch (fallbackError) {
      console.error('❌ Failed to get fallback topics from backend:', fallbackError);
    }
    
    // Ultimate fallback: Client-side fallback topics
    console.log('🔄 Using client-side fallback topics');
    return getClientFallbackTopics();
  }
}

/**
 * UTILITY FUNCTION: Check Backend Health
 * 
 * Verifies backend API and AI service availability
 */
export async function checkBackendHealth(): Promise<HealthResponse | null> {
  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.HEALTH}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (response.ok) {
      return await response.json();
    }

    return null;
  } catch (error) {
    console.error('❌ Backend health check failed:', error);
    return null;
  }
}

/**
 * ULTIMATE FALLBACK: Client-side topics
 * 
 * Used only when backend is completely unavailable
 */
function getClientFallbackTopics(): Topic[] {
  console.log('⚠️ Using ultimate client-side fallback topics');
  
  return [
    {
      id: "client-fallback-1",
      name: "Product Quality & Performance",
      description: "How consumers perceive the overall quality, reliability, and performance of the product"
    },
    {
      id: "client-fallback-2", 
      name: "Value for Money",
      description: "Consumer opinions on pricing, value proposition, and cost-effectiveness compared to alternatives"
    },
    {
      id: "client-fallback-3",
      name: "Brand Trust & Reputation", 
      description: "How the brand is perceived in terms of credibility, trustworthiness, and overall reputation"
    },
    {
      id: "client-fallback-4",
      name: "Customer Service Experience",
      description: "Consumer experiences with support, service quality, and problem resolution"
    },
    {
      id: "client-fallback-5",
      name: "User Experience & Usability",
      description: "How easy, intuitive, and satisfying the product is to use from a consumer perspective"
    },
    {
      id: "client-fallback-6",
      name: "Innovation & Features",
      description: "Consumer perception of the product's innovative aspects, features, and technological advancement"
    },
    {
      id: "client-fallback-7",
      name: "Social Responsibility",
      description: "How consumers view the brand's environmental impact, ethics, and social responsibility"
    },
    {
      id: "client-fallback-8",
      name: "Availability & Accessibility", 
      description: "Consumer experiences with product availability, distribution, and ease of purchase"
    },
    {
      id: "client-fallback-9",
      name: "Comparison with Competitors",
      description: "How consumers compare this product/brand to competitors and alternatives in the market"
    },
    {
      id: "client-fallback-10",
      name: "Long-term Satisfaction",
      description: "Consumer opinions on durability, long-term value, and continued satisfaction over time"
    }
  ];
} 