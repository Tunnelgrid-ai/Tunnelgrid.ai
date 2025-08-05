/**
 * MY REPORTS PAGE
 * 
 * PURPOSE: Simplified interface showing only studies that have been confirmed and started analysis
 * 
 * FEATURES:
 * - View only studies that reached ANALYSIS_RUNNING status
 * - Simple list view with basic information
 * - Navigate to view completed reports
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  FileText,
  Plus
} from 'lucide-react';

import { 
  studyService, 
  Study, 
  StudyStatus
} from '@/services/studyService';
import { useAuth } from '@/contexts/AuthContext';
import { MainLayout } from '@/components/layout/MainLayout';

interface MyReportsPageProps {}

export const MyReportsPage: React.FC<MyReportsPageProps> = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // State management
  const [studies, setStudies] = useState<Study[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is authenticated (only in production)
  if (!user && process.env.NODE_ENV === 'production') {
    return (
      <MainLayout>
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Authentication Required</h3>
            <p className="text-muted-foreground mb-4">
              Please sign in to view your reports.
            </p>
            <Button onClick={() => navigate('/auth')}>
              Sign In
            </Button>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Load studies on component mount
  useEffect(() => {
    // In development, always load studies (user is always available)
    // In production, only load if user is authenticated
    if (user || process.env.NODE_ENV === 'development') {
      loadStudies();
    }
  }, [user]);

  const loadStudies = async () => {
    try {
      setLoading(true);
      setError(null);

      // Only fetch studies that have reached ANALYSIS_RUNNING or COMPLETED status
      const result = await studyService.listStudies({
        page: 1,
        page_size: 100, // Get all studies since we're filtering by status
      });
      
      if (result.success && result.data) {
        // Filter to only show studies that have been confirmed and started analysis
        const confirmedStudies = result.data.studies.filter(study => 
          study.status === StudyStatus.ANALYSIS_RUNNING || 
          study.status === StudyStatus.COMPLETED
        );
        setStudies(confirmedStudies);
      } else {
        setError(result.error || 'Failed to load reports');
      }
    } catch (err) {
      setError('Failed to load reports');
      console.error('Error loading reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStudyCard = (study: Study) => (
    <Card key={study.study_id} className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg font-semibold truncate">
              {study.study_name}
            </CardTitle>
            {study.study_description && (
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                {study.study_description}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2 ml-4">
            <Badge className={studyService.getStatusColor(study.status)}>
              {studyService.getStatusDisplayName(study.status)}
            </Badge>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        {/* Study Info */}
        <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground mb-4">
          <div>
            <span>Created {formatDate(study.created_at)}</span>
          </div>
          <div>
            <span>Updated {formatDate(study.updated_at)}</span>
          </div>
        </div>

        {/* Action Button */}
        <div className="flex gap-2">
          {study.status === StudyStatus.COMPLETED ? (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => navigate(`/reports/${study.study_id}`)}
              className="flex-1"
            >
              <FileText className="h-4 w-4 mr-2" />
              View Report
            </Button>
          ) : (
            <Button 
              variant="outline" 
              size="sm"
              className="flex-1"
              disabled
            >
              Analysis in Progress...
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );

  if (loading && studies.length === 0) {
    return (
      <MainLayout>
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-muted-foreground">Loading your reports...</p>
            </div>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold">My Reports</h1>
              <p className="text-muted-foreground mt-2">
                View your confirmed brand analysis reports
              </p>
              {process.env.NODE_ENV === 'development' && (
                <div className="mt-2">
                  <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                    🚀 Development Mode - Authentication Bypassed
                  </Badge>
                </div>
              )}
            </div>
            <Button onClick={() => navigate('/setup')} className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              New Study
            </Button>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Reports Grid */}
        {studies.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {studies.map(getStudyCard)}
          </div>
        ) : (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No reports found</h3>
            <p className="text-muted-foreground mb-4">
              You haven't completed any brand analysis studies yet. Create a new study to get started.
            </p>
            <Button onClick={() => navigate('/setup')}>
              <Plus className="h-4 w-4 mr-2" />
              Create Your First Study
            </Button>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

