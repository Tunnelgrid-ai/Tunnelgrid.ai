
import { useEffect } from "react";
import { nanoid } from "nanoid";
import { Topic, Product } from "@/types/brandTypes";

// Sample topics to pre-populate if none exist
const sampleTopics = [
  "Product Quality",
  "Customer Service",
  "Sustainability",
  "Innovation",
  "Value for Money",
  "Brand Reputation",
  "User Experience",
  "Product Features",
  "Reliability",
  "Industry Trends"
];

export const useTopicsInitialization = (
  topics: Topic[],
  setTopics: (topics: Topic[]) => void
) => {
  // Pre-populate with sample topics if none exist
  useEffect(() => {
    if (topics.length === 0) {
      const initialTopics = sampleTopics.map(name => ({
        id: nanoid(),
        name,
        description: ""
      }));
      setTopics(initialTopics);
    }
  }, [topics.length, setTopics]);

  const handleUpdateTopic = (updatedTopic: Topic) => {
    setTopics(topics.map(topic => 
      topic.id === updatedTopic.id ? updatedTopic : topic
    ));
  };

  return { handleUpdateTopic };
};
