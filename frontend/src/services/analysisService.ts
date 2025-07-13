/**
 * AI ANALYSIS SERVICE
 * 
 * PURPOSE: Frontend service for AI-powered brand analysis
 * 
 * FEATURES:
 * - Start AI analysis jobs
 * - Track analysis progress in real-time
 * - Retrieve analysis results
 * - Error handling and retry logic
 * - Type-safe API interactions
 */

// Configuration: API settings similar to other services
const API_CONFIG = {
  BASE_URL: import.meta.env.DEV ? '' : 'http://127.0.0.1:8000',  // Use proxy in dev, direct in prod
};

// =============================================================================
// TYPE DEFINITIONS
// =============================================================================

export interface AnalysisJobRequest {
  audit_id: string;
}

export interface AnalysisJobResponse {
  success: boolean;
  job_id: string;
  message: string;
  estimated_completion_time?: string;
  total_queries: number;
}

export interface AnalysisJobStatus {
  job_id: string;
  audit_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'partial_failure';
  total_queries: number;
  completed_queries: number;
  failed_queries: number;
  progress_percentage: number;
  estimated_time_remaining?: number;
  created_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface Citation {
  citation_id: string;
  response_id: string;
  citation_text: string;
  source_url?: string;
  extracted_at: string;
}

export interface BrandMention {
  mention_id: string;
  response_id: string;
  brand_name: string;
  mention_context: string;
  sentiment_score?: number;
  extracted_at: string;
}

export interface AnalysisResponse {
  response_id: string;
  query_id: string;
  model: string;
  response_text: string;
  processing_time_ms?: number;
  token_usage?: any;
  created_at: string;
  queries?: {
    audit_id: string;
    persona: string;
    query_text: string;
  };
}

export interface AnalysisResults {
  job_status: AnalysisJobStatus;
  total_responses: number;
  total_citations: number;
  total_brand_mentions: number;
  responses: AnalysisResponse[];
  citations: Citation[];
  brand_mentions: BrandMention[];
}

export interface AnalysisError {
  success: false;
  error: string;
  details?: string;
}

export type AnalysisServiceResult<T> = 
  | { success: true; data: T }
  | AnalysisError;

// =============================================================================
// ANALYSIS SERVICE CLASS
// =============================================================================

class AnalysisService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_CONFIG.BASE_URL}/api/analysis`;
  }

  /**
   * Start a new AI analysis job for an audit
   */
  async startAnalysis(auditId: string): Promise<AnalysisServiceResult<AnalysisJobResponse>> {
    try {
      console.log('🚀 Starting AI analysis for audit:', auditId);

      const response = await fetch(`${this.baseUrl}/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          audit_id: auditId
        } as AnalysisJobRequest),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: AnalysisJobResponse = await response.json();
      
      console.log('✅ Analysis job started:', data.job_id);
      console.log(`📊 Processing ${data.total_queries} queries`);

      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to start analysis:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        error: 'Failed to start analysis',
        details: errorMessage
      };
    }
  }

  /**
   * Get the current status of an analysis job
   */
  async getJobStatus(jobId: string): Promise<AnalysisServiceResult<AnalysisJobStatus>> {
    try {
      const response = await fetch(`${this.baseUrl}/status/${jobId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: AnalysisJobStatus = await response.json();
      
      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to get job status:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        error: 'Failed to get job status',
        details: errorMessage
      };
    }
  }

  /**
   * Get analysis results for a completed audit
   */
  async getResults(auditId: string): Promise<AnalysisServiceResult<AnalysisResults>> {
    try {
      console.log('📋 Fetching analysis results for audit:', auditId);

      const response = await fetch(`${this.baseUrl}/results/${auditId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: AnalysisResults = await response.json();
      
      console.log('✅ Analysis results retrieved');
      console.log(`📊 ${data.total_responses} responses, ${data.total_citations} citations, ${data.total_brand_mentions} brand mentions`);

      return { success: true, data };

    } catch (error) {
      console.error('❌ Failed to get analysis results:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        error: 'Failed to get analysis results',
        details: errorMessage
      };
    }
  }

  /**
   * Poll job status until completion
   * 
   * @param jobId - Analysis job ID
   * @param onProgress - Callback for progress updates
   * @param intervalMs - Polling interval in milliseconds (default: 3000)
   * @param timeoutMs - Maximum polling time (default: 10 minutes)
   */
  async pollJobStatus(
    jobId: string,
    onProgress?: (status: AnalysisJobStatus) => void,
    intervalMs: number = 3000,
    timeoutMs: number = 600000 // 10 minutes
  ): Promise<AnalysisServiceResult<AnalysisJobStatus>> {
    const startTime = Date.now();

    return new Promise((resolve) => {
      const poll = async () => {
        try {
          // Check timeout
          if (Date.now() - startTime > timeoutMs) {
            resolve({
              success: false,
              error: 'Polling timeout',
              details: 'Analysis is taking longer than expected'
            });
            return;
          }

          // Get current status
          const statusResult = await this.getJobStatus(jobId);
          
          if (!statusResult.success) {
            resolve(statusResult);
            return;
          }

          const status = statusResult.data;
          
          // Call progress callback
          if (onProgress) {
            onProgress(status);
          }

          // Check if job is complete
          if (status.status === 'completed' || status.status === 'partial_failure') {
            console.log('✅ Analysis job completed successfully');
            resolve({ success: true, data: status });
            return;
          }

          if (status.status === 'failed') {
            console.error('❌ Analysis job failed:', status.error_message);
            resolve({
              success: false,
              error: 'Analysis job failed',
              details: status.error_message || 'Unknown error'
            });
            return;
          }

          // Continue polling
          setTimeout(poll, intervalMs);

        } catch (error) {
          console.error('❌ Error during polling:', error);
          resolve({
            success: false,
            error: 'Polling error',
            details: error instanceof Error ? error.message : 'Unknown error'
          });
        }
      };

      // Start polling
      poll();
    });
  }

  /**
   * Complete analysis workflow: start job and poll until completion
   */
  async runCompleteAnalysis(
    auditId: string,
    onProgress?: (status: AnalysisJobStatus) => void
  ): Promise<AnalysisServiceResult<AnalysisResults>> {
    try {
      console.log('🔄 Starting complete analysis workflow for audit:', auditId);

      // Step 1: Start analysis job
      const startResult = await this.startAnalysis(auditId);
      if (!startResult.success) {
        const errorResult = startResult as AnalysisError;
        return {
          success: false,
          error: errorResult.error,
          details: errorResult.details
        };
      }

      const jobId = startResult.data.job_id;
      
      // Step 2: Poll until completion
      const pollResult = await this.pollJobStatus(jobId, onProgress);
      if (!pollResult.success) {
        const errorResult = pollResult as AnalysisError;
        return {
          success: false,
          error: errorResult.error,
          details: errorResult.details
        };
      }

      // Step 3: Get final results
      const resultsResult = await this.getResults(auditId);
      if (!resultsResult.success) {
        return resultsResult;
      }

      console.log('🎉 Complete analysis workflow finished successfully');
      return resultsResult;

    } catch (error) {
      console.error('❌ Complete analysis workflow failed:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        error: 'Complete analysis workflow failed',
        details: errorMessage
      };
    }
  }
}

// =============================================================================
// SERVICE INSTANCE & EXPORTS
// =============================================================================

export const analysisService = new AnalysisService();

// Helper functions for common operations
export const startAnalysis = (auditId: string) => analysisService.startAnalysis(auditId);
export const getJobStatus = (jobId: string) => analysisService.getJobStatus(jobId);
export const getAnalysisResults = (auditId: string) => analysisService.getResults(auditId);
export const runCompleteAnalysis = (auditId: string, onProgress?: (status: AnalysisJobStatus) => void) => 
  analysisService.runCompleteAnalysis(auditId, onProgress); 