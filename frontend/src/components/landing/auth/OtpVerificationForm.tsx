
import React from "react";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "@/components/ui/form";
import { 
  InputOTP,
  InputOTPGroup,
  InputOTPSlot
} from "@/components/ui/input-otp";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ArrowLeft, Check } from "lucide-react";

const otpSchema = z.object({
  otp: z.string().min(6, "Please enter the complete verification code")
});

interface OtpVerificationFormProps {
  email: string;
  onSuccess: () => void;
  onError: (error: Error) => void;
  onBack: () => void;
  onResend: () => void;
}

export const OtpVerificationForm = ({
  email,
  onSuccess,
  onError,
  onBack,
  onResend
}: OtpVerificationFormProps) => {
  const { verifyOtp } = useAuth();
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [otpError, setOtpError] = React.useState<string | null>(null);

  const form = useForm<z.infer<typeof otpSchema>>({
    resolver: zodResolver(otpSchema),
    defaultValues: {
      otp: ""
    }
  });

  const handleVerify = async (values: z.infer<typeof otpSchema>) => {
    setIsSubmitting(true);
    setOtpError(null);
    try {
      await verifyOtp(email, values.otp);
      onSuccess();
    } catch (error: any) {
      setOtpError(error.message || "Verification failed");
      onError(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="mb-4">
        <Button 
          type="button" 
          variant="ghost" 
          onClick={onBack} 
          className="p-0 h-auto flex items-center text-sm text-primary"
        >
          <ArrowLeft className="mr-1 h-4 w-4" />
          Back
        </Button>
      </div>

      <div className="flex flex-col items-center mb-6">
        <div className="rounded-full bg-primary/10 p-3 mb-4">
          <Check className="h-6 w-6 text-primary" />
        </div>
        <h2 className="text-xl font-semibold text-center">Verify Your Email</h2>
        <p className="text-sm text-center text-muted-foreground mt-2">
          We've sent a verification code to<br />
          <span className="font-medium text-foreground">{email}</span>
        </p>
      </div>

      {otpError && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{otpError}</AlertDescription>
        </Alert>
      )}

      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleVerify)} className="space-y-4">
          <FormField
            control={form.control}
            name="otp"
            render={({ field }) => (
              <FormItem className="mx-auto max-w-[300px]">
                <FormLabel className="text-center w-full block">Enter verification code</FormLabel>
                <FormControl>
                  <InputOTP maxLength={6} {...field}>
                    <InputOTPGroup>
                      <InputOTPSlot index={0} />
                      <InputOTPSlot index={1} />
                      <InputOTPSlot index={2} />
                      <InputOTPSlot index={3} />
                      <InputOTPSlot index={4} />
                      <InputOTPSlot index={5} />
                    </InputOTPGroup>
                  </InputOTP>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="flex flex-col gap-4 mt-6">
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "Verifying..." : "Verify & Sign In"}
            </Button>
            
            <Button type="button" variant="ghost" onClick={onResend} className="w-full">
              Resend Code
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
};
