/**
 * SERVICE SELECTION STEP
 * 
 * PURPOSE: Allow users to select which LLM services to use for brand analysis
 * 
 * FEATURES:
 * - Service selection with descriptions
 * - Cost and performance information
 * - Service availability status
 * - Recommended configurations
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Zap, Globe, Sparkles, CheckCircle, AlertCircle, Info } from 'lucide-react';

export type LLMServiceType = 'openai' | 'perplexity' | 'gemini';

interface ServiceInfo {
  id: LLMServiceType;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  features: string[];
  cost: string;
  speed: 'fast' | 'medium' | 'slow';
  accuracy: 'high' | 'medium' | 'low';
  availability: 'available' | 'beta' | 'coming-soon';
  recommended: boolean;
}

const services: ServiceInfo[] = [
  {
    id: 'openai',
    name: 'OpenAI GPT-4o',
    description: 'Advanced language model with excellent reasoning and analysis capabilities',
    icon: <Zap className="h-5 w-5" />,
    color: 'text-purple-600',
    features: [
      'Excellent reasoning capabilities',
      'Strong citation extraction',
      'Consistent response quality',
      'Wide knowledge base'
    ],
    cost: '$0.01 per 1K tokens',
    speed: 'fast',
    accuracy: 'high',
    availability: 'available',
    recommended: true
  },
  {
    id: 'perplexity',
    name: 'Perplexity AI',
    description: 'Real-time web search with up-to-date information and citations',
    icon: <Globe className="h-5 w-5" />,
    color: 'text-blue-600',
    features: [
      'Real-time web search',
      'Live citations and sources',
      'Current market insights',
      'Brand mention detection'
    ],
    cost: '$0.005 per 1K tokens',
    speed: 'medium',
    accuracy: 'high',
    availability: 'available',
    recommended: true
  },
  {
    id: 'gemini',
    name: 'Google Gemini',
    description: 'Google\'s advanced AI model with strong analytical capabilities',
    icon: <Sparkles className="h-5 w-5" />,
    color: 'text-orange-600',
    features: [
      'Strong analytical reasoning',
      'Multimodal capabilities',
      'Google\'s latest technology',
      'Competitive pricing'
    ],
    cost: '$0.003 per 1K tokens',
    speed: 'fast',
    accuracy: 'high',
    availability: 'beta',
    recommended: false
  }
];

interface ServiceSelectionStepProps {
  selectedServices: LLMServiceType[];
  onServiceToggle: (service: LLMServiceType) => void;
  onNext: () => void;
  onBack: () => void;
  isSubmitting?: boolean;
}

export const ServiceSelectionStep: React.FC<ServiceSelectionStepProps> = ({
  selectedServices,
  onServiceToggle,
  onNext,
  onBack,
  isSubmitting = false
}) => {
  const getSpeedColor = (speed: string) => {
    switch (speed) {
      case 'fast': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'slow': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getAccuracyColor = (accuracy: string) => {
    switch (accuracy) {
      case 'high': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getAvailabilityBadge = (availability: string) => {
    switch (availability) {
      case 'available':
        return <Badge variant="default" className="bg-green-100 text-green-800">Available</Badge>;
      case 'beta':
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800">Beta</Badge>;
      case 'coming-soon':
        return <Badge variant="outline" className="text-gray-500">Coming Soon</Badge>;
      default:
        return null;
    }
  };

  const isServiceEnabled = (service: ServiceInfo) => {
    return service.availability === 'available' || service.availability === 'beta';
  };

  const canProceed = selectedServices.length > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Choose AI Services</h2>
        <p className="text-muted-foreground">
          Select which AI services to use for your brand analysis. Using multiple services provides more comprehensive insights.
        </p>
      </div>

      {/* Service Selection */}
      <div className="grid gap-4">
        {services.map((service) => (
          <Card 
            key={service.id} 
            className={`relative transition-all duration-200 ${
              selectedServices.includes(service.id) 
                ? 'ring-2 ring-blue-500 bg-blue-50/50' 
                : 'hover:shadow-md'
            } ${!isServiceEnabled(service) ? 'opacity-50' : ''}`}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={service.color}>
                    {service.icon}
                  </div>
                  <div>
                    <CardTitle className="text-lg flex items-center gap-2">
                      {service.name}
                      {service.recommended && (
                        <Badge variant="default" className="bg-green-100 text-green-800 text-xs">
                          Recommended
                        </Badge>
                      )}
                    </CardTitle>
                    <CardDescription className="mt-1">
                      {service.description}
                    </CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getAvailabilityBadge(service.availability)}
                  {isServiceEnabled(service) && (
                    <Switch
                      checked={selectedServices.includes(service.id)}
                      onCheckedChange={() => onServiceToggle(service.id)}
                      disabled={!isServiceEnabled(service)}
                    />
                  )}
                </div>
              </div>
            </CardHeader>
            
            {isServiceEnabled(service) && (
              <CardContent className="pt-0">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Features */}
                  <div>
                    <h4 className="font-medium text-sm mb-2">Key Features</h4>
                    <ul className="space-y-1">
                      {service.features.map((feature, index) => (
                        <li key={index} className="flex items-center gap-2 text-sm text-muted-foreground">
                          <CheckCircle className="h-3 w-3 text-green-500" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Metrics */}
                  <div>
                    <h4 className="font-medium text-sm mb-2">Performance</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Cost:</span>
                        <span className="font-medium">{service.cost}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Speed:</span>
                        <span className={`font-medium ${getSpeedColor(service.speed)}`}>
                          {service.speed.charAt(0).toUpperCase() + service.speed.slice(1)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Accuracy:</span>
                        <span className={`font-medium ${getAccuracyColor(service.accuracy)}`}>
                          {service.accuracy.charAt(0).toUpperCase() + service.accuracy.slice(1)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            )}
          </Card>
        ))}
      </div>

      {/* Recommendations */}
      {selectedServices.length === 0 && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            We recommend selecting at least OpenAI and Perplexity for the most comprehensive analysis. 
            OpenAI provides excellent reasoning while Perplexity offers real-time web search capabilities.
          </AlertDescription>
        </Alert>
      )}

      {selectedServices.length > 0 && (
        <Alert className="bg-blue-50 border-blue-200">
          <CheckCircle className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-blue-800">
            <strong>Selected Services:</strong> {selectedServices.map(s => 
              services.find(service => service.id === s)?.name
            ).join(', ')}
          </AlertDescription>
        </Alert>
      )}

      {/* Navigation */}
      <div className="flex justify-between pt-6">
        <Button variant="outline" onClick={onBack} disabled={isSubmitting}>
          Back
        </Button>
        <Button 
          onClick={onNext} 
          disabled={!canProceed || isSubmitting}
          className="min-w-[100px]"
        >
          {isSubmitting ? 'Processing...' : 'Continue'}
        </Button>
      </div>
    </div>
  );
}; 