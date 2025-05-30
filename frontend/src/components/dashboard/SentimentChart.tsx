
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface SentimentData {
  name: string;
  positive: number;
  neutral: number;
  negative: number;
}

const data: SentimentData[] = [
  { name: "OpenAI", positive: 65, neutral: 25, negative: 10 },
  { name: "Perplexity", positive: 55, neutral: 35, negative: 10 },
  { name: "Claude", positive: 60, neutral: 30, negative: 10 },
  { name: "Gemini", positive: 50, neutral: 40, negative: 10 },
];

export const SentimentChart = () => {
  return (
    <div className="stat-card h-[300px]">
      <h3 className="text-lg font-medium mb-4">Brand Sentiment Across AI Models</h3>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20 }}>
          <XAxis type="number" domain={[0, 100]} />
          <YAxis dataKey="name" type="category" scale="band" />
          <Tooltip
            formatter={(value) => [`${value}%`, ""]}
            labelFormatter={(label) => `AI Model: ${label}`}
          />
          <Legend />
          <Bar
            dataKey="positive"
            stackId="a"
            fill="#22c55e"
            name="Positive"
            radius={[0, 0, 0, 0]}
          />
          <Bar
            dataKey="neutral"
            stackId="a"
            fill="#94a3b8"
            name="Neutral"
            radius={[0, 0, 0, 0]}
          />
          <Bar
            dataKey="negative"
            stackId="a"
            fill="#ef4444"
            name="Negative"
            radius={[0, 0, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
