
import { useState } from "react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FileText } from "lucide-react";

interface Report {
  id: string;
  brandName: string;
  product: string;
  createdAt: string;
}

const MyReportsPage = () => {
  const navigate = useNavigate();
  // This will be empty for now, but would be populated with actual reports data from an API
  const [reports, setReports] = useState<Report[]>([]);
  
  const handleViewReport = (reportId: string) => {
    navigate(`/reports/${reportId}`);
  };

  const handleStartAudit = () => {
    navigate("/search");
  };
  
  return (
    <MainLayout>
      <div className="container px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">My Reports</h1>
        
        {reports.length > 0 ? (
          <div className="rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Brand</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reports.map((report) => (
                  <TableRow key={report.id}>
                    <TableCell className="font-medium">{report.brandName}</TableCell>
                    <TableCell>{report.product}</TableCell>
                    <TableCell>{new Date(report.createdAt).toLocaleDateString()}</TableCell>
                    <TableCell className="text-right">
                      <Button 
                        onClick={() => handleViewReport(report.id)}
                        size="sm"
                      >
                        View Report
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
              <FileText className="h-8 w-8 text-muted-foreground" />
            </div>
            <h2 className="text-xl font-semibold mb-2">No reports yet</h2>
            <p className="text-muted-foreground max-w-md mb-8">
              You haven't run any audits yet. Start your first brand audit to see your results here.
            </p>
            <Button onClick={handleStartAudit} className="bg-accent hover:bg-accent/90 text-accent-foreground">
              Run Brand Audit
            </Button>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default MyReportsPage;
