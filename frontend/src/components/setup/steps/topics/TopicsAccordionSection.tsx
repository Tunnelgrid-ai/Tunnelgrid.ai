import { Topic } from "@/types/brandTypes";
import { TopicCard } from "./TopicCard";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent
} from "@/components/ui/accordion";

interface TopicsAccordionSectionProps {
  title: string;
  description: string;
  topics: Topic[];
  categoryColor: string;
  onEditTopic?: (topicId: string, updates: Partial<Topic>) => void;
  onDeleteTopic?: (topicId: string) => void;
  value: string; // For accordion control
}

export const TopicsAccordionSection: React.FC<TopicsAccordionSectionProps> = ({
  title, 
  description, 
  topics, 
  categoryColor,
  onEditTopic,
  onDeleteTopic,
  value
}) => {
  return (
    <AccordionItem
      value={value}
      className={`border rounded-lg ${categoryColor}`}
    >
      <AccordionTrigger className="px-6 py-4 text-left hover:no-underline">
        <div className="flex flex-col items-start space-y-1">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
      </AccordionTrigger>
      
      <AccordionContent className="px-6 pb-6">
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
          
          {/* Empty state */}
          {topics.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <p className="text-sm">No {title.toLowerCase()} generated yet</p>
            </div>
          )}
        </div>
      </AccordionContent>
    </AccordionItem>
  );
};