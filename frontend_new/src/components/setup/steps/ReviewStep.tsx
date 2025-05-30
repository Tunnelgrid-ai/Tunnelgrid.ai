import { BrandEntity, Persona, Product, Question, Topic } from "@/types/brandTypes";
import { Accordion } from "@/components/ui/accordion";
import { ReviewAccordionItem } from "./review/ReviewAccordionItem";
import { BrandInfoReview } from "./review/BrandInfoReview";
import { ProductsReview } from "./review/ProductsReview";
import { TopicsReview } from "./review/TopicsReview";
import { PersonasReview } from "./review/PersonasReview";
import { QuestionsReview } from "./review/QuestionsReview";

interface ReviewStepProps {
  brandInfo: BrandEntity;
  products: Product[];
  topics: Topic[];
  personas: Persona[];
  questions: Question[];
}

export const ReviewStep = ({
  brandInfo,
  products,
  topics,
  personas,
  questions,
}: ReviewStepProps) => {
  // Get the selected product name (assuming first product is selected)
  const selectedProductName = products.length > 0 ? products[0].name : undefined;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-2 font-heading">Review Your Setup</h2>
        <p className="text-text-secondary">
          Review all the information you've provided before submitting.
        </p>
      </div>

      <div className="space-y-6">
        <Accordion type="single" collapsible className="w-full">
          <ReviewAccordionItem 
            value="brandInfo" 
            title="Brand Information" 
            isComplete={!!(brandInfo.name && brandInfo.website)}
          >
            <BrandInfoReview 
              brandInfo={brandInfo} 
              selectedProductName={selectedProductName}
            />
          </ReviewAccordionItem>

          <ReviewAccordionItem 
            value="topics" 
            title="Topics" 
            isComplete={topics.length > 0}
          >
            <TopicsReview topics={topics} products={products} />
          </ReviewAccordionItem>

          <ReviewAccordionItem 
            value="personas" 
            title="Personas" 
            isComplete={personas.length > 0}
          >
            <PersonasReview personas={personas} topics={topics} products={products} />
          </ReviewAccordionItem>

          <ReviewAccordionItem 
            value="questions" 
            title="Questions" 
            isComplete={questions.length > 0}
          >
            <QuestionsReview questions={questions} personas={personas} />
          </ReviewAccordionItem>
        </Accordion>
      </div>
    </div>
  );
};
