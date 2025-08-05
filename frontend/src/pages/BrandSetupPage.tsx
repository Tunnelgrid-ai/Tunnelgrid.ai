import { useEffect } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { MainLayout } from "@/components/layout/MainLayout";
import { BrandSetupWizard } from "@/components/setup/BrandSetupWizard";

const BrandSetupPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { studyId } = useParams(); // NEW: Get studyId from URL params

  // Check if we have a brand from navigation or if we're editing a study
  useEffect(() => {
    if (!location.state?.selectedBrand && !location.state?.manualSetup && !studyId) {
      // Redirect to home if no brand is selected, not in manual setup mode, and no studyId
      navigate("/");
    }
  }, [location.state, navigate, studyId]);

  // Get the data from navigation state
  const { selectedBrand, description } = location.state || {};

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto py-8 px-4">
        <h1 className="text-3xl font-heading font-bold mb-6 text-white tracking-tight bg-gradient-to-r from-brand-blue via-brand-purple to-brand-cyan bg-clip-text text-transparent">
          {studyId ? 'Edit Study' : 'Brand Setup'}
        </h1>
        
        <div className="relative">
          {/* Grid background overlay */}
          <div className="absolute inset-0 grid-background opacity-[0.06] rounded-lg pointer-events-none"></div>
          <BrandSetupWizard
            brand={selectedBrand}
            brandDescription={description}
            studyId={studyId} // NEW: Pass studyId to wizard
          />
        </div>
      </div>
    </MainLayout>
  );
};

export default BrandSetupPage;
