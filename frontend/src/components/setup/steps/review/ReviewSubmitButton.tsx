
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

export const ReviewSubmitButton = () => {
  return (
    <div className="flex justify-center pt-6">
      <Button asChild className="px-8">
        <Link to="/sandbox">
          Test Your Setup in Sandbox <ArrowRight className="ml-2 h-4 w-4" />
        </Link>
      </Button>
    </div>
  );
};
