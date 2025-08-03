import { Topic } from "@/types/brandTypes";
import { TopicCard } from "./TopicCard";

interface TopicsCategorySectionProps {
  title: string;
  description: string;
  example: string;
  topics: Topic[];
  categoryColor: string;
  targetCount: number;
  onEditTopic?: (topicId: string, updates: Partial<Topic>) => void;
  onDeleteTopic?: (topicId: string) => void;
}

export const TopicsCategorySection: React.FC<TopicsCategorySectionProps> = ({
  title, 
  description, 
  example, 
  topics, 
  categoryColor, 
  targetCount,
  onEditTopic,
  onDeleteTopic
}) => {
  return (
    <div className={`p-6 rounded-lg border ${categoryColor}`}>
      <div className="space-y-4">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">{title}</h3>
            <span className="text-sm text-muted-foreground">
              {topics.length}/{targetCount} topics
            </span>
          </div>
          
          <p className="text-sm text-muted-foreground">{description}</p>
          
          <div className="text-xs text-accent bg-accent/10 rounded px-2 py-1 inline-block">
            Example: "{example}"
          </div>
        </div>
        
        {/* Topics Grid */}
        <div className="grid grid-cols-1 gap-3">
          {topics.map(topic => (
            <TopicCard 
              key={topic.id} 
              topic={topic} 
              onEdit={onEditTopic}
              onDelete={onDeleteTopic}
            />
          ))}
          
          {/* Empty state or add button could go here */}
          {topics.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <p className="text-sm">No {title.toLowerCase()} generated yet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 