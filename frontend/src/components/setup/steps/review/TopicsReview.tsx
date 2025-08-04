import { Product, Topic } from "@/types/brandTypes";
import { EditBadge } from "./EditBadge";

interface TopicsReviewProps {
  topics: Topic[];
  products: Product[];
}

export const TopicsReview = ({ topics, products }: TopicsReviewProps) => {
  if (topics.length === 0) {
    return (
      <div className="text-center p-4 bg-card-dark rounded-md border border-black/20">
        <p className="text-text-secondary">No topics added yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {topics.map((topic) => (
        <div
          key={topic.id}
          className="border border-black/20 rounded-md p-4 bg-card-dark"
        >
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-semibold text-white">{topic.name}</h4>
            <EditBadge isEdited={topic.editedByUser} />
          </div>
          {topic.description && <p className="text-sm mt-1 text-text-secondary">{topic.description}</p>}
          
          {topic.products && topic.products.length > 0 && (
            <div className="mt-2">
              <h5 className="text-sm font-medium text-white">Related Products:</h5>
              <div className="flex flex-wrap gap-1 mt-1">
                {topic.products.map((productId) => {
                  const product = products.find((p) => p.id === productId);
                  return (
                    product && (
                      <span
                        key={productId}
                        className="bg-surface-dark px-2 py-0.5 rounded-md text-xs border border-black/20 text-text-secondary"
                      >
                        {product.name}
                      </span>
                    )
                  );
                })}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
