import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

interface ModelVisibilityData {
  name: string;
  visibility: number;
  logo?: string;
}

interface ModelVisibilityCardProps {
  data: ModelVisibilityData[];
  onModelClick?: (model: ModelVisibilityData) => void;
}

export const ModelVisibilityCard = ({ data, onModelClick }: ModelVisibilityCardProps) => {
  const getModelIcon = (modelName: string) => {
    const name = modelName.toLowerCase();
    
    if (name.includes('google')) return '🔍';
    if (name.includes('anthropic')) return '🤖';
    if (name.includes('openai') || name.includes('gpt')) return '🧠';
    if (name.includes('perplexity')) return '🔮';
    if (name.includes('claude')) return '🎭';
    return '⚡';
  };

  const getVisibilityColor = (visibility: number) => {
    if (visibility >= 50) return "text-green-400";
    if (visibility >= 30) return "text-yellow-400";
    return "text-red-400";
  };

  const getProgressColor = (visibility: number) => {
    if (visibility >= 50) return "bg-green-400";
    if (visibility >= 30) return "bg-yellow-400";
    return "bg-red-400";
  };

  // Sort models by visibility in descending order
  const sortedData = [...data].sort((a, b) => b.visibility - a.visibility);

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-4">
        <CardTitle className="text-xl font-heading">Model Visibility</CardTitle>
        <p className="text-sm text-muted-foreground">
          Explore how often your brand is surfaced across models.
        </p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sortedData.map((model, index) => (
            <div
              key={model.name}
              className="flex items-center justify-between p-4 rounded-lg bg-muted/10 hover:bg-muted/20 transition-colors cursor-pointer group"
              onClick={() => onModelClick?.(model)}
            >
              <div className="flex items-center space-x-4 flex-1">
                {/* Model Icon */}
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-lg">
                  {model.logo || getModelIcon(model.name)}
                </div>

                {/* Model Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <h4 className="font-medium text-foreground truncate">
                      {model.name}
                    </h4>
                    <span className="text-xs text-muted-foreground">
                      #{index + 1}
                    </span>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mt-2 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className={`text-sm font-semibold ${getVisibilityColor(model.visibility)}`}>
                        {model.visibility}%
                      </span>
                    </div>
                    <div className="w-full bg-muted/30 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(model.visibility)}`}
                        style={{ width: `${model.visibility}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Visibility Badge */}
                <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                  model.visibility >= 50 
                    ? 'bg-green-400/10 text-green-400'
                    : model.visibility >= 30
                    ? 'bg-yellow-400/10 text-yellow-400'
                    : 'bg-red-400/10 text-red-400'
                }`}>
                  {model.visibility >= 50 ? 'High' : model.visibility >= 30 ? 'Medium' : 'Low'}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="mt-6 p-4 bg-muted/10 rounded-lg">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Average Visibility:</span>
            <span className="font-semibold">
              {(data.reduce((sum, model) => sum + model.visibility, 0) / data.length).toFixed(1)}%
            </span>
          </div>
          <div className="flex items-center justify-between text-sm mt-1">
            <span className="text-muted-foreground">Top Model:</span>
            <span className="font-semibold">
              {sortedData[0]?.name} ({sortedData[0]?.visibility}%)
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 