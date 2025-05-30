import React from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { AuthProvider } from "@/contexts/auth";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import BrandSetupPage from "./pages/BrandSetupPage";
import BrandSearchPage from "./pages/BrandSearchPage";
import ReportsPage from "./pages/ReportsPage";
import ReportViewPage from "./pages/ReportViewPage";
import SettingsPage from "./pages/SettingsPage";
import AuthPage from "./pages/AuthPage";
import MyReportsPage from "./pages/MyReportsPage";

const queryClient = new QueryClient();

// Redirect component for Auth page
const AuthRedirect = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const tab = searchParams.get('tab');
  
  // Navigate to home with state to trigger auth dialog
  React.useEffect(() => {
    navigate('/', { 
      state: { 
        openAuthDialog: true, 
        authTab: tab === 'book' ? 'book' : 'login' 
      } 
    });
  }, [navigate, tab]);
  
  return null;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <AuthProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/setup" element={<BrandSetupPage />} />
            <Route path="/search" element={<BrandSearchPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/reports/:reportId" element={<ReportViewPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/my-reports" element={<MyReportsPage />} />
            <Route path="/auth" element={<AuthRedirect />} />
            {/* Redirect /audit to /search */}
            <Route path="/audit" element={<Navigate replace to="/search" />} />
            {/* Catch-all route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
