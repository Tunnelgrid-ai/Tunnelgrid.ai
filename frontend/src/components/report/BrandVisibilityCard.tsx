import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

interface BrandVisibilityData {
  percentage: number;
  platforms: {
    name: string;
    url: string;
    mentions: number;
    visibility: number;
  }[];
  totalPrompts: number;
  totalAppearances: number;
}

interface BrandVisibilityCardProps {
  data: BrandVisibilityData;
  onViewDetails?: () => void;
}

export const BrandVisibilityCard = ({ data, onViewDetails }: BrandVisibilityCardProps) => {
  const radius = 90;
  const strokeWidth = 8;
  const normalizedRadius = radius - strokeWidth * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDasharray = `${circumference} ${circumference}`;
  const strokeDashoffset = circumference - (data.percentage / 100) * circumference;

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-4">
        <CardTitle className="text-xl font-heading">Brand Visibility</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Circular Progress */}
          <div className="flex flex-col items-center justify-center">
            <div className="relative w-48 h-48">
              <svg
                height={radius * 2}
                width={radius * 2}
                className="transform -rotate-90"
              >
                {/* Background circle */}
                <circle
                  stroke="rgb(55 65 81)"
                  fill="transparent"
                  strokeWidth={strokeWidth}
                  r={normalizedRadius}
                  cx={radius}
                  cy={radius}
                />
                {/* Progress circle */}
                <circle
                  stroke="rgb(34 197 94)"
                  fill="transparent"
                  strokeWidth={strokeWidth}
                  strokeDasharray={strokeDasharray}
                  style={{ strokeDashoffset }}
                  strokeLinecap="round"
                  r={normalizedRadius}
                  cx={radius}
                  cy={radius}
                  className="transition-all duration-500 ease-in-out"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-4xl font-bold text-foreground">
                  {data.percentage}%
                </span>
              </div>
            </div>
            <p className="text-sm text-muted-foreground mt-4 text-center max-w-xs">
              Across {data.totalPrompts} prompts, brands came up in {data.percentage}% of all responses.
              YouTube showed up in {data.totalAppearances}% of responses.
            </p>
          </div>

          {/* Platform List */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">All Brands</h3>
              <div className="flex space-x-4 text-sm text-muted-foreground">
                <span>Mentions</span>
                <span>Visibility</span>
              </div>
            </div>
            
            <div className="space-y-3">
              {data.platforms.map((platform, index) => (
                <div
                  key={platform.name}
                  className="flex items-center justify-between py-3 px-4 rounded-lg bg-muted/20 hover:bg-muted/30 transition-colors cursor-pointer"
                  onClick={onViewDetails}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-sm text-muted-foreground w-4">
                      {index + 1}
                    </span>
                    <div className="w-6 h-6 rounded bg-primary/20 flex items-center justify-center">
                      <span className="text-xs font-bold text-primary">
                        {platform.name.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <div className="font-medium">{platform.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {platform.url}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-6">
                    <span className="text-sm font-medium w-8 text-center">
                      {platform.mentions}
                    </span>
                    <span className="text-sm font-medium w-8 text-center">
                      {platform.visibility}%
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {onViewDetails && (
              <button
                onClick={onViewDetails}
                className="w-full mt-4 text-sm text-primary hover:text-primary/80 transition-colors"
              >
                View complete list →
              </button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 