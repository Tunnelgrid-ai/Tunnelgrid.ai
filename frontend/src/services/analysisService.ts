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
   * Start analysis and return job ID immediately (for loading screen)
   */
  async startAnalysisJob(
    auditId: string
  ): Promise<AnalysisServiceResult<{ job_id: string; total_queries: number }>> {
    try {
      console.log('🚀 Starting analysis job for audit:', auditId);

      const startResult = await this.startAnalysis(auditId);
      if (!startResult.success) {
        const errorResult = startResult as AnalysisError;
        return {
          success: false,
          error: errorResult.error,
          details: errorResult.details
        };
      }

      console.log('✅ Analysis job started successfully');
      return {
        success: true,
        data: {
          job_id: startResult.data.job_id,
          total_queries: startResult.data.total_queries
        }
      };

    } catch (error) {
      console.error('❌ Failed to start analysis job:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        error: 'Failed to start analysis job',
        details: errorMessage
      };
    }
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

  /**
   * Generate comprehensive report data from analysis results
   */
  async getComprehensiveReport(auditId: string): Promise<AnalysisServiceResult<any>> {
    try {
      console.log('📊 Generating comprehensive report for audit:', auditId);

      // Get analysis results
      const resultsResult = await this.getResults(auditId);
      if (!resultsResult.success) {
        return resultsResult;
      }

      const results = resultsResult.data;
      
      // Process data into comprehensive report format
      const reportData = {
        reportInfo: {
          id: auditId,
          brandName: "Your Brand", // This should come from audit data
          analysisDate: new Date().toISOString().split('T')[0],
          totalQueries: results.job_status.total_queries,
          totalResponses: results.total_responses,
        },
        brandVisibility: this.processBrandVisibility(results),
        brandReach: this.processBrandReach(results),
        topicMatrix: this.processTopicMatrix(results),
        modelVisibility: this.processModelVisibility(results),
        sources: this.processSources(results),
      };

      console.log('✅ Comprehensive report generated successfully');
      return {
        success: true,
        data: reportData
      };

    } catch (error) {
      console.error('❌ Failed to generate comprehensive report:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      return {
        success: false,
        error: 'Failed to generate comprehensive report',
        details: errorMessage
      };
    }
  }

  private processBrandVisibility(results: AnalysisResults) {
    // Process brand mentions to calculate visibility percentage
    const totalResponses = results.total_responses;
    const brandMentions = results.brand_mentions.length;
    const visibilityPercentage = totalResponses > 0 ? Math.round((brandMentions / totalResponses) * 100) : 0;

    // Group mentions by domain/platform
    const platformCounts: Record<string, { mentions: number; responses: Set<string> }> = {};
    
    results.brand_mentions.forEach(mention => {
      const response = results.responses.find(r => r.response_id === mention.response_id);
      if (response) {
        // Extract domain from citations if available
        const citations = results.citations.filter(c => c.response_id === response.response_id);
        citations.forEach(citation => {
          if (citation.source_url) {
            try {
              const domain = new URL(citation.source_url).hostname;
              if (!platformCounts[domain]) {
                platformCounts[domain] = { mentions: 0, responses: new Set() };
              }
              platformCounts[domain].mentions++;
              platformCounts[domain].responses.add(response.response_id);
            } catch (e) {
              // Invalid URL, skip
            }
          }
        });
      }
    });

    const platforms = Object.entries(platformCounts)
      .map(([domain, data]) => ({
        name: domain.replace('www.', '').split('.')[0],
        url: domain,
        mentions: data.mentions,
        visibility: Math.round((data.responses.size / totalResponses) * 100)
      }))
      .sort((a, b) => b.visibility - a.visibility)
      .slice(0, 5);

    return {
      percentage: visibilityPercentage,
      platforms,
      totalPrompts: results.job_status.total_queries,
      totalAppearances: visibilityPercentage,
    };
  }

  private processBrandReach(results: AnalysisResults) {
    // This would need persona and topic data from your backend
    // For now, return mock structure that matches your data
    return {
      personasVisibility: [],
      topicsVisibility: [],
    };
  }

  private processTopicMatrix(results: AnalysisResults) {
    // This would need persona and topic relationship data
    return {
      personas: [],
      topics: [],
      matrix: [],
    };
  }

  private processModelVisibility(results: AnalysisResults) {
    // Group responses by model
    const modelCounts: Record<string, number> = {};
    const totalResponses = results.total_responses;
    
    results.responses.forEach(response => {
      const model = response.model || 'Unknown';
      modelCounts[model] = (modelCounts[model] || 0) + 1;
    });

    return Object.entries(modelCounts)
      .map(([name, count]) => ({
        name,
        visibility: Math.round((count / totalResponses) * 100)
      }))
      .sort((a, b) => b.visibility - a.visibility);
  }

  private processSources(results: AnalysisResults) {
    // Process citations to get source domains and types
    const domainCounts: Record<string, number> = {};
    const typeCounts: Record<string, number> = {};

    results.citations.forEach(citation => {
      if (citation.source_url) {
        try {
          const url = new URL(citation.source_url);
          const domain = url.hostname.replace('www.', '');
          domainCounts[domain] = (domainCounts[domain] || 0) + 1;

          // Categorize by domain type (simplified)
          const category = this.categorizeDomain(domain);
          typeCounts[category] = (typeCounts[category] || 0) + 1;
        } catch (e) {
          // Invalid URL, skip
        }
      }
    });

    const topSources = Object.entries(domainCounts)
      .map(([domain, count]) => ({ domain, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    const sourceTypes = Object.entries(typeCounts)
      .map(([category, count]) => ({ category, count }))
      .sort((a, b) => b.count - a.count);

    return {
      topSources,
      sourceTypes,
    };
  }

  private categorizeDomain(domain: string): string {
    const lower = domain.toLowerCase();
    
    if (lower.includes('youtube') || lower.includes('spotify') || lower.includes('netflix')) {
      return 'Entertainment Sites';
    }
    if (lower.includes('amazon') || lower.includes('ebay') || lower.includes('shop')) {
      return 'E-commerce Sites';
    }
    if (lower.includes('facebook') || lower.includes('twitter') || lower.includes('instagram') || lower.includes('linkedin')) {
      return 'Social Networks';
    }
    if (lower.includes('reddit') || lower.includes('forum') || lower.includes('stack')) {
      return 'Forums/Community Sites';
    }
    if (lower.includes('wikipedia') || lower.includes('edu') || lower.includes('academic')) {
      return 'Educational Sites';
    }
    if (lower.includes('news') || lower.includes('cnn') || lower.includes('bbc') || lower.includes('times')) {
      return 'News/Media Sites';
    }
    if (lower.includes('blog') || lower.includes('medium') || lower.includes('wordpress')) {
      return 'Blogs/Content Sites';
    }
    if (lower.includes('review') || lower.includes('yelp') || lower.includes('rating')) {
      return 'Directory/Review Sites';
    }
    if (lower.includes('api') || lower.includes('service') || lower.includes('app')) {
      return 'Business Service Sites';
    }
    
    return 'Unknown/Other';
  }
}

// =============================================================================
// SERVICE INSTANCE & EXPORTS
// =============================================================================

export const analysisService = new AnalysisService();

// Helper functions for common operations
export const startAnalysis = (auditId: string) => analysisService.startAnalysis(auditId);
export const startAnalysisJob = (auditId: string) => analysisService.startAnalysisJob(auditId);
export const getJobStatus = (jobId: string) => analysisService.getJobStatus(jobId);
export const getAnalysisResults = (auditId: string) => analysisService.getResults(auditId);
export const runCompleteAnalysis = (auditId: string, onProgress?: (status: AnalysisJobStatus) => void) => 
  analysisService.runCompleteAnalysis(auditId, onProgress);
export const getComprehensiveReport = (auditId: string) => analysisService.getComprehensiveReport(auditId); 