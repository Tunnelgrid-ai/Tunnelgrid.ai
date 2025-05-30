
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

// Mock data for example responses
const mockResponses: Record<string, string> = {
  default: "Try typing a prompt about your brand to see how different AI models would respond.",
  "Tell me about TechPulse": 
    "TechPulse is a technology company that specializes in innovative software solutions for businesses. They are known for their user-friendly interfaces and robust backend systems that help companies streamline their operations and improve productivity. TechPulse has received positive reviews for their customer service and ongoing product development.",
  "What are TechPulse's best products?":
    "TechPulse offers several highly regarded products, with their flagship being PulseFlow, an integrated project management system. Their TechSync data integration platform is also popular among enterprise clients. Recently, they've launched PulseDash, an analytics dashboard solution that's gaining traction in the market for its intuitive design and powerful visualization capabilities."
};

export const PromptSandbox = () => {
  const [prompt, setPrompt] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [responses, setResponses] = useState<Record<string, string>>({
    openai: "",
    perplexity: "",
    claude: "",
  });

  const handlePromptTest = () => {
    setIsProcessing(true);
    
    // Simulate API call delay
    setTimeout(() => {
      // Get mock response based on prompt or use default
      const mockResponse = prompt.toLowerCase().includes("techpulse") 
        ? (mockResponses[prompt] || mockResponses.default)
        : mockResponses.default;
      
      // Set slightly different responses for different models
      setResponses({
        openai: mockResponse,
        perplexity: mockResponse + " The company was founded in 2015 and has offices in San Francisco and London.",
        claude: mockResponse + " Their commitment to innovation has positioned them as a leader in their industry segment.",
      });
      setIsProcessing(false);
    }, 1500);
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold">Prompt Testing Sandbox</h2>
        <p className="text-muted-foreground mt-2">
          Test how different AI models respond to prompts about your brand
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Test Your Prompt</CardTitle>
          <CardDescription>
            Enter a prompt to see how AI models would respond when asked about your brand
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea
            placeholder="E.g., 'Tell me about TechPulse' or 'What are TechPulse's best products?'"
            className="min-h-[100px]"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
        </CardContent>
        <CardFooter>
          <Button 
            onClick={handlePromptTest} 
            disabled={isProcessing || !prompt.trim()}
            className="ml-auto"
          >
            {isProcessing ? "Processing..." : "Test Prompt"}
          </Button>
        </CardFooter>
      </Card>

      {(responses.openai || isProcessing) && (
        <Card>
          <CardHeader>
            <CardTitle>AI Responses</CardTitle>
            <CardDescription>
              How different AI models respond to your prompt
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="openai">
              <TabsList className="mb-4">
                <TabsTrigger value="openai">OpenAI</TabsTrigger>
                <TabsTrigger value="perplexity">Perplexity</TabsTrigger>
                <TabsTrigger value="claude">Claude</TabsTrigger>
              </TabsList>
              <TabsContent value="openai" className="mt-0">
                <div className="p-4 bg-slate-50 rounded-md min-h-[100px]">
                  {isProcessing ? (
                    <p className="text-muted-foreground">Processing...</p>
                  ) : (
                    <p>{responses.openai}</p>
                  )}
                </div>
              </TabsContent>
              <TabsContent value="perplexity" className="mt-0">
                <div className="p-4 bg-slate-50 rounded-md min-h-[100px]">
                  {isProcessing ? (
                    <p className="text-muted-foreground">Processing...</p>
                  ) : (
                    <p>{responses.perplexity}</p>
                  )}
                </div>
              </TabsContent>
              <TabsContent value="claude" className="mt-0">
                <div className="p-4 bg-slate-50 rounded-md min-h-[100px]">
                  {isProcessing ? (
                    <p className="text-muted-foreground">Processing...</p>
                  ) : (
                    <p>{responses.claude}</p>
                  )}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
