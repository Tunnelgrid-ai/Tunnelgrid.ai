/**
 * AI ANALYSIS LOADING SCREEN
 * 
 * PURPOSE: Beautiful, engaging loading screen for AI analysis process
 * 
 * FEATURES:
 * - Real-time progress tracking
 * - Animated progress indicators
 * - Dynamic status messages
 * - Modern, responsive design
 * - Error state handling
 */

import React from 'react';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import { Bot, Brain, Search, Zap, AlertCircle, CheckCircle2 } from 'lucide-react';
import { AnalysisJobStatus } from '@/services/analysisService';

interface AnalysisLoadingScreenProps {
  status?: AnalysisJobStatus;
  onCancel?: () => void;
}

export const AnalysisLoadingScreen: React.FC<AnalysisLoadingScreenProps> = ({
  status,
  onCancel
}) => {
  const getStatusInfo = () => {
    if (!status) {
      return {
        icon: Bot,
        title: "Initializing AI Analysis",
        message: "Preparing to query top AI models for brand perception insights...",
        progress: 0,
        isComplete: false,
        isError: false
      };
    }

    const isComplete = status.status === 'completed' || status.status === 'partial_failure';
    const isError = status.status === 'failed';
    
    let icon = Bot;
    let title = "AI Analysis in Progress";
    let message = "Querying top AI models to understand brand perception...";

    switch (status.status) {
      case 'pending':
        icon = Bot;
        title = "Starting Analysis";
        message = "Preparing to analyze your brand with AI insights...";
        break;
      case 'running':
        icon = Brain;
        title = "AI Models Working";
        message = `Processing ${status.completed_queries} of ${status.total_queries} queries...`;
        break;
      case 'completed':
        icon = CheckCircle2;
        title = "Analysis Complete!";
        message = "Successfully gathered comprehensive brand insights.";
        break;
      case 'partial_failure':
        icon = AlertCircle;
        title = "Analysis Mostly Complete";
        message = `Completed ${status.completed_queries} of ${status.total_queries} queries with some issues.`;
        break;
      case 'failed':
        icon = AlertCircle;
        title = "Analysis Failed";
        message = status.error_message || "Unable to complete analysis. Please try again.";
        break;
    }

    return {
      icon,
      title,
      message,
      progress: status.progress_percentage,
      isComplete,
      isError
    };
  };

  const statusInfo = getStatusInfo();
  const IconComponent = statusInfo.icon;

  const formatTimeRemaining = (seconds?: number) => {
    if (!seconds || seconds <= 0) return null;
    
    if (seconds < 60) {
      return `${Math.round(seconds)} seconds remaining`;
    } else {
      const minutes = Math.floor(seconds / 60);
      return `~${minutes} minute${minutes > 1 ? 's' : ''} remaining`;
    }
  };

  const getProgressColor = () => {
    if (statusInfo.isError) return 'bg-red-500';
    if (statusInfo.isComplete) return 'bg-green-500';
    return 'bg-blue-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <Card className="bg-black/40 backdrop-blur-lg border-white/20 shadow-2xl">
          <CardContent className="p-8 text-center">
            {/* Animated Icon */}
            <div className="mb-8 flex justify-center">
              <div className={`
                relative p-6 rounded-full 
                ${statusInfo.isError ? 'bg-red-500/20' : statusInfo.isComplete ? 'bg-green-500/20' : 'bg-blue-500/20'}
                ${!statusInfo.isComplete && !statusInfo.isError ? 'animate-pulse' : ''}
              `}>
                <IconComponent 
                  className={`
                    w-12 h-12 
                    ${statusInfo.isError ? 'text-red-400' : statusInfo.isComplete ? 'text-green-400' : 'text-blue-400'}
                  `}
                />
                
                {/* Animated rings for active states */}
                {!statusInfo.isComplete && !statusInfo.isError && (
                  <>
                    <div className="absolute inset-0 rounded-full border-2 border-blue-400/30 animate-ping"></div>
                    <div className="absolute inset-0 rounded-full border border-blue-400/50 animate-pulse"></div>
                  </>
                )}
              </div>
            </div>

            {/* Title */}
            <h2 className="text-3xl font-bold text-white mb-4 font-heading">
              {statusInfo.title}
            </h2>

            {/* Message */}
            <p className="text-gray-300 text-lg mb-8 leading-relaxed">
              {statusInfo.message}
            </p>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-400">Progress</span>
                <span className="text-sm text-gray-400 font-mono">
                  {Math.round(statusInfo.progress)}%
                </span>
              </div>
              
              <Progress 
                value={statusInfo.progress} 
                className="h-3 bg-white/10"
              />
            </div>

            {/* Stats */}
            {status && (
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">
                    {status.completed_queries}
                  </div>
                  <div className="text-sm text-gray-400">Completed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">
                    {status.total_queries}
                  </div>
                  <div className="text-sm text-gray-400">Total Queries</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">
                    {status.failed_queries}
                  </div>
                  <div className="text-sm text-gray-400">Failed</div>
                </div>
              </div>
            )}

            {/* Time Remaining */}
            {status?.estimated_time_remaining && (
              <div className="mb-6">
                <p className="text-gray-400 text-sm">
                  ⏱️ {formatTimeRemaining(status.estimated_time_remaining)}
                </p>
              </div>
            )}

            {/* AI Models Indicator */}
            <div className="mb-6">
              <div className="flex justify-center items-center space-x-4 text-gray-400 text-sm">
                <div className="flex items-center space-x-2">
                  <Zap className="w-4 h-4 text-yellow-400" />
                  <span>OpenAI GPT-4o</span>
                </div>
                <div className="w-1 h-1 bg-gray-600 rounded-full"></div>
                <div className="flex items-center space-x-2">
                  <Search className="w-4 h-4 text-blue-400" />
                  <span>Advanced Analysis</span>
                </div>
                <div className="w-1 h-1 bg-gray-600 rounded-full"></div>
                <div className="flex items-center space-x-2">
                  <Brain className="w-4 h-4 text-purple-400" />
                  <span>Smart Processing</span>
                </div>
              </div>
            </div>

            {/* Dynamic Status Messages */}
            <div className="space-y-2 text-sm text-gray-400">
              {!statusInfo.isComplete && !statusInfo.isError && (
                <>
                  <p>🤖 AI models are analyzing your brand across multiple personas</p>
                  <p>📊 Extracting brand mentions and sentiment insights</p>
                  <p>🔍 Gathering citations and reference sources</p>
                </>
              )}
              
              {statusInfo.isComplete && !statusInfo.isError && (
                <>
                  <p>✨ Analysis complete with comprehensive insights</p>
                  <p>📈 Brand mentions and sentiment data ready</p>
                  <p>🎯 Citations and sources compiled</p>
                </>
              )}
              
              {statusInfo.isError && (
                <>
                  <p>❌ Analysis encountered issues</p>
                  <p>🔄 You can retry or view partial results</p>
                </>
              )}
            </div>

            {/* Cancel Button (only show during processing) */}
            {onCancel && !statusInfo.isComplete && !statusInfo.isError && (
              <div className="mt-8">
                <button
                  onClick={onCancel}
                  className="px-6 py-3 text-gray-400 hover:text-white transition-colors border border-gray-600 hover:border-gray-400 rounded-lg"
                >
                  Cancel Analysis
                </button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"></div>
        </div>
      </div>
    </div>
  );
}; 