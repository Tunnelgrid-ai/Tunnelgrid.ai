
import { supabase } from "@/integrations/supabase/client";

export const useEmailApproval = () => {
  const checkEmailApproved = async (email: string): Promise<boolean> => {
    try {
      if (!email) {
        console.error("No email provided for approval check");
        return false;
      }
      
      // Ensure email is lowercase for case-insensitive comparison
      const normalizedEmail = email.toLowerCase().trim();
      console.log("Checking approval for email:", normalizedEmail);
      
      // First try with exact match
      let { data, error } = await supabase
        .from('approved_emails')
        .select('*')
        .eq('email', normalizedEmail);
      
      if (error) {
        console.error("Error checking approved email with eq:", error);
        return false;
      }
      
      // If no exact match found, try with ilike for case-insensitive matching
      if (!data || data.length === 0) {
        console.log("No exact match found, trying case-insensitive match");
        const { data: ilikeData, error: ilikeError } = await supabase
          .from('approved_emails')
          .select('*')
          .ilike('email', normalizedEmail);
        
        if (ilikeError) {
          console.error("Error checking approved email with ilike:", ilikeError);
          return false;
        }
        
        data = ilikeData;
      }
      
      const isApproved = data && data.length > 0;
      console.log("Email approval status:", isApproved);
      
      // If not approved, dump all approved emails for debugging
      if (!isApproved) {
        console.log("Email not found in approved list:", normalizedEmail);
        
        const { data: allEmails, error: allEmailsError } = await supabase
          .from('approved_emails')
          .select('email, id');
        
        if (!allEmailsError && allEmails) {
          console.log("All approved emails in database:", allEmails);
        } else if (allEmailsError) {
          console.error("Error fetching all emails:", allEmailsError);
        }
      } else {
        console.log("Email found in approved list!", data[0]);
      }
      
      return isApproved;
    } catch (error) {
      console.error("Error in checkEmailApproved:", error);
      return false;
    }
  };

  return { checkEmailApproved };
};
