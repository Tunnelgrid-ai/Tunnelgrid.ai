
import { Progress } from "@/components/ui/progress";

interface PerceptionScoreCardProps {
  score: number;
  change: number;
  title: string;
}

export const PerceptionScoreCard = ({
  score,
  change,
  title,
}: PerceptionScoreCardProps) => {
  return (
    <div className="stat-card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">{title}</h3>
        <div
          className={`text-sm px-2 py-0.5 rounded-full ${
            change > 0
              ? "bg-green-50 text-green-700"
              : change < 0
              ? "bg-red-50 text-red-700"
              : "bg-gray-50 text-gray-700"
          }`}
        >
          {change > 0 ? "+" : ""}
          {change.toFixed(1)}%
        </div>
      </div>
      <div className="text-3xl font-bold mb-1">{score.toFixed(1)}</div>
      <Progress
        value={score}
        className="h-2"
      />
      <p className="text-sm text-muted-foreground mt-2">
        {score >= 75
          ? "Excellent brand perception"
          : score >= 60
          ? "Good brand perception"
          : score >= 40
          ? "Average brand perception"
          : "Needs improvement"}
      </p>
    </div>
  );
};
