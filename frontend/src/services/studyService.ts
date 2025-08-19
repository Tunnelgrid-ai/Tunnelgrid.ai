/**
 * STUDY MANAGEMENT SERVICE
 * 
 * PURPOSE: Frontend service for study management and progress tracking
 * 
 * FEATURES:
 * - Create, read, update, delete studies
 * - Progress saving and restoration
 * - Study sharing and collaboration
 * - Templates for quick start
 * - Search and filtering
 * - Statistics and analytics
 */

// Configuration
const API_CONFIG = {
  BASE_URL: import.meta.env.DEV ? 'https://dazzling-smile-production.up.railway.app' : 'https://dazzling-smile-production.up.railway.app',
};

// =============================================================================
// TYPE DEFINITIONS
// =============================================================================

export interface Study {
  study_id: string;
  user_id: string;
  brand_id: string;
  product_id?: string;
  study_name: string;
  study_description?: string;
  current_step: StudyStep;
  progress_percentage: number;
  status: StudyStatus;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
  last_accessed_at: string;
  completed_at?: string;
  analysis_job_id?: string;
}

export enum StudyStep {
  BRAND_INFO = "brand_info",
  PERSONAS = "personas",
  PRODUCTS = "products",
  QUESTIONS = "questions",
  TOPICS = "topics",
  REVIEW = "review",
  ANALYSIS = "analysis",
  COMPLETED = "completed"
}

export enum StudyStatus {
  DRAFT = "draft",
  IN_PROGRESS = "in_progress",
  SETUP_COMPLETED = "setup_completed",
  ANALYSIS_RUNNING = "analysis_running",
  COMPLETED = "completed",
  FAILED = "failed"
}

export enum PermissionLevel {
  VIEW = "view",
  EDIT = "edit",
  ADMIN = "admin"
}

export interface StudyProgress {
  study_id: string;
  current_step: StudyStep;
  progress_percentage: number;
  step_data: Record<string, any>;
  last_updated: string;
}

export interface StudyShare {
  share_id: string;
  study_id: string;
  shared_by: string;
  shared_with_email: string;
  permission_level: PermissionLevel;
  created_at: string;
  expires_at?: string;
  is_active: boolean;
}

export interface StudyTemplate {
  template_id: string;
  template_name: string;
  template_description?: string;
  template_data: Record<string, any>;
  created_by?: string;
  is_public: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface StudyStats {
  total_studies: number;
  completed_studies: number;
  in_progress_studies: number;
  draft_studies: number;
  recent_studies: Study[];
}

export interface StudyListResponse {
  studies: Study[];
  total_count: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// =============================================================================
// STUDY SERVICE CLASS
// =============================================================================

class StudyService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_CONFIG.BASE_URL}/api/studies`;
  }

  // =============================================================================
  // STUDY CRUD OPERATIONS
  // =============================================================================

  /**
   * Create a new study
   */
  async createStudy(request: {
    brand_id: string;
    product_id?: string;
    study_name?: string;
    study_description?: string;
    template_id?: string;
  }): Promise<ApiResponse<Study>> {
    try {
      console.log('🚀 Creating new study:', request);

      const response = await fetch(`${this.baseUrl}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: Study = await response.json();
      
      console.log('✅ Study created successfully:', data.study_id);
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to create study:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * List user's studies with pagination
   */
  async listStudies(params: {
    page?: number;
    page_size?: number;
    status?: StudyStatus;
  } = {}): Promise<ApiResponse<StudyListResponse>> {
    try {
      console.log('📋 Listing studies with params:', params);

      const searchParams = new URLSearchParams();
      if (params.page) searchParams.append('page', params.page.toString());
      if (params.page_size) searchParams.append('page_size', params.page_size.toString());
      if (params.status) searchParams.append('status', params.status);

      const response = await fetch(`${this.baseUrl}/?${searchParams}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: StudyListResponse = await response.json();
      
      console.log(`✅ Retrieved ${data.studies.length} studies`);
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to list studies:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Get study details by ID
   */
  async getStudy(studyId: string): Promise<ApiResponse<Study>> {
    try {
      console.log('📖 Getting study:', studyId);

      const response = await fetch(`${this.baseUrl}/${studyId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: Study = await response.json();
      
      console.log('✅ Study retrieved successfully');
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to get study:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Update study metadata
   */
  async updateStudy(studyId: string, request: {
    study_name?: string;
    study_description?: string;
  }): Promise<ApiResponse<Study>> {
    try {
      console.log('✏️ Updating study:', studyId, request);

      const response = await fetch(`${this.baseUrl}/${studyId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: Study = await response.json();
      
      console.log('✅ Study updated successfully');
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to update study:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Delete study (soft delete)
   */
  async deleteStudy(studyId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      console.log('🗑️ Deleting study:', studyId);

      const response = await fetch(`${this.baseUrl}/${studyId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      console.log('✅ Study deleted successfully');
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to delete study:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  // =============================================================================
  // PROGRESS MANAGEMENT
  // =============================================================================

  /**
   * Save study progress for a specific step
   */
  async saveProgress(studyId: string, request: {
    step_name: StudyStep;
    step_data: Record<string, any>;
    progress_percentage: number;
  }): Promise<ApiResponse<StudyProgress>> {
    try {
      console.log('💾 Saving progress for study:', studyId, request.step_name);

      const response = await fetch(`${this.baseUrl}/${studyId}/progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: StudyProgress = await response.json();
      
      console.log('✅ Progress saved successfully');
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to save progress:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Get current study progress
   */
  async getProgress(studyId: string): Promise<ApiResponse<StudyProgress>> {
    try {
      console.log('📊 Getting progress for study:', studyId);

      const response = await fetch(`${this.baseUrl}/${studyId}/progress`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: StudyProgress = await response.json();
      
      console.log('✅ Progress retrieved successfully');
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to get progress:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  // =============================================================================
  // SHARING & COLLABORATION
  // =============================================================================

  /**
   * Share a study with another user
   */
  async shareStudy(studyId: string, request: {
    shared_with_email: string;
    permission_level?: PermissionLevel;
    expires_at?: string;
  }): Promise<ApiResponse<StudyShare>> {
    try {
      console.log('📤 Sharing study:', studyId, request.shared_with_email);

      const response = await fetch(`${this.baseUrl}/${studyId}/share`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: StudyShare = await response.json();
      
      console.log('✅ Study shared successfully');
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to share study:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * List all shares for a study
   */
  async listShares(studyId: string): Promise<ApiResponse<StudyShare[]>> {
    try {
      console.log('📋 Listing shares for study:', studyId);

      const response = await fetch(`${this.baseUrl}/${studyId}/shares`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: StudyShare[] = await response.json();
      
      console.log(`✅ Retrieved ${data.length} shares`);
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to list shares:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  // =============================================================================
  // STATISTICS & ANALYTICS
  // =============================================================================

  /**
   * Get study statistics for the user
   */
  async getStudyStats(): Promise<ApiResponse<StudyStats>> {
    try {
      console.log('📊 Getting study statistics');

      const response = await fetch(`${this.baseUrl}/stats/overview`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: StudyStats = await response.json();
      
      console.log('✅ Study statistics retrieved successfully');
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to get study stats:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  // =============================================================================
  // TEMPLATES
  // =============================================================================

  /**
   * Create a study template
   */
  async createTemplate(request: {
    template_name: string;
    template_description?: string;
    template_data: Record<string, any>;
    is_public?: boolean;
  }): Promise<ApiResponse<StudyTemplate>> {
    try {
      console.log('📝 Creating template:', request.template_name);

      const response = await fetch(`${this.baseUrl}/templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: StudyTemplate = await response.json();
      
      console.log('✅ Template created successfully');
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to create template:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * List available study templates
   */
  async listTemplates(publicOnly: boolean = true): Promise<ApiResponse<StudyTemplate[]>> {
    try {
      console.log('📋 Listing templates, public only:', publicOnly);

      const searchParams = new URLSearchParams();
      searchParams.append('public_only', publicOnly.toString());

      const response = await fetch(`${this.baseUrl}/templates?${searchParams}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: StudyTemplate[] = await response.json();
      
      console.log(`✅ Retrieved ${data.length} templates`);
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to list templates:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  /**
   * Calculate progress percentage based on current step
   */
  calculateProgressPercentage(currentStep: StudyStep): number {
    const stepProgress = {
      [StudyStep.BRAND_INFO]: 10,
      [StudyStep.PERSONAS]: 25,
      [StudyStep.PRODUCTS]: 40,
      [StudyStep.QUESTIONS]: 55,
      [StudyStep.TOPICS]: 70,
      [StudyStep.REVIEW]: 85,
      [StudyStep.ANALYSIS]: 95,
      [StudyStep.COMPLETED]: 100,
    };
    
    return stepProgress[currentStep] || 0;
  }

  /**
   * Get step display name
   */
  getStepDisplayName(step: StudyStep): string {
    const stepNames = {
      [StudyStep.BRAND_INFO]: 'Brand Information',
      [StudyStep.PERSONAS]: 'Personas',
      [StudyStep.PRODUCTS]: 'Products',
      [StudyStep.QUESTIONS]: 'Questions',
      [StudyStep.TOPICS]: 'Topics',
      [StudyStep.REVIEW]: 'Review',
      [StudyStep.ANALYSIS]: 'Analysis',
      [StudyStep.COMPLETED]: 'Completed',
    };
    
    return stepNames[step] || step;
  }

  /**
   * Get status display name
   */
  getStatusDisplayName(status: StudyStatus): string {
    const statusNames = {
      [StudyStatus.DRAFT]: 'Draft',
      [StudyStatus.IN_PROGRESS]: 'In Progress',
      [StudyStatus.SETUP_COMPLETED]: 'Setup Complete',
      [StudyStatus.ANALYSIS_RUNNING]: 'Analysis Running',
      [StudyStatus.COMPLETED]: 'Completed',
      [StudyStatus.FAILED]: 'Failed',
    };
    
    return statusNames[status] || status;
  }

  /**
   * Get status color for UI
   */
  getStatusColor(status: StudyStatus): string {
    const statusColors = {
      [StudyStatus.DRAFT]: 'bg-gray-100 text-gray-800',
      [StudyStatus.IN_PROGRESS]: 'bg-blue-100 text-blue-800',
      [StudyStatus.SETUP_COMPLETED]: 'bg-yellow-100 text-yellow-800',
      [StudyStatus.ANALYSIS_RUNNING]: 'bg-purple-100 text-purple-800',
      [StudyStatus.COMPLETED]: 'bg-green-100 text-green-800',
      [StudyStatus.FAILED]: 'bg-red-100 text-red-800',
    };
    
    return statusColors[status] || 'bg-gray-100 text-gray-800';
  }
}

// =============================================================================
// SERVICE INSTANCE & EXPORTS
// =============================================================================

export const studyService = new StudyService();

// Helper functions for common operations
export const createStudy = (request: Parameters<typeof studyService.createStudy>[0]) => 
  studyService.createStudy(request);

export const listStudies = (params?: Parameters<typeof studyService.listStudies>[0]) => 
  studyService.listStudies(params);

export const getStudy = (studyId: string) => studyService.getStudy(studyId);

export const updateStudy = (studyId: string, request: Parameters<typeof studyService.updateStudy>[1]) => 
  studyService.updateStudy(studyId, request);

export const deleteStudy = (studyId: string) => studyService.deleteStudy(studyId);

export const saveProgress = (studyId: string, request: Parameters<typeof studyService.saveProgress>[1]) => 
  studyService.saveProgress(studyId, request);

export const getProgress = (studyId: string) => studyService.getProgress(studyId);

export const shareStudy = (studyId: string, request: Parameters<typeof studyService.shareStudy>[1]) => 
  studyService.shareStudy(studyId, request);

export const listShares = (studyId: string) => studyService.listShares(studyId);

export const getStudyStats = () => studyService.getStudyStats();

export const createTemplate = (request: Parameters<typeof studyService.createTemplate>[0]) => 
  studyService.createTemplate(request);

export const listTemplates = (publicOnly?: boolean) => studyService.listTemplates(publicOnly);

// Export types and enums
export type { Study, StudyProgress, StudyShare, StudyTemplate, StudyStats, StudyListResponse, ApiResponse }; 