import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface TopSource {
  domain: string;
  count: number;
}

interface SourceType {
  category: string;
  count: number;
}

interface SourcesData {
  topSources: TopSource[];
  sourceTypes: SourceType[];
}

interface SourcesCardProps {
  data: SourcesData;
  onSourceClick?: (source: TopSource) => void;
  onSourceTypeClick?: (sourceType: SourceType) => void;
}

export const SourcesCard = ({ data, onSourceClick, onSourceTypeClick }: SourcesCardProps) => {
  const getDomainIcon = (domain: string) => {
    const lowerDomain = domain.toLowerCase();
    
    if (lowerDomain.includes('youtube')) return '▶️';
    if (lowerDomain.includes('spotify')) return '🎵';
    if (lowerDomain.includes('amazon')) return '📦';
    if (lowerDomain.includes('ebay')) return '🛒';
    if (lowerDomain.includes('wikipedia')) return '📚';
    if (lowerDomain.includes('google')) return '🔍';
    if (lowerDomain.includes('apple')) return '🍎';
    if (lowerDomain.includes('reddit')) return '👥';
    if (lowerDomain.includes('twitter') || lowerDomain.includes('x.com')) return '🐦';
    if (lowerDomain.includes('facebook')) return '👍';
    if (lowerDomain.includes('instagram')) return '📸';
    if (lowerDomain.includes('linkedin')) return '💼';
    if (lowerDomain.includes('github')) return '👨‍💻';
    if (lowerDomain.includes('stackoverflow')) return '💻';
    if (lowerDomain.includes('medium')) return '📝';
    return '🌐';
  };

  const getCategoryIcon = (category: string) => {
    const lowerCategory = category.toLowerCase();
    
    if (lowerCategory.includes('business')) return '💼';
    if (lowerCategory.includes('entertainment')) return '🎬';
    if (lowerCategory.includes('blog')) return '📝';
    if (lowerCategory.includes('news')) return '📰';
    if (lowerCategory.includes('social')) return '👥';
    if (lowerCategory.includes('directory')) return '📁';
    if (lowerCategory.includes('forum')) return '💬';
    if (lowerCategory.includes('educational')) return '🎓';
    if (lowerCategory.includes('e-commerce')) return '🛒';
    if (lowerCategory.includes('service')) return '⚙️';
    return '📄';
  };

  const maxSourceCount = Math.max(...data.topSources.map(s => s.count));
  const maxTypeCount = Math.max(...data.sourceTypes.map(s => s.count));

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-4">
        <CardTitle className="text-xl font-heading">Sources</CardTitle>
        <p className="text-sm text-muted-foreground">
          See which domains and content categories are most commonly cited when AI mentions your brand.
        </p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Top Sources */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Top Sources</h3>
            <p className="text-sm text-muted-foreground">
              Searching various prompts to AI tools from where your brand comes up most often.
            </p>
            
            <div className="border border-border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow className="border-border">
                    <TableHead className="text-muted-foreground">Domain</TableHead>
                    <TableHead className="text-muted-foreground text-right">Mentions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.topSources.map((source) => (
                    <TableRow 
                      key={source.domain}
                      className="border-border hover:bg-muted/20 cursor-pointer transition-colors"
                      onClick={() => onSourceClick?.(source)}
                    >
                      <TableCell>
                        <div className="flex items-center space-x-3">
                          <span className="text-lg">
                            {getDomainIcon(source.domain)}
                          </span>
                          <div>
                            <div className="font-medium">{source.domain}</div>
                            {/* Visual bar */}
                            <div className="mt-1 w-full bg-muted/30 rounded-full h-1.5">
                              <div
                                className="h-1.5 rounded-full bg-primary transition-all duration-500"
                                style={{ width: `${(source.count / maxSourceCount) * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <span className="font-semibold text-primary">
                          {source.count}
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>

          {/* Source Types */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Source Type</h3>
            <p className="text-sm text-muted-foreground">
              Based on content, brands visibility by content type. Helps identify where to be mentioned or what content to create.
            </p>
            
            <div className="border border-border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow className="border-border">
                    <TableHead className="text-muted-foreground">Category</TableHead>
                    <TableHead className="text-muted-foreground text-right">Mentions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.sourceTypes.map((sourceType) => (
                    <TableRow 
                      key={sourceType.category}
                      className="border-border hover:bg-muted/20 cursor-pointer transition-colors"
                      onClick={() => onSourceTypeClick?.(sourceType)}
                    >
                      <TableCell>
                        <div className="flex items-center space-x-3">
                          <span className="text-lg">
                            {getCategoryIcon(sourceType.category)}
                          </span>
                          <div>
                            <div className="font-medium">{sourceType.category}</div>
                            {/* Visual bar */}
                            <div className="mt-1 w-full bg-muted/30 rounded-full h-1.5">
                              <div
                                className="h-1.5 rounded-full bg-accent transition-all duration-500"
                                style={{ width: `${(sourceType.count / maxTypeCount) * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <span className="font-semibold text-accent">
                          {sourceType.count}
                        </span>
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