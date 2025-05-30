
import { serve } from "https://deno.land/std@0.190.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const sendEmail = async (meetingData: any) => {
  const { full_name, email, company, message } = meetingData;
  
  // Format the message for email
  const emailBody = `
    New Meeting Request:
    
    Name: ${full_name}
    Email: ${email}
    Company: ${company}
    Message: ${message || "No message provided"}
    
    This request was submitted on ${new Date().toLocaleString()}.
  `;
  
  try {
    // Send email using Supabase edge function or a simple email service
    // For this example, we'll log it - you would replace this with your email service
    console.log("SENDING EMAIL:", emailBody);
    
    // Here you would typically call your email service
    // Example: await fetch('https://api.youremailprovider.com', {...})
    
    return { success: true };
  } catch (error) {
    console.error("Failed to send email:", error);
    return { success: false, error };
  }
};

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_ANON_KEY") ?? ""
    );

    const { meetingData } = await req.json();
    
    // Store in database
    const { error: dbError } = await supabaseClient
      .from('meeting_requests')
      .insert([meetingData]);

    if (dbError) {
      throw new Error(`Database error: ${dbError.message}`);
    }

    // Send email notification
    const emailResult = await sendEmail(meetingData);

    return new Response(
      JSON.stringify({ success: true, emailSent: emailResult.success }),
      { 
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 200 
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 400 
      }
    );
  }
});
