import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Lightbulb, 
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  Users,
  MessageSquare
} from "lucide-react";

interface OpportunityGap {
  personaName: string;
  topicName: string;
  currentScore: number;
  potentialScore: number;
  impact: 'High' | 'Medium' | 'Low';
  effort: 'High' | 'Medium' | 'Low';
  priority: number;
}

interface ContentStrategy {
  topicName: string;
  currentVisibility: number;
  competitorMentions: number;
  recommendedAction: string;
  targetIncrease: number;
}

interface CompetitiveInsight {
  competitorName: string;
  mentionCount: number;
  strongestTopics: string[];
  opportunityAreas: string[];
}

interface StrategicRecommendationsData {
  opportunityGaps: OpportunityGap[];
  contentStrategy: ContentStrategy[];
  competitiveInsights: CompetitiveInsight[];
  overallScore: {
    current: number;
    potential: number;
  };
  keyRecommendations: string[];
}

interface StrategicRecommendationsCardProps {
  data: StrategicRecommendationsData;
  onRecommendationClick?: (recommendation: string) => void;
}

export const StrategicRecommendationsCard = ({ 
  data, 
  onRecommendationClick 
}: StrategicRecommendationsCardProps) => {
  // Debug logging
  console.log('🎯 Strategic Recommendations Component Data:', data);
  console.log('🏆 Competitive Insights:', data.competitiveInsights);
  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'High': return 'bg-red-100 text-red-800 border-red-200';
      case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getEffortColor = (effort: string) => {
    switch (effort) {
      case 'High': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'Medium': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'Low': return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityIcon = (priority: number) => {
    if (priority >= 8) return <AlertTriangle className="w-4 h-4 text-red-500" />;
    if (priority >= 6) return <Target className="w-4 h-4 text-yellow-500" />;
    return <CheckCircle className="w-4 h-4 text-green-500" />;
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-4">
        <CardTitle className="text-xl font-heading flex items-center space-x-2">
          <Lightbulb className="w-5 h-5 text-yellow-500" />
          <span>Strategic Recommendations</span>
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Actionable insights to improve your brand visibility and competitive positioning.
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Performance Score */}
        <div className="bg-muted/30 p-4 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold">Brand Visibility Potential</h3>
            <div className="text-sm text-muted-foreground">
              {data.overallScore.current}% → {data.overallScore.potential}%
            </div>
          </div>
          <Progress value={data.overallScore.current} className="h-2 mb-2" />
          <div className="flex items-center space-x-2 text-sm">
            <TrendingUp className="w-4 h-4 text-green-500" />
            <span className="text-green-600 font-medium">
              +{data.overallScore.potential - data.overallScore.current}% potential increase
            </span>
          </div>
        </div>

        {/* Key Recommendations */}
        <div>
          <h3 className="font-semibold mb-3 flex items-center space-x-2">
            <Target className="w-4 h-4" />
            <span>Priority Actions</span>
          </h3>
          <div className="space-y-2">
            {data.keyRecommendations.slice(0, 3).map((recommendation, index) => (
              <div 
                key={index}
                className="flex items-start space-x-3 p-3 bg-primary/5 rounded-lg cursor-pointer hover:bg-primary/10 transition-colors"
                onClick={() => onRecommendationClick?.(recommendation)}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getPriorityIcon(8 - index)}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">{recommendation}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-muted-foreground flex-shrink-0 mt-0.5" />
              </div>
            ))}
          </div>
        </div>

        {/* Opportunity Gaps */}
        <div>
          <h3 className="font-semibold mb-3 flex items-center space-x-2">
            <Users className="w-4 h-4" />
            <span>Top Opportunity Gaps</span>
          </h3>
          <div className="space-y-3">
            {data.opportunityGaps.slice(0, 4).map((gap, index) => (
              <div key={index} className="border border-border rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-sm">{gap.personaName}</span>
                    <span className="text-muted-foreground text-xs">×</span>
                    <span className="text-sm text-muted-foreground">{gap.topicName}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    {getPriorityIcon(gap.priority)}
                    <span className="text-xs text-muted-foreground">Priority {gap.priority}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-2 mb-2">
                  <div className="text-center">
                    <div className="text-lg font-bold text-primary">{gap.currentScore}%</div>
                    <div className="text-xs text-muted-foreground">Current</div>
                  </div>
                  <div className="text-center">
                    <ArrowRight className="w-4 h-4 mx-auto text-muted-foreground" />
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-green-600">{gap.potentialScore}%</div>
                    <div className="text-xs text-muted-foreground">Potential</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex space-x-2">
                    <Badge className={`text-xs ${getImpactColor(gap.impact)}`}>
                      {gap.impact} Impact
                    </Badge>
                    <Badge className={`text-xs ${getEffortColor(gap.effort)}`}>
                      {gap.effort} Effort
                    </Badge>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    +{gap.potentialScore - gap.currentScore}% potential
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Content Strategy */}
        <div>
          <h3 className="font-semibold mb-3 flex items-center space-x-2">
            <MessageSquare className="w-4 h-4" />
            <span>Content Strategy Insights</span>
          </h3>
          <div className="space-y-3">
            {data.contentStrategy.slice(0, 3).map((strategy, index) => (
              <div key={index} className="border border-border rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-sm">{strategy.topicName}</h4>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-muted-foreground">
                      {strategy.competitorMentions} competitor mentions
                    </span>
                  </div>
                </div>
                
                <div className="mb-2">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span>Current Visibility</span>
                    <span>{strategy.currentVisibility}%</span>
                  </div>
                  <Progress value={strategy.currentVisibility} className="h-1" />
                </div>
                
                <div className="text-sm text-muted-foreground mb-2">
                  {strategy.recommendedAction}
                </div>
                
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-xs">
                    Target: +{strategy.targetIncrease}%
                  </Badge>
                  <TrendingUp className="w-4 h-4 text-green-500" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Competitive Insights */}
        {data.competitiveInsights.length > 0 && (
          <div>
            <h3 className="font-semibold mb-3 flex items-center space-x-2">
              <TrendingDown className="w-4 h-4" />
              <span>Competitive Analysis</span>
            </h3>
            <div className="space-y-3">
              {data.competitiveInsights.slice(0, 2).map((insight, index) => (
                <div key={index} className="border border-border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-sm">{insight.competitorName}</h4>
                    <Badge variant="outline" className="text-xs">
                      {insight.mentionCount} mentions
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div>
                      <div className="text-muted-foreground mb-1">Strong in:</div>
                      <div className="space-y-1">
                        {insight.strongestTopics.slice(0, 2).map((topic, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs mr-1 max-w-full">
                            <span className="truncate block max-w-[120px]" title={topic}>
                              {topic.length > 20 ? topic.substring(0, 20) + '...' : topic}
                            </span>
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground mb-1">Opportunities:</div>
                      <div className="space-y-1">
                        {insight.opportunityAreas.slice(0, 2).map((area, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs mr-1 bg-green-50 max-w-full">
                            <span className="truncate block max-w-[120px]" title={area}>
                              {area.length > 20 ? area.substring(0, 20) + '...' : area}
                            </span>
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="pt-4 border-t border-border">
          <Button className="w-full" onClick={() => onRecommendationClick?.('detailed-analysis')}>
            <Lightbulb className="w-4 h-4 mr-2" />
            View Detailed Action Plan
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};