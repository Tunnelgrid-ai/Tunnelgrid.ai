
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";

export const useAuthActions = () => {
  const { toast } = useToast();

  const signUp = async (email: string, userData?: { full_name?: string }) => {
    try {
      // Use Supabase's native signInWithOtp with appropriate options
      const { data, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          data: userData,
          emailRedirectTo: window.location.origin, // Add redirect URL to fix magic link
        }
      });

      if (error) {
        console.error("Supabase OTP error:", error);
        throw error;
      }

      toast({
        title: "Verification link sent",
        description: "Please check your email for the login link.",
      });
    } catch (error: any) {
      console.error("Sign up error:", error);
      toast({
        title: "Sign up failed",
        description: error.message,
        variant: "destructive",
      });
      throw error;
    }
  };

  const signInWithOtp = async (email: string) => {
    try {
      // Directly use Supabase's native signInWithOtp without custom email verification
      const { data, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          shouldCreateUser: false, // Only allow existing users to sign in
          emailRedirectTo: window.location.origin, // Add redirect URL to fix magic link
        }
      });

      if (error) {
        console.error("Supabase OTP error:", error);
        throw error;
      }

      toast({
        title: "Verification link sent",
        description: "Please check your email for the login link.",
      });
    } catch (error: any) {
      console.error("Sign in error:", error);
      // Provide a more user-friendly error message for non-existing users
      if (error.message?.includes("User not found") || 
          error.message?.includes("Email not found")) {
        toast({
          title: "Account not found",
          description: "No account exists with this email address.",
          variant: "destructive",
        });
      } else {
        toast({
          title: "Sign in failed",
          description: error.message,
          variant: "destructive",
        });
      }
      throw error;
    }
  };

  const verifyOtp = async (email: string, token: string) => {
    try {
      console.log("Verifying OTP for email:", email);
      const { data, error } = await supabase.auth.verifyOtp({
        email,
        token,
        type: 'email'
      });

      if (error) {
        console.error("OTP verification error:", error);
        throw error;
      }

      console.log("OTP verification successful", data);
      toast({
        title: "Signed in successfully",
      });
    } catch (error: any) {
      console.error("Verification error:", error);
      toast({
        title: "Verification failed",
        description: error.message,
        variant: "destructive",
      });
      throw error;
    }
  };

  const signOut = async () => {
    try {
      await supabase.auth.signOut();
      toast({
        title: "Signed out successfully",
      });
    } catch (error: any) {
      toast({
        title: "Sign out failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  return {
    signUp,
    signInWithOtp,
    verifyOtp,
    signOut
  };
};
