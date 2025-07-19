import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface PersonaVisibility {
  name: string;
  visibility: number;
}

interface TopicVisibility {
  name: string;
  visibility: number;
}

interface BrandReachData {
  personasVisibility: PersonaVisibility[];
  topicsVisibility: TopicVisibility[];
}

interface BrandReachCardProps {
  data: BrandReachData;
  onPersonaClick?: (persona: PersonaVisibility) => void;
  onTopicClick?: (topic: TopicVisibility) => void;
}

export const BrandReachCard = ({ data, onPersonaClick, onTopicClick }: BrandReachCardProps) => {
  const getVisibilityColor = (visibility: number) => {
    if (visibility >= 50) return "text-green-400";
    if (visibility >= 30) return "text-yellow-400";
    return "text-red-400";
  };

  const getVisibilityBg = (visibility: number) => {
    if (visibility >= 50) return "bg-green-400/10";
    if (visibility >= 30) return "bg-yellow-400/10";
    return "bg-red-400/10";
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-4">
        <CardTitle className="text-xl font-heading">Brand Reach</CardTitle>
        <p className="text-sm text-muted-foreground">
          Explore which topics, personas, and sources are most frequently tied to your brand across AI-generated content.
        </p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Personas Visibility */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Personas Visibility</h3>
            <p className="text-sm text-muted-foreground">
              We create relevant personas and give AI prompts from their perspective. Here's how often your brand shows up in their results.
            </p>
            
            <div className="border border-border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow className="border-border">
                    <TableHead className="text-muted-foreground">Persona</TableHead>
                    <TableHead className="text-muted-foreground text-right">Visibility</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.personasVisibility.map((persona) => (
                    <TableRow 
                      key={persona.name}
                      className="border-border hover:bg-muted/20 cursor-pointer transition-colors"
                      onClick={() => onPersonaClick?.(persona)}
                    >
                      <TableCell className="font-medium">{persona.name}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <span className={`font-semibold ${getVisibilityColor(persona.visibility)}`}>
                            {persona.visibility}%
                          </span>
                          <div className={`w-2 h-2 rounded-full ${getVisibilityBg(persona.visibility)}`} />
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>

          {/* Topics Visibility */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Topic Visibility</h3>
            <p className="text-sm text-muted-foreground">
              Shows how often your brand is mentioned in AI responses about these topics, ranked by visibility score.
            </p>
            
            <div className="border border-border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow className="border-border">
                    <TableHead className="text-muted-foreground">Topic</TableHead>
                    <TableHead className="text-muted-foreground text-right">Visibility</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.topicsVisibility.map((topic) => (
                    <TableRow 
                      key={topic.name}
                      className="border-border hover:bg-muted/20 cursor-pointer transition-colors"
                      onClick={() => onTopicClick?.(topic)}
                    >
                      <TableCell className="font-medium">{topic.name}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <span className={`font-semibold ${getVisibilityColor(topic.visibility)}`}>
                            {topic.visibility}%
                          </span>
                          <div className={`w-2 h-2 rounded-full ${getVisibilityBg(topic.visibility)}`} />
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 