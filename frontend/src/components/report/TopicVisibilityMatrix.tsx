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
        <div className="overflow-x-auto">
          <div className="min-w-full">
            {/* Header with topics */}
            <div className="grid grid-cols-[200px_1fr] gap-4 mb-4">
              <div></div> {/* Empty cell for persona column */}
              <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${data.topics.length}, minmax(120px, 1fr))` }}>
                {data.topics.map((topic) => (
                  <div 
                    key={topic}
                    className="text-xs font-medium text-center p-2 bg-muted/20 rounded-lg transform -rotate-12 origin-center"
                    style={{ minHeight: '60px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  >
                    <span className="transform rotate-12">{topic}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Matrix rows */}
            <div className="space-y-2">
              {data.personas.map((persona) => (
                <div key={persona} className="grid grid-cols-[200px_1fr] gap-4">
                  {/* Persona name */}
                  <div className="flex items-center justify-end pr-4">
                    <Badge variant="outline" className="text-xs font-medium">
                      {persona}
                    </Badge>
                  </div>
                  
                  {/* Score cells */}
                  <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${data.topics.length}, minmax(120px, 1fr))` }}>
                    {data.topics.map((topic) => {
                      const score = getScoreForCell(persona, topic);
                      const cellData = getCellData(persona, topic);
                      
                      return (
                        <div
                          key={`${persona}-${topic}`}
                          className={`
                            h-12 rounded-lg border border-border flex items-center justify-center
                            cursor-pointer transition-all duration-200 hover:scale-105 hover:border-primary
                            ${getScoreColor(score)} ${getScoreOpacity(score)}
                          `}
                          onClick={() => cellData && onCellClick?.(cellData)}
                          title={`${persona} × ${topic}: ${score}%`}
                        >
                          <span className="text-sm font-bold text-white drop-shadow-sm">
                            {score > 0 ? score : "—"}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            {/* Legend */}
            <div className="mt-8 flex items-center justify-center space-x-4">
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
        </div>
      </CardContent>
    </Card>
  );
}; 