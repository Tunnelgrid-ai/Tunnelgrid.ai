
interface Topic {
  id: string;
  name: string;
  percentage: number;
}

interface TopicsCardProps {
  topics: Topic[];
}

export const TopicsCard = ({ topics }: TopicsCardProps) => {
  return (
    <div className="stat-card">
      <h3 className="text-lg font-medium mb-4">Top Topics</h3>
      <div className="space-y-4">
        {topics.map((topic) => (
          <div key={topic.id} className="space-y-1">
            <div className="flex justify-between">
              <span className="text-sm font-medium">{topic.name}</span>
              <span className="text-sm text-muted-foreground">
                {topic.percentage}%
              </span>
            </div>
            <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
              <div
                className="h-full bg-brand-purple rounded-full"
                style={{ width: `${topic.percentage}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
