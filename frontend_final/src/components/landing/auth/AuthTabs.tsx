
import React, { useState } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { LoginForm } from "./LoginForm";
import { SignupForm } from "./SignupForm";

interface AuthTabsProps {
  onLoginSuccess: (email: string) => void;
  onSignupSuccess: (email: string) => void;
  onError: (error: Error) => void;
}

export const AuthTabs = ({ onLoginSuccess, onSignupSuccess, onError }: AuthTabsProps) => {
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [authError, setAuthError] = useState<string | null>(null);

  const handleError = (error: Error) => {
    setAuthError(error.message);
    onError(error);
  };

  return (
    <Tabs 
      defaultValue="login" 
      value={authMode} 
      onValueChange={(value) => setAuthMode(value as "login" | "signup")}
    >
      <TabsList className="grid w-full grid-cols-2 mb-6">
        <TabsTrigger value="login">Login</TabsTrigger>
        <TabsTrigger value="signup">Sign Up</TabsTrigger>
      </TabsList>
      
      {authError && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{authError}</AlertDescription>
        </Alert>
      )}

      <TabsContent value="login">
        <LoginForm
          onSuccess={onLoginSuccess}
          onError={handleError}
        />
      </TabsContent>
      
      <TabsContent value="signup">
        <SignupForm
          onSuccess={onSignupSuccess}
          onError={handleError}
        />
      </TabsContent>
    </Tabs>
  );
};
