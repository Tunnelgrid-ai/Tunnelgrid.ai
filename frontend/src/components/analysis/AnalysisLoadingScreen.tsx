/**
 * AI ANALYSIS LOADING SCREEN
 * 
 * PURPOSE: Beautiful, engaging loading screen for AI analysis process
 * 
 * FEATURES:
 * - Real-time progress tracking for multiple LLM services
 * - Individual progress indicators for OpenAI, Perplexity, and Gemini
 * - Animated progress indicators
 * - Dynamic status messages
 * - Modern, responsive design
 * - Error state handling
 */

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getApiUrl } from '@/config/api';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Loader2, CheckCircle, AlertCircle, Brain, FileText, Users, Zap, Globe, Sparkles } from 'lucide-react';

interface LLMServiceStatus {
  service: 'openai' | 'perplexity' | 'gemini';
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress_percentage: number;
  completed_queries: number;
  total_queries: number;
  failed_queries: number;
  error_message?: string;
  estimated_time_remaining?: number;
}

interface AnalysisJobStatus {
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
  // New field for multi-service tracking
  service_statuses?: LLMServiceStatus[];
}

interface AnalysisLoadingScreenProps {
  auditId: string;
  jobId: string;
  onComplete?: (results: any) => void;
  onError?: (error: string) => void;
  onCancel?: () => void;
}

export const AnalysisLoadingScreen: React.FC<AnalysisLoadingScreenProps> = ({
  auditId,
  jobId,
  onComplete,
  onError,
  onCancel
}) => {
  const [status, setStatus] = useState<AnalysisJobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(true);

  // Poll for status updates
  useEffect(() => {
    let pollInterval: NodeJS.Timeout;

    const pollStatus = async () => {
      try {
        // Don't poll if we don't have a job ID yet
        if (!jobId) {
          console.log('⏳ Waiting for job ID...');
          return;
        }

        const response = await fetch(`${getApiUrl('ANALYSIS_STATUS')}/${jobId}`);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data: AnalysisJobStatus = await response.json();
        setStatus(data);

        // Handle completion
        if (data.status === 'completed') {
          setIsPolling(false);
          onComplete?.(data);
        } else if (data.status === 'failed') {
          setIsPolling(false);
          const errorMsg = data.error_message || 'Analysis failed';
          setError(errorMsg);
          onError?.(errorMsg);
        } else if (data.status === 'partial_failure') {
          // Continue polling but show warning
          console.warn('Analysis completed with partial failures:', data.error_message);
        }

      } catch (err) {
        console.error('Error polling analysis status:', err);
        setError(err instanceof Error ? err.message : 'Failed to get analysis status');
        setIsPolling(false);
        onError?.(err instanceof Error ? err.message : 'Failed to get analysis status');
      }
    };

    // Initial poll
    pollStatus();

    // Set up polling interval
    pollInterval = setInterval(pollStatus, 3000); // Poll every 3 seconds

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [jobId, onComplete, onError]);

  const getStatusIcon = () => {
    if (!jobId) return <Loader2 className="h-6 w-6 animate-spin" />;
    if (!status) return <Loader2 className="h-6 w-6 animate-spin" />;
    
    switch (status.status) {
      case 'pending':
        return <Loader2 className="h-6 w-6 animate-spin" />;
      case 'running':
        return <Brain className="h-6 w-6 animate-pulse text-blue-500" />;
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-6 w-6 text-red-500" />;
      case 'partial_failure':
        return <AlertCircle className="h-6 w-6 text-yellow-500" />;
      default:
        return <Loader2 className="h-6 w-6 animate-spin" />;
    }
  };

  const getStatusColor = () => {
    if (!jobId) return 'bg-gray-100 text-gray-800';
    if (!status) return 'bg-gray-100';
    
    switch (status.status) {
      case 'pending':
        return 'bg-blue-100 text-blue-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'partial_failure':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusMessage = () => {
    if (!jobId) return 'Starting analysis job...';
    if (!status) return 'Initializing analysis...';
    
    switch (status.status) {
      case 'pending':
        return 'Preparing analysis job...';
      case 'running':
        return 'Analyzing your brand with multiple AI services...';
      case 'completed':
        return 'Analysis completed successfully!';
      case 'failed':
        return 'Analysis failed';
      case 'partial_failure':
        return 'Analysis completed with some issues';
      default:
        return 'Processing...';
    }
  };

  const getServiceIcon = (service: string) => {
    switch (service) {
      case 'openai':
        return <Zap className="h-4 w-4" />;
      case 'perplexity':
        return <Globe className="h-4 w-4" />;
      case 'gemini':
        return <Sparkles className="h-4 w-4" />;
      default:
        return <Brain className="h-4 w-4" />;
    }
  };

  const getServiceColor = (service: string) => {
    switch (service) {
      case 'openai':
        return 'text-purple-600';
      case 'perplexity':
        return 'text-blue-600';
      case 'gemini':
        return 'text-orange-600';
      default:
        return 'text-gray-600';
    }
  };

  const getServiceStatusColor = (serviceStatus: LLMServiceStatus) => {
    switch (serviceStatus.status) {
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatTimeRemaining = (seconds?: number) => {
    if (!seconds) return null;
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s remaining`;
    }
    return `${remainingSeconds}s remaining`;
  };

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="w-full max-w-2xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-6 w-6" />
              Analysis Error
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
            <div className="flex gap-2">
              <Button onClick={() => window.location.reload()}>
                Try Again
              </Button>
              {onCancel && (
                <Button variant="outline" onClick={onCancel}>
                  Go Back
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-[400px] p-4">
      <Card className="w-full max-w-3xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {getStatusIcon()}
            AI Brand Analysis in Progress
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Status Badge */}
          <div className="flex items-center gap-2">
            <Badge className={getStatusColor()}>
              {!jobId ? 'STARTING' : status?.status?.toUpperCase() || 'INITIALIZING'}
            </Badge>
            {status?.estimated_time_remaining && (
              <span className="text-sm text-muted-foreground">
                {formatTimeRemaining(status.estimated_time_remaining)}
              </span>
            )}
          </div>

          {/* Overall Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Overall Progress</span>
              <span>{Math.round(status?.progress_percentage || 0)}%</span>
            </div>
            <Progress value={status?.progress_percentage || 0} className="h-2" />
          </div>

          {/* Status Message */}
          <p className="text-center text-muted-foreground">
            {getStatusMessage()}
          </p>

          {/* Multi-Service Progress Tracking */}
          {status?.service_statuses && status.service_statuses.length > 0 && (
            <div className="space-y-4">
              <h4 className="font-medium text-sm">AI Service Progress:</h4>
              <div className="grid gap-3">
                {status.service_statuses.map((serviceStatus, index) => (
                  <div key={index} className="border rounded-lg p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className={getServiceColor(serviceStatus.service)}>
                          {getServiceIcon(serviceStatus.service)}
                        </div>
                        <span className="font-medium capitalize">
                          {serviceStatus.service}
                        </span>
                      </div>
                      <Badge className={getServiceStatusColor(serviceStatus)}>
                        {serviceStatus.status.toUpperCase()}
                      </Badge>
                    </div>
                    
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Progress</span>
                        <span>{Math.round(serviceStatus.progress_percentage)}%</span>
                      </div>
                      <Progress value={serviceStatus.progress_percentage} className="h-1.5" />
                    </div>
                    
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>
                        {serviceStatus.completed_queries} / {serviceStatus.total_queries} queries
                      </span>
                      {serviceStatus.failed_queries > 0 && (
                        <span className="text-red-600">
                          {serviceStatus.failed_queries} failed
                        </span>
                      )}
                    </div>
                    
                    {serviceStatus.error_message && (
                      <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                        {serviceStatus.error_message}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Statistics */}
          {status && (
            <div className="grid grid-cols-3 gap-4 pt-4 border-t">
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-blue-600">
                  <FileText className="h-4 w-4" />
                  <span className="font-semibold">{status.total_queries}</span>
                </div>
                <p className="text-xs text-muted-foreground">Total Questions</p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 text-green-600">
                  <CheckCircle className="h-4 w-4" />
                  <span className="font-semibold">{status.completed_queries}</span>
                </div>
                <p className="text-xs text-muted-foreground">Completed</p>
              </div>
              {status.failed_queries > 0 && (
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-red-600">
                    <AlertCircle className="h-4 w-4" />
                    <span className="font-semibold">{status.failed_queries}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">Failed</p>
                </div>
              )}
            </div>
          )}

          {/* What's happening */}
          <div className="bg-muted/50 rounded-lg p-4">
            <h4 className="font-medium mb-2">What's happening:</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li className="flex items-center gap-2">
                <Brain className="h-3 w-3" />
                AI services are analyzing your brand across multiple personas
              </li>
              <li className="flex items-center gap-2">
                <FileText className="h-3 w-3" />
                Processing questions about brand perception and visibility
              </li>
              <li className="flex items-center gap-2">
                <Users className="h-3 w-3" />
                Generating insights for each target audience
              </li>
              <li className="flex items-center gap-2">
                <Zap className="h-3 w-3" />
                Combining results from multiple AI services for comprehensive analysis
              </li>
            </ul>
          </div>

          {/* Cancel Button */}
          {onCancel && status?.status === 'running' && (
            <div className="flex justify-center pt-4">
              <Button variant="outline" onClick={onCancel}>
                Cancel Analysis
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}; 