import { Product } from "@/types/brandTypes";

interface ProductsReviewProps {
  products: Product[];
}

export const ProductsReview = ({ products }: ProductsReviewProps) => {
  if (products.length === 0) {
    return (
      <div className="text-center p-4 bg-card-dark rounded-md border border-black/20">
        <p className="text-text-secondary">No products added yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {products.map((product) => (
        <div
          key={product.id}
          className="border border-black/20 rounded-md p-4 bg-card-dark"
        >
          <div>
            <h3 className="font-medium text-white">{product.name}</h3>
          </div>
          <div className="mt-2">
            <h5 className="text-sm font-medium text-white">Value Props:</h5>
            <div className="flex flex-wrap gap-1 mt-1">
              {product.valueProps.map((prop, index) => (
                <span
                  key={index}
                  className="bg-surface-dark px-2 py-0.5 rounded-md text-xs border border-black/20 text-text-secondary"
                >
                  {prop}
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
