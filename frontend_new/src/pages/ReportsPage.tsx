
import { useState } from "react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

interface Report {
  id: string;
  brandName: string;
  brandLogo?: string;
  analysisDate: string;
}

// Mock data for reports
const mockReports: Report[] = [
  {
    id: "report-1",
    brandName: "Nike",
    brandLogo: "https://placehold.co/100x100?text=Nike",
    analysisDate: "2025-04-30"
  },
  {
    id: "report-2",
    brandName: "Adidas",
    brandLogo: "https://placehold.co/100x100?text=Adidas",
    analysisDate: "2025-04-28"
  },
  {
    id: "report-3",
    brandName: "TechPulse",
    brandLogo: "https://placehold.co/100x100?text=TP",
    analysisDate: "2025-04-25"
  },
  {
    id: "report-4",
    brandName: "EcoSmart",
    brandLogo: "https://placehold.co/100x100?text=Eco",
    analysisDate: "2025-04-22"
  }
];

const ReportsPage = () => {
  const navigate = useNavigate();
  
  const handleViewReport = (reportId: string) => {
    navigate(`/reports/${reportId}`);
  };
  
  return (
    <MainLayout>
      <div className="container px-0">
        <h1 className="text-3xl font-bold mb-8">Brand Reports</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockReports.map((report) => (
            <Card key={report.id} className="overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-12 h-12 bg-slate-100 rounded-md flex items-center justify-center overflow-hidden">
                    {report.brandLogo ? (
                      <img src={report.brandLogo} alt={report.brandName} className="w-full h-full object-cover" />
                    ) : (
                      <span className="text-xl font-medium">{report.brandName.substring(0, 2)}</span>
                    )}
                  </div>
                  <div>
                    <h3 className="font-medium text-lg">{report.brandName}</h3>
                    <p className="text-sm text-muted-foreground">
                      Analysis from {new Date(report.analysisDate).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                
                <Button 
                  onClick={() => handleViewReport(report.id)} 
                  className="w-full"
                >
                  View Report
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </MainLayout>
  );
};

export default ReportsPage;
