
import React, { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { AuthTabs } from "@/components/landing/auth/AuthTabs";
import { Button } from "@/components/ui/button";
import { CheckCircle } from "lucide-react";

const AuthPage = () => {
  const { user, loading, signInWithOtp } = useAuth();
  const [authError, setAuthError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sentMagicLinkEmail, setSentMagicLinkEmail] = useState<string | null>(null);
  const navigate = useNavigate();

  // Handle login with magic link
  const handleLoginWithMagicLink = async (email: string) => {
    setAuthError(null);
    setSentMagicLinkEmail(email);
  };

  // Handle signup
  const handleSignup = async (email: string) => {
    setAuthError(null);
    setSentMagicLinkEmail(email);
  };

  // Handle resending magic link
  const handleResendLink = async () => {
    if (!sentMagicLinkEmail) return;
    
    setAuthError(null);
    setIsSubmitting(true);
    try {
      await signInWithOtp(sentMagicLinkEmail);
      setIsSubmitting(false);
    } catch (error: any) {
      setAuthError(error.message || "Failed to resend verification link");
      setIsSubmitting(false);
    }
  };

  // If already logged in, redirect to search page
  if (user && !loading) {
    return <Navigate to="/search" replace />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="text-2xl">Welcome</CardTitle>
          <CardDescription>
            {sentMagicLinkEmail ? "Verification link sent" : "Sign in or create a new account"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sentMagicLinkEmail ? (
            // Show confirmation message after magic link is sent
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <CheckCircle className="h-12 w-12 text-green-500" />
              </div>
              <p className="text-lg font-medium">Verification link sent!</p>
              <p className="text-muted-foreground">
                We've sent a magic link to <span className="font-medium">{sentMagicLinkEmail}</span>. 
                Please check your email and click the link to sign in.
              </p>
              <p className="text-sm text-muted-foreground">
                Didn't receive the email? Check your spam folder or try again.
              </p>
            </div>
          ) : (
            // Show login/signup tabs
            <AuthTabs
              onLoginSuccess={handleLoginWithMagicLink}
              onSignupSuccess={handleSignup}
              onError={(error) => setAuthError(error.message)}
            />
          )}
        </CardContent>
        {sentMagicLinkEmail && (
          <CardFooter className="flex flex-col space-y-2">
            <Button 
              variant="outline" 
              className="w-full" 
              onClick={() => setSentMagicLinkEmail(null)}
            >
              Back to Login
            </Button>
            <Button 
              variant="ghost" 
              className="w-full" 
              onClick={handleResendLink}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Sending..." : "Resend Link"}
            </Button>
          </CardFooter>
        )}
      </Card>
    </div>
  );
};

export default AuthPage;
