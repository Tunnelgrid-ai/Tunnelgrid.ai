/**
 * PERSONAS SERVICE - Frontend API integration for personas generation
 * 
 * PURPOSE: Handle all API interactions related to personas generation and storage
 * 
 * FEATURES:
 * - Generate personas using AI
 * - Store personas in database
 * - Retrieve personas by audit ID
 * - Fallback personas for offline/error scenarios
 */

import type { Persona } from '@/types/brandTypes';

const API_BASE_URL = 'https://dazzling-smile-production.up.railway.app/api';

// Request/Response types matching backend models
export interface PersonaGenerateRequest {
  brandName: string;
  brandDescription: string;
  brandDomain: string;
  productName: string;
  brandId: string;
  productId: string;
  topics: string[];
  industry?: string;
  additionalContext?: string;
  auditId?: string;
}

export interface Demographics {
  ageRange?: string;
  gender?: string;
  location?: string;
  goals?: string[];
}

export interface PersonaResponse {
  id: string;
  name: string;
  description: string;
  painPoints: string[];
  motivators: string[];
  demographics?: Demographics;
  topicId?: string;
  productId?: string;
}

export interface PersonasApiResponse {
  success: boolean;
  personas: PersonaResponse[];
  source: string;
  processingTime: number;
  tokenUsage?: number;
  reason?: string;
}

export interface PersonaStoreRequest {
  auditId: string;
  brandId?: string;
  personas: PersonaResponse[];
}

export interface PersonaStoreResponse {
  success: boolean;
  storedCount: number;
  message: string;
  errors?: string[];
}

export interface PersonaUpdateRequest {
  name?: string;
  description?: string;
  painPoints?: string[];
  motivators?: string[];
  demographics?: Demographics;
}

export interface PersonaUpdateResponse {
  success: boolean;
  message: string;
  persona?: PersonaResponse;
  errors?: string[];
}

/**
 * Generate personas using AI based on brand and product information
 */
export async function generatePersonas(request: PersonaGenerateRequest): Promise<PersonasApiResponse> {
  try {
    console.log('🚀 Generating personas with request:', request);

    const response = await fetch(`${API_BASE_URL}/personas/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      
      // Handle FastAPI validation errors properly
      let errorMessage = 'Unknown error';
      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          // FastAPI validation errors are arrays
          errorMessage = errorData.detail.map((err: any) => 
            `${err.loc?.join('.') || 'field'}: ${err.msg}`
          ).join(', ');
        } else {
          errorMessage = errorData.detail;
        }
      }
      
      throw new Error(`API Error: ${response.status} - ${errorMessage}`);
    }

    const data: PersonasApiResponse = await response.json();
    
    console.log('✅ Personas generated successfully:', {
      count: data.personas.length,
      source: data.source,
      processingTime: data.processingTime
    });

    return data;

  } catch (error) {
    console.error('❌ Error generating personas:', error);
    
    // Return fallback response on error
    return {
      success: false,
      personas: [],
      source: 'error',
      processingTime: 0,
      reason: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Store generated personas in the database
 */
export async function storePersonas(request: PersonaStoreRequest): Promise<PersonaStoreResponse> {
  try {
    console.log('💾 Storing personas:', { auditId: request.auditId, count: request.personas.length });

    const response = await fetch(`${API_BASE_URL}/personas/store`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      
      // Handle FastAPI validation errors properly
      let errorMessage = 'Unknown error';
      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          // FastAPI validation errors are arrays
          errorMessage = errorData.detail.map((err: any) => 
            `${err.loc?.join('.') || 'field'}: ${err.msg}`
          ).join(', ');
        } else {
          errorMessage = errorData.detail;
        }
      }
      
      throw new Error(`API Error: ${response.status} - ${errorMessage}`);
    }

    const data: PersonaStoreResponse = await response.json();
    
    console.log('✅ Personas stored successfully:', {
      storedCount: data.storedCount,
      message: data.message
    });

    return data;

  } catch (error) {
    console.error('❌ Error storing personas:', error);
    
    return {
      success: false,
      storedCount: 0,
      message: error instanceof Error ? error.message : 'Unknown error storing personas'
    };
  }
}

/**
 * Update a specific persona
 */
export async function updatePersona(personaId: string, updates: PersonaUpdateRequest): Promise<PersonaUpdateResponse> {
  try {
    console.log('📝 Updating persona:', personaId, updates);

    const response = await fetch(`${API_BASE_URL}/personas/${personaId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      
      // Handle FastAPI validation errors properly
      let errorMessage = 'Unknown error';
      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          // FastAPI validation errors are arrays
          errorMessage = errorData.detail.map((err: any) => 
            `${err.loc?.join('.') || 'field'}: ${err.msg}`
          ).join(', ');
        } else {
          errorMessage = errorData.detail;
        }
      }
      
      throw new Error(`Persona update failed: ${errorMessage}`);
    }

    const data: PersonaUpdateResponse = await response.json();
    
    if (!data.success) {
      throw new Error(data.message || 'Persona update failed');
    }
    
    console.log(`✅ Updated persona successfully:`, data.persona);
    return data;
    
  } catch (error) {
    console.error('❌ Persona update failed:', error);
    throw error;
  }
}

/**
 * Get personas associated with a specific audit
 */
export async function getPersonasByAudit(auditId: string): Promise<PersonasApiResponse> {
  try {
    console.log('📥 Retrieving personas for audit:', auditId);

    const response = await fetch(`${API_BASE_URL}/personas/by-audit/${auditId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      
      // Handle FastAPI validation errors properly
      let errorMessage = 'Unknown error';
      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          // FastAPI validation errors are arrays
          errorMessage = errorData.detail.map((err: any) => 
            `${err.loc?.join('.') || 'field'}: ${err.msg}`
          ).join(', ');
        } else {
          errorMessage = errorData.detail;
        }
      }
      
      throw new Error(`API Error: ${response.status} - ${errorMessage}`);
    }

    const data: PersonasApiResponse = await response.json();
    
    console.log('✅ Personas retrieved successfully:', {
      count: data.personas.length,
      source: data.source
    });

    return data;

  } catch (error) {
    console.error('❌ Error retrieving personas:', error);
    
    return {
      success: false,
      personas: [],
      source: 'error',
      processingTime: 0,
      reason: error instanceof Error ? error.message : 'Unknown error retrieving personas'
    };
  }
}

/**
 * Get fallback personas (for testing or when AI is unavailable)
 */
export async function getFallbackPersonas(): Promise<PersonasApiResponse> {
  try {
    console.log('🔄 Getting fallback personas');

    const response = await fetch(`${API_BASE_URL}/personas/fallback`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      
      // Handle FastAPI validation errors properly
      let errorMessage = 'Unknown error';
      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          // FastAPI validation errors are arrays
          errorMessage = errorData.detail.map((err: any) => 
            `${err.loc?.join('.') || 'field'}: ${err.msg}`
          ).join(', ');
        } else {
          errorMessage = errorData.detail;
        }
      }
      
      throw new Error(`API Error: ${response.status} - ${errorMessage}`);
    }

    const data: PersonasApiResponse = await response.json();
    
    console.log('✅ Fallback personas retrieved:', { count: data.personas.length });

    return data;

  } catch (error) {
    console.error('❌ Error getting fallback personas:', error);
    
    // Return hardcoded fallback as last resort
    return {
      success: true,
      personas: [
        {
          id: 'fallback-1',
          name: 'Tech Professional',
          description: 'Technology professionals who are looking for advanced solutions to improve workflow efficiency.',
          painPoints: ['Limited time for research', 'Complex integration requirements', 'Need for reliable support'],
          motivators: ['Productivity improvements', 'Time savings', 'Cutting-edge features'],
          demographics: {
            ageRange: '28-45',
            gender: 'All genders',
            location: 'Urban areas',
            goals: ['Streamline workflows', 'Reduce overhead costs']
          }
        },
        {
          id: 'fallback-2', 
          name: 'Small Business Owner',
          description: 'Entrepreneurs and small business owners seeking cost-effective solutions.',
          painPoints: ['Budget constraints', 'Limited technical knowledge', 'Need for simple solutions'],
          motivators: ['Cost savings', 'Easy implementation', 'Growth opportunities'],
          demographics: {
            ageRange: '30-55',
            gender: 'All genders',
            location: 'Nationwide',
            goals: ['Expand customer base', 'Optimize operations']
          }
        },
        {
          id: 'fallback-3',
          name: 'Creative Professional',
          description: 'Designers, writers, and content creators who need tools to enhance their creative output.',
          painPoints: ['Deadline pressures', 'Need for inspiration', 'Technical limitations'],
          motivators: ['Enhanced creative freedom', 'Collaboration features', 'Portfolio showcase options'],
          demographics: {
            ageRange: '25-40',
            gender: 'All genders',
            location: 'Urban creative hubs',
            goals: ['Improve creative output', 'Find new clients']
          }
        }
      ],
      source: 'hardcoded-fallback',
      processingTime: 0
    };
  }
}

/**
 * Convert API persona response to frontend Persona type
 */
export function convertToFrontendPersona(apiPersona: PersonaResponse): Persona {
  return {
    id: apiPersona.id,
    name: apiPersona.name,
    description: apiPersona.description,
    painPoints: apiPersona.painPoints,
    motivators: apiPersona.motivators,
    demographics: apiPersona.demographics ? {
      ageRange: apiPersona.demographics.ageRange,
      gender: apiPersona.demographics.gender,
      location: apiPersona.demographics.location,
      goals: apiPersona.demographics.goals
    } : undefined,
    topicId: apiPersona.topicId,
    productId: apiPersona.productId
  };
}

/**
 * Convert frontend Persona type to API persona format
 */
export function convertToApiPersona(frontendPersona: Persona): PersonaResponse {
  return {
    id: frontendPersona.id || '',
    name: frontendPersona.name,
    description: frontendPersona.description,
    painPoints: frontendPersona.painPoints,
    motivators: frontendPersona.motivators,
    demographics: frontendPersona.demographics ? {
      ageRange: frontendPersona.demographics.ageRange,
      gender: frontendPersona.demographics.gender,
      location: frontendPersona.demographics.location,
      goals: frontendPersona.demographics.goals
    } : undefined,
    topicId: frontendPersona.topicId,
    productId: frontendPersona.productId
  };
} 