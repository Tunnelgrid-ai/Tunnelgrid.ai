
import { ReactNode } from "react";
import { CheckCircle } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

interface ReviewAccordionItemProps {
  value: string;
  title: string;
  isComplete: boolean;
  children: ReactNode;
}

export const ReviewAccordionItem = ({
  value,
  title,
  isComplete,
  children,
}: ReviewAccordionItemProps) => {
  return (
    <AccordionItem value={value}>
      <AccordionTrigger className="flex items-center">
        <div className="flex items-center">
          <CheckCircle
            className={`mr-2 h-5 w-5 ${
              isComplete ? "text-green-500" : "text-gray-300"
            }`}
          />
          <span>{title}</span>
        </div>
      </AccordionTrigger>
      <AccordionContent>{children}</AccordionContent>
    </AccordionItem>
  );
};
