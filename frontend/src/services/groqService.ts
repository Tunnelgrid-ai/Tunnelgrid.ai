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
import { getApiUrl } from '@/config/api';

// TIMEOUT configuration
const TIMEOUT = 35000; // Slightly longer than backend timeout

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
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT);

    const response = await fetch(getApiUrl('TOPICS_GENERATE'), {
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
      
      const fallbackResponse = await fetch(getApiUrl('TOPICS_FALLBACK'), {
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
    const response = await fetch(getApiUrl('TOPICS_HEALTH'), {
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
 * Ensures proper category distribution: 4 unbranded, 3 branded, 3 comparative
 */
function getClientFallbackTopics(): Topic[] {
  console.log('⚠️ Using ultimate client-side fallback topics');
  
  return [
    // Unbranded Topics (4)
    {
      id: "client-fallback-unbranded-1",
      name: "Best Industry Solutions",
      description: "General recommendations where brands might be mentioned naturally",
      category: "unbranded"
    },
    {
      id: "client-fallback-unbranded-2", 
      name: "Top Platform Reviews",
      description: "User experiences with leading platforms in the space",
      category: "unbranded"
    },
    {
      id: "client-fallback-unbranded-3",
      name: "Popular Service Comparisons", 
      description: "Consumer discussions comparing different service options",
      category: "unbranded"
    },
    {
      id: "client-fallback-unbranded-4",
      name: "Market Leader Analysis",
      description: "Analysis of top performers in the industry",
      category: "unbranded"
    },
    // Branded Topics (3)
    {
      id: "client-fallback-branded-1",
      name: "Brand User Experience",
      description: "Direct feedback and opinions about the brand",
      category: "branded"
    },
    {
      id: "client-fallback-branded-2",
      name: "Brand Service Quality",
      description: "Assessment of brand's service quality and reliability",
      category: "branded"
    },
    {
      id: "client-fallback-branded-3",
      name: "Brand Value Proposition",
      description: "Discussion of brand's unique benefits and value",
      category: "branded"
    },
    // Comparative Topics (3)
    {
      id: "client-fallback-comparative-1",
      name: "Brand vs Competitors",
      description: "Direct comparisons between brand and market alternatives",
      category: "comparative"
    },
    {
      id: "client-fallback-comparative-2",
      name: "Feature Comparison",
      description: "Comparing specific features and capabilities with rivals",
      category: "comparative"
    },
    {
      id: "client-fallback-comparative-3",
      name: "Market Position Analysis",
      description: "How brand ranks against industry competitors",
      category: "comparative"
    }
  ];
} 