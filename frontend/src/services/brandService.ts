/**
 * BRAND SERVICE - Frontend API integration for brand operations
 * 
 * PURPOSE: Handle all API interactions related to brand management
 * 
 * FEATURES:
 * - Update brand descriptions
 * - Consistent error handling
 * - TypeScript type safety
 */

import { getApiUrl } from '@/config/api';

// Request/Response types matching backend models
export interface BrandDescriptionUpdateRequest {
  description: string;
}

export interface BrandDescriptionUpdateResponse {
  success: boolean;
  message: string;
  brand_id?: string;
}

class BrandService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = getApiUrl('BRANDS_CREATE').replace('/create', '');
  }

  /**
   * Update brand description
   */
  async updateBrandDescription(brandId: string, description: string): Promise<BrandDescriptionUpdateResponse> {
    try {
      console.log('📝 Updating brand description:', brandId, description.substring(0, 50) + '...');
      
      const updateRequest: BrandDescriptionUpdateRequest = {
        description: description.trim()
      };
      
      const response = await fetch(`${this.baseUrl}/${brandId}/description`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateRequest),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(`API error: ${response.status} - ${errorData.detail || 'Brand description update failed'}`);
      }

      const data: BrandDescriptionUpdateResponse = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Brand description update failed');
      }
      
      console.log(`✅ Updated brand description successfully for brand ${brandId}`);

      return data;
    } catch (error) {
      console.error('❌ Brand description update failed:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const brandService = new BrandService();

// Export default for compatibility
export default brandService;