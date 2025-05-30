
interface Recommendation {
  id: string;
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
}

interface RecommendationsCardProps {
  recommendations: Recommendation[];
}

export const RecommendationsCard = ({
  recommendations,
}: RecommendationsCardProps) => {
  const getPriorityBadgeColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-50 text-red-700 border-red-200";
      case "medium":
        return "bg-yellow-50 text-yellow-700 border-yellow-200";
      case "low":
        return "bg-green-50 text-green-700 border-green-200";
      default:
        return "bg-gray-50 text-gray-700 border-gray-200";
    }
  };

  return (
    <div className="stat-card col-span-full">
      <h3 className="text-lg font-medium mb-4">Optimization Recommendations</h3>
      <div className="space-y-4">
        {recommendations.map((rec) => (
          <div
            key={rec.id}
            className="border rounded-md p-4 bg-white"
          >
            <div className="flex justify-between items-center mb-2">
              <h4 className="font-medium">{rec.title}</h4>
              <span
                className={`text-xs px-2 py-0.5 rounded-full border ${getPriorityBadgeColor(
                  rec.priority
                )}`}
              >
                {rec.priority.charAt(0).toUpperCase() + rec.priority.slice(1)} Priority
              </span>
            </div>
            <p className="text-sm text-muted-foreground">{rec.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
