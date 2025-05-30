
// This edge function will check if an email exists in the approved_emails table
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.23.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_ANON_KEY") ?? ""
    );

    // Get the email from request
    const { email } = await req.json();
    
    if (!email) {
      return new Response(
        JSON.stringify({ error: "Email is required" }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" }, status: 400 }
      );
    }

    // Check if email exists in approved_emails table with exact match
    const { data: exactMatch, error: exactError } = await supabaseClient
      .from("approved_emails")
      .select("*")
      .eq("email", email.toLowerCase().trim());

    if (exactError) {
      return new Response(
        JSON.stringify({ error: "Error checking exact match", details: exactError }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" }, status: 500 }
      );
    }

    // Check with ilike for case-insensitive match
    const { data: ilikeMatch, error: ilikeError } = await supabaseClient
      .from("approved_emails")
      .select("*")
      .ilike("email", email.toLowerCase().trim());

    if (ilikeError) {
      return new Response(
        JSON.stringify({ error: "Error checking case-insensitive match", details: ilikeError }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" }, status: 500 }
      );
    }

    // Get all emails for debugging
    const { data: allEmails, error: allError } = await supabaseClient
      .from("approved_emails")
      .select("email, id");

    return new Response(
      JSON.stringify({
        exists: exactMatch && exactMatch.length > 0,
        existsIlike: ilikeMatch && ilikeMatch.length > 0,
        exactMatch,
        ilikeMatch,
        allEmails,
        email: email.toLowerCase().trim()
      }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" }, status: 200 }
    );

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" }, status: 500 }
    );
  }
});
