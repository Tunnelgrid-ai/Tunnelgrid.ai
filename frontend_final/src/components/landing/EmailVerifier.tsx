
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";

export const EmailVerifier = () => {
  const [email, setEmail] = useState("");
  const [isChecking, setIsChecking] = useState(false);
  const [result, setResult] = useState<any>(null);

  const checkDirectly = async () => {
    setIsChecking(true);
    try {
      const normalizedEmail = email.toLowerCase().trim();
      
      // Check directly with Supabase client
      const { data: directData, error: directError } = await supabase
        .from("approved_emails")
        .select("*")
        .eq("email", normalizedEmail);
      
      if (directError) {
        console.error("Direct check error:", directError);
        toast({
          title: "Error",
          description: `Direct check failed: ${directError.message}`,
          variant: "destructive"
        });
        return;
      }
      
      setResult({
        directCheck: {
          exists: directData && directData.length > 0,
          data: directData
        }
      });
      
      // Now check using the edge function
      const { data: functionData, error: functionError } = await supabase.functions.invoke(
        "verify-email-exists",
        {
          body: { email: normalizedEmail }
        }
      );
      
      if (functionError) {
        console.error("Function check error:", functionError);
        setResult(prev => ({
          ...prev,
          functionCheck: {
            error: functionError
          }
        }));
        return;
      }
      
      setResult(prev => ({
        ...prev,
        functionCheck: functionData
      }));
      
      toast({
        title: "Check complete",
        description: directData && directData.length > 0 
          ? "Email found in database!" 
          : "Email NOT found in database",
        variant: directData && directData.length > 0 ? "default" : "destructive"
      });
      
    } catch (error) {
      console.error("Email verification error:", error);
      toast({
        title: "Error",
        description: `Verification failed: ${error.message}`,
        variant: "destructive"
      });
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <Card className="mt-4 w-full max-w-md">
      <CardHeader>
        <CardTitle>Email Verification Debugger</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2 mb-4">
          <Input 
            placeholder="Enter email to check"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Button onClick={checkDirectly} disabled={isChecking}>
            {isChecking ? "Checking..." : "Check"}
          </Button>
        </div>
        
        {result && (
          <div className="p-4 bg-muted rounded-md overflow-auto max-h-[300px]">
            <pre className="text-xs">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
