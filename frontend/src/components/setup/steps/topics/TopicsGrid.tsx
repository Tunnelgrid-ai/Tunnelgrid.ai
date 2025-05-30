
import React from "react";
import { Topic } from "@/types/brandTypes";
import { TopicChip } from "./TopicChip";

interface TopicsGridProps {
  topics: Topic[];
  onUpdateTopic: (updatedTopic: Topic) => void;
}

export const TopicsGrid: React.FC<TopicsGridProps> = ({ topics, onUpdateTopic }) => {
  if (topics.length === 0) {
    return (
      <div className="text-center p-8 border-2 border-dashed rounded-lg">
        <p className="text-muted-foreground">
          No topics available. Please add topics to continue.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-4">
      {topics.map((topic) => (
        <TopicChip
          key={topic.id}
          topic={topic}
          onUpdate={onUpdateTopic}
        />
      ))}
    </div>
  );
};
