import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface MatrixCell {
  personaName: string;
  topicName: string;
  score: number;
}

interface TopicVisibilityMatrixData {
  personas: string[];
  topics: string[];
  matrix: MatrixCell[];
}

interface TopicVisibilityMatrixProps {
  data: TopicVisibilityMatrixData;
  onCellClick?: (cell: MatrixCell) => void;
}

export const TopicVisibilityMatrix = ({ data, onCellClick }: TopicVisibilityMatrixProps) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "bg-green-500";
    if (score >= 60) return "bg-green-400";
    if (score >= 40) return "bg-yellow-400";
    if (score >= 20) return "bg-orange-400";
    return "bg-red-400";
  };

  const getScoreOpacity = (score: number) => {
    return `opacity-${Math.max(20, Math.min(100, score))}`;
  };

  const getScoreForCell = (persona: string, topic: string): number => {
    const cell = data.matrix.find(
      (c) => c.personaName === persona && c.topicName === topic
    );
    return cell?.score || 0;
  };

  const getCellData = (persona: string, topic: string): MatrixCell | null => {
    return data.matrix.find(
      (c) => c.personaName === persona && c.topicName === topic
    ) || null;
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-4">
        <CardTitle className="text-xl font-heading">Topic Visibility Matrix</CardTitle>
        <p className="text-sm text-muted-foreground">
          Explore to see how often your brand is mentioned for each persona for a given topic.
        </p>
      </CardHeader>
      <CardContent>
        <div className="relative">
          <div className="flex border border-border rounded-lg overflow-hidden">
            {/* Fixed Persona Column */}
            <div className="flex-shrink-0 bg-background border-r border-border">
              {/* Persona Column Header */}
              <div className="h-16 p-3 bg-muted/20 border-b border-border flex items-center justify-center">
                <span className="text-xs font-medium text-muted-foreground">Personas</span>
              </div>
              
              {/* Persona Names */}
              <div className="min-h-0">
                {data.personas.map((persona) => (
                  <div key={persona} className="h-14 p-2 border-b border-border/50 flex items-center justify-end">
                    <Badge variant="outline" className="text-xs font-medium max-w-[180px] truncate">
                      {persona}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>

            {/* Scrollable Topics & Matrix */}
            <div className="flex-1 overflow-x-auto">
              <div className="min-w-0" style={{ width: `${data.topics.length * 130}px` }}>
                {/* Topics Header */}
                <div className="h-16 border-b border-border bg-muted/20 flex">
                  {data.topics.map((topic) => (
                    <div 
                      key={topic}
                      className="w-32 flex-shrink-0 p-2 border-r border-border/50 last:border-r-0 flex items-center justify-center"
                    >
                      <div className="text-xs font-medium text-center transform -rotate-12 line-clamp-2">
                        {topic}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Matrix Grid */}
                <div className="min-h-0">
                  {data.personas.map((persona) => (
                    <div key={persona} className="h-14 border-b border-border/50 flex">
                      {data.topics.map((topic) => {
                        const score = getScoreForCell(persona, topic);
                        const cellData = getCellData(persona, topic);
                        
                        return (
                          <div
                            key={`${persona}-${topic}`}
                            className="w-32 flex-shrink-0 border-r border-border/50 last:border-r-0 p-1"
                          >
                            <div
                              className={`
                                w-full h-full rounded-md border border-border/30 flex items-center justify-center
                                cursor-pointer transition-all duration-200 hover:scale-105 hover:border-primary
                                ${getScoreColor(score)} ${score > 0 ? 'opacity-90' : 'opacity-30'}
                              `}
                              onClick={() => cellData && onCellClick?.(cellData)}
                              title={`${persona} × ${topic}: ${score}%`}
                            >
                              <span className="text-sm font-bold text-white drop-shadow-sm">
                                {score > 0 ? score : "—"}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Legend */}
          <div className="mt-6 flex items-center justify-center space-x-4">
            <span className="text-xs text-muted-foreground">Score Range:</span>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <div className="w-4 h-4 rounded bg-red-400"></div>
                <span className="text-xs">0-20</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-4 h-4 rounded bg-orange-400"></div>
                <span className="text-xs">21-40</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-4 h-4 rounded bg-yellow-400"></div>
                <span className="text-xs">41-60</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-4 h-4 rounded bg-green-400"></div>
                <span className="text-xs">61-80</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-4 h-4 rounded bg-green-500"></div>
                <span className="text-xs">81-100</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 