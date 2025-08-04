import { BrandEntity } from "@/types/brandTypes";
import { EditBadge } from "./EditBadge";

interface BrandInfoReviewProps {
  brandInfo: BrandEntity;
  selectedProductName?: string;
}

export const BrandInfoReview = ({ brandInfo, selectedProductName }: BrandInfoReviewProps) => {
  return (
    <div className="space-y-4 p-4 rounded-md bg-card-dark border border-black/20">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h4 className="font-medium text-white">Brand Name</h4>
          <p className="text-text-secondary">{brandInfo.name || "Not set"}</p>
        </div>
      </div>

      <div>
        <h4 className="font-medium text-white">Domain</h4>
        <p className="text-text-secondary">{brandInfo.website || "Not set"}</p>
      </div>

      {brandInfo.description && (
        <div>
          <div className="flex items-center justify-between mb-1">
            <h4 className="font-medium text-white">Description</h4>
            <EditBadge isEdited={brandInfo.editedByUser} />
          </div>
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
