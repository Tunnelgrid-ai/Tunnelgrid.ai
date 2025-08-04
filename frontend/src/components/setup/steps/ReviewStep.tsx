import { BrandEntity, Persona, Product, Question, Topic } from "@/types/brandTypes";
import { Accordion } from "@/components/ui/accordion";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ReviewAccordionItem } from "./review/ReviewAccordionItem";
import { BrandInfoReview } from "./review/BrandInfoReview";
import { ProductsReview } from "./review/ProductsReview";
import { TopicsReview } from "./review/TopicsReview";
import { PersonasReview } from "./review/PersonasReview";
import { QuestionsReview } from "./review/QuestionsReview";
import { CheckCircle, Rocket } from "lucide-react";

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
        <h2 className="text-xl font-semibold mb-2 font-heading">Final Review Before Starting Your Audit</h2>
      </div>

      {/* Step Guidance */}
      <Alert className="border-accent/20 bg-accent/5">
        <Rocket className="h-4 w-4 text-accent" />
        <AlertDescription className="text-sm">
          <p> 
          Please confirm all details. Once submitted, your brand analysis will begin, and you can track visibility across AI systems.
          </p>
        </AlertDescription>
      </Alert>

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
