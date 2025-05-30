import { BrandEntity } from "@/types/brandTypes";

interface BrandInfoReviewProps {
  brandInfo: BrandEntity;
  selectedProductName?: string;
}

export const BrandInfoReview = ({ brandInfo, selectedProductName }: BrandInfoReviewProps) => {
  return (
    <div className="space-y-4 p-4 rounded-md bg-card-dark border border-black/20">
      <div>
        <h4 className="font-medium text-white">Brand Name</h4>
        <p className="text-text-secondary">{brandInfo.name || "Not set"}</p>
      </div>

      <div>
        <h4 className="font-medium text-white">Domain</h4>
        <p className="text-text-secondary">{brandInfo.website || "Not set"}</p>
      </div>

      {brandInfo.description && (
        <div>
          <h4 className="font-medium text-white">Description</h4>
          <p className="text-text-secondary">{brandInfo.description}</p>
        </div>
      )}

      {selectedProductName && (
        <div>
          <h4 className="font-medium text-white">Selected Product</h4>
          <p className="text-text-secondary">{selectedProductName}</p>
        </div>
      )}
    </div>
  );
};
