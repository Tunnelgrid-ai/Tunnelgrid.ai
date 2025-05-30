import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { LoginForm } from "./auth/LoginForm";
import { toast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import { BookMeetingForm } from "./BookMeetingForm";
import { CheckCircle } from "lucide-react";
interface AuthDialogProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  defaultTab: 'login' | 'book';
}
export const AuthDialog = ({
  isOpen,
  onOpenChange,
  defaultTab = "login"
}: AuthDialogProps) => {
  const {
    signInWithOtp
  } = useAuth();
  const [authMode, setAuthMode] = useState<"login" | "book">(defaultTab);
  const [authError, setAuthError] = useState<string | null>(null);
  const [sentMagicLinkEmail, setSentMagicLinkEmail] = useState<string | null>(null);
  const navigate = useNavigate();

  // Update tab when defaultTab prop changes
  useEffect(() => {
    if (defaultTab) {
      setAuthMode(defaultTab);
    }
  }, [defaultTab]);

  // Reset states when dialog opens/closes
  useEffect(() => {
    if (!isOpen) {
      setAuthError(null);
      setSentMagicLinkEmail(null);
    }
  }, [isOpen]);
  const handleAuthSuccess = () => {
    onOpenChange(false); // Close dialog after successful login
    navigate("/search"); // Redirect to search page
  };
  const handleAuthError = (error: Error) => {
    setAuthError(error.message || "Authentication failed");
  };
  const handleLoginWithMagicLink = (email: string) => {
    setSentMagicLinkEmail(email);
    setAuthError(null);
  };
  const handleResendLink = async () => {
    if (!sentMagicLinkEmail) return;
    setAuthError(null);
    try {
      await signInWithOtp(sentMagicLinkEmail);
      toast({
        title: "Verification link resent",
        description: "Please check your email for the magic link"
      });
    } catch (error: any) {
      setAuthError(error.message || "Failed to resend verification link");
    }
  };
  const handleBookingSuccess = () => {
    toast({
      title: "Meeting request submitted",
      description: "We'll be in touch shortly to schedule your meeting."
    });
    onOpenChange(false); // Close dialog after successful booking
  };
  return <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        
        
        {sentMagicLinkEmail ?
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
            <div className="flex flex-col space-y-2 mt-4">
              <Button variant="outline" onClick={() => setSentMagicLinkEmail(null)}>
                Back to Login
              </Button>
              <Button variant="ghost" onClick={handleResendLink}>
                Resend Link
              </Button>
            </div>
          </div> : authMode === "book" ?
      // Book a meeting form
      <div className="space-y-6">
            <Button onClick={() => setAuthMode("login")} variant="ghost" className="mb-4">
              Back to Login
            </Button>
            
            <BookMeetingForm onSuccess={handleBookingSuccess} onBack={() => setAuthMode("login")} />
          </div> :
      // Login form
      <div className="space-y-6">
            {authError && <Alert variant="destructive" className="mb-6">
                <AlertDescription>{authError}</AlertDescription>
              </Alert>}

            <LoginForm onSuccess={handleLoginWithMagicLink} onError={handleAuthError} />
            
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  Or
                </span>
              </div>
            </div>
            
            <Button onClick={() => setAuthMode("book")} variant="outline" className="w-full">
              Book a Meeting
            </Button>
          </div>}
      </DialogContent>
    </Dialog>;
};