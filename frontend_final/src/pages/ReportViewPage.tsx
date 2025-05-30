
import { useParams } from "react-router-dom";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Share2 } from "lucide-react";

interface ReportData {
  id: string;
  brandName: string;
  brandLogo?: string;
  analysisDate: string;
  perceptionScore: number;
  sentimentScore: {
    positive: number;
    neutral: number;
    negative: number;
  };
  topics: {
    name: string;
    score: number;
  }[];
}

// Mock data for reports
const mockReportData: Record<string, ReportData> = {
  "report-1": {
    id: "report-1",
    brandName: "Nike",
    brandLogo: "https://placehold.co/100x100?text=Nike",
    analysisDate: "2025-04-30",
    perceptionScore: 87,
    sentimentScore: {
      positive: 65,
      neutral: 25,
      negative: 10
    },
    topics: [
      { name: "Product Quality", score: 92 },
      { name: "Customer Service", score: 78 },
      { name: "Sustainability", score: 84 },
      { name: "Innovation", score: 91 }
    ]
  },
  "report-2": {
    id: "report-2",
    brandName: "Adidas",
    brandLogo: "https://placehold.co/100x100?text=Adidas",
    analysisDate: "2025-04-28",
    perceptionScore: 82,
    sentimentScore: {
      positive: 58,
      neutral: 32,
      negative: 10
    },
    topics: [
      { name: "Product Quality", score: 89 },
      { name: "Customer Service", score: 75 },
      { name: "Sustainability", score: 81 },
      { name: "Innovation", score: 83 }
    ]
  },
  "report-3": {
    id: "report-3",
    brandName: "TechPulse",
    brandLogo: "https://placehold.co/100x100?text=TP",
    analysisDate: "2025-04-25",
    perceptionScore: 79,
    sentimentScore: {
      positive: 52,
      neutral: 35,
      negative: 13
    },
    topics: [
      { name: "Product Quality", score: 85 },
      { name: "Customer Service", score: 72 },
      { name: "Innovation", score: 90 },
      { name: "Pricing", score: 70 }
    ]
  },
  "report-4": {
    id: "report-4",
    brandName: "EcoSmart",
    brandLogo: "https://placehold.co/100x100?text=Eco",
    analysisDate: "2025-04-22",
    perceptionScore: 91,
    sentimentScore: {
      positive: 72,
      neutral: 22,
      negative: 6
    },
    topics: [
      { name: "Sustainability", score: 95 },
      { name: "Product Quality", score: 87 },
      { name: "Ethical Practices", score: 93 },
      { name: "Innovation", score: 84 }
    ]
  }
};

const ReportViewPage = () => {
  const { reportId } = useParams<{ reportId: string }>();
  const report = reportId ? mockReportData[reportId] : null;
  
  if (!report) {
    return (
      <MainLayout>
        <div className="text-center py-16">
          <h1 className="text-2xl font-bold mb-2">Report Not Found</h1>
          <p className="text-muted-foreground">The requested report could not be found.</p>
        </div>
      </MainLayout>
    );
  }
  
  return (
    <MainLayout fullWidth>
      <div className="mb-6 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-slate-100 rounded-md flex items-center justify-center overflow-hidden">
            {report.brandLogo ? (
              <img src={report.brandLogo} alt={report.brandName} className="w-full h-full object-cover" />
            ) : (
              <span className="text-xl font-medium">{report.brandName.substring(0, 2)}</span>
            )}
          </div>
          <div>
            <h1 className="text-2xl font-bold">{report.brandName}</h1>
            <p className="text-sm text-muted-foreground">
              Analysis from {new Date(report.analysisDate).toLocaleDateString()}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Share2 className="mr-2 h-4 w-4" />
            Share
          </Button>
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* Perception Score Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-md font-medium">Perception Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center py-4">
              <div className="relative h-40 w-40">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-4xl font-bold">{report.perceptionScore}</div>
                </div>
                <svg className="h-full w-full" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="#e2e8f0"
                    strokeWidth="10"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="hsl(var(--accent))"
                    strokeWidth="10"
                    strokeDasharray={`${2 * Math.PI * 45 * report.perceptionScore / 100} ${2 * Math.PI * 45 * (100 - report.perceptionScore) / 100}`}
                    strokeLinecap="round"
                    transform="rotate(-90 50 50)"
                  />
                </svg>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* Sentiment Score Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-md font-medium">Sentiment Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(report.sentimentScore).map(([sentiment, score]) => (
                <div key={sentiment} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm capitalize">{sentiment}</span>
                    <span className="text-sm font-medium">{score}%</span>
                  </div>
                  <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                    <div
                      className={`h-full ${sentiment === 'positive' ? 'bg-green-500' : sentiment === 'negative' ? 'bg-red-500' : 'bg-yellow-500'}`}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        
        {/* Topics Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-md font-medium">Key Topics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {report.topics.map((topic) => (
                <div key={topic.name} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">{topic.name}</span>
                    <span className="text-sm font-medium">{topic.score}</span>
                  </div>
                  <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-accent"
                      style={{ width: `${topic.score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Additional report content would go here */}
    </MainLayout>
  );
};

export default ReportViewPage;
