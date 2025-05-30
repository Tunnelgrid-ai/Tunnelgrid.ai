/**
 * AUDIT SERVICE - SIMPLIFIED VERSION WITH PRODUCT CREATION
 * 
 * This service handles creating audit entries when users start a brand analysis.
 * Now includes automatic product creation to avoid foreign key violations.
 * 
 * DEVELOPMENT MODE: 
 * - When no user is authenticated, uses a fake user ID for testing
 * - This allows development/testing without setting up authentication
 * - Clear console logging indicates when this workaround is active
 * 
 * USER FLOW CONTEXT:
 * 1. User searches for a brand → gets brand_id from search results
 * 2. User lands on Brand Info Step → sees brand details and products
 * 3. User selects a product → we have product_id
 * 4. User clicks "Next" → THIS IS WHERE WE CREATE THE AUDIT ENTRY
 * 
 * Why we need this:
 * - An audit represents one complete analysis session
 * - It tracks which brand + product combination is being analyzed
 * - It allows us to track progress (in-progress → complete)
 * - It connects all generated data (topics, personas, etc.) to this specific analysis
 */

import { supabase } from "@/integrations/supabase/client";
import { v4 as uuidv4 } from 'uuid';

/**
 * TYPE DEFINITION: Audit Service Response
 * 
 * Standardized response format for all audit service operations
 * Provides consistent error handling and success feedback
 */
interface AuditServiceResponse<T = any> {
  success: boolean;
  data?: T;                      // Response data (if successful)
  error?: string;                // Error message (if failed)
}

/**
 * DEVELOPMENT CONFIGURATION
 * 
 * Set this to true during development to enable testing without authentication
 * Set to false in production to require real user authentication
 */
const DEV_MODE = true;  // TODO: Set to false in production

/**
 * DEVELOPMENT FAKE USER ID
 * 
 * This is used when DEV_MODE is true and no real user is authenticated
 * Allows testing the audit creation flow without setting up authentication
 */
const DEV_FAKE_USER_ID = "72f7b6f6-ce78-41dd-a691-44d1ff8f7a01"; // Valid test user UUID

/**
 * TYPE DEFINITION: CreateAuditRequest
 * 
 * This defines exactly what information we need to create a new audit:
 * - brandId: The UUID of the brand from the brands table (passed from search step)
 * - productId: The UUID of the selected product from the products table
 * - userId: The UUID of the current user (for tracking who initiated this audit)
 *           In DEV_MODE, this can be our fake user ID
 */
export interface CreateAuditRequest {
  brandId: string;
  productId: string;
  userId: string;
  productName?: string; // Optional: product name to ensure it exists in database
}

/**
 * TYPE DEFINITION: AuditResponse
 * 
 * Response from createAudit function
 * Includes success status, audit ID, and development mode information
 */
export interface AuditResponse extends AuditServiceResponse {
  auditId?: string;              // The ID of the created audit
  actualProductId?: string;      // The actual product ID from database (may differ from request)
  devMode?: boolean;             // Whether dev mode was used for user ID
}

/**
 * HELPER FUNCTION: getValidUserId
 * 
 * PURPOSE: Handles user ID validation with development workaround
 * 
 * LOGIC:
 * 1. If real user ID provided → use it
 * 2. If no user ID and DEV_MODE is true → use fake ID
 * 3. If no user ID and DEV_MODE is false → return null (error)
 * 
 * @param userId - The user ID from authentication (can be null/undefined)
 * @returns Object with validUserId and whether dev mode was used
 */
export function getValidUserId(userId?: string | null): { 
  validUserId: string | null; 
  usingDevMode: boolean; 
} {
  // Case 1: Real user ID provided
  if (userId) {
    console.log('✅ Using authenticated user ID:', userId);
    return { 
      validUserId: userId, 
      usingDevMode: false 
    };
  }

  // Case 2: No user ID, but development mode enabled
  if (DEV_MODE) {
    console.warn('🚧 DEVELOPMENT MODE: Using fake user ID for testing');
    console.warn('🚧 Real user ID was:', userId);
    console.warn('🚧 Using fake user ID:', DEV_FAKE_USER_ID);
    console.warn('🚧 Remember to set DEV_MODE = false in production!');
    return { 
      validUserId: DEV_FAKE_USER_ID, 
      usingDevMode: true 
    };
  }

  // Case 3: No user ID and production mode
  console.error('❌ No user ID provided and DEV_MODE is disabled');
  return { 
    validUserId: null, 
    usingDevMode: false 
  };
}

/**
 * HELPER FUNCTION: ensureProductExists
 * 
 * PURPOSE: Ensure a product exists in the database before creating audit
 * If the product doesn't exist, create it first
 * 
 * @param brandId - The brand ID that owns this product
 * @param productId - The frontend-generated product ID
 * @param productName - The name of the product
 * @returns Promise with the actual database product ID
 */
export async function ensureProductExists(brandId: string, productId: string, productName: string): Promise<string> {
  try {
    console.log('📝 Ensuring product exists:', { brandId, productId, productName });
    
    const response = await fetch('/api/products/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        product_name: productName,
        brand_id: brandId
      }),
    });

    if (response.ok) {
      const result = await response.json();
      console.log('✅ Product created in database:', result);
      const createdProductId = result.data?.product_id;
      if (createdProductId) {
        console.log('✅ Using backend product ID:', createdProductId);
        return createdProductId;
      } else {
        console.warn('⚠️ Product created but no product_id in response, using frontend ID:', productId);
        return productId;
      }
    } else {
      console.warn('⚠️ Product creation failed, using frontend ID:', productId);
      return productId;
    }

  } catch (error) {
    console.warn('⚠️ Error ensuring product exists, using frontend ID:', error);
    return productId;
  }
}

/**
 * MAIN FUNCTION: createAudit
 * 
 * PURPOSE: Creates a new audit entry via backend API to bypass RLS
 * 
 * NEW APPROACH: Instead of calling Supabase directly from frontend,
 * we call our backend API which uses service role key to bypass RLS
 */
export async function createAudit(request: CreateAuditRequest): Promise<AuditResponse> {
  try {
    console.log('🔍 createAudit called with request:', {
      brandId: request.brandId,
      productId: request.productId,
      userId: request.userId,
      productName: request.productName
    });

    // STEP 1: Validate user ID
    const { validUserId, usingDevMode } = getValidUserId(request.userId);
    
    if (!validUserId) {
      return {
        success: false,
        error: 'User authentication required. Please log in to continue.',
        devMode: false
      };
    }

    // STEP 2: Validate required fields
    if (!request.brandId || request.brandId.trim() === '') {
      console.error('❌ Missing brand ID');
      return {
        success: false,
        error: 'Brand ID is required',
        devMode: false
      };
    }

    // STEP 3: Ensure product exists if product name provided
    let actualProductId = request.productId;
    console.log('🔍 Initial product ID:', actualProductId);
    
    if (request.productName && request.productName.trim() !== '') {
      console.log('📝 Product name provided, ensuring product exists...');
      actualProductId = await ensureProductExists(
        request.brandId, 
        request.productId, 
        request.productName
      );
      console.log('📝 Product ID after ensureProductExists:', actualProductId);
    }

    // STEP 4: Final validation of product ID
    if (!actualProductId || actualProductId.trim() === '') {
      console.error('❌ No valid product ID available');
      return {
        success: false,
        error: 'Product ID is required. Please select a product.',
        devMode: false
      };
    }

    // STEP 5: Make API request to create audit
    console.log('📝 Making audit creation request to backend...');
    
    const response = await fetch('/api/audits/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        brand_id: request.brandId,
        product_id: actualProductId,
        user_id: validUserId,
        product_name: request.productName
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Audit creation failed:', response.status, errorText);
      return {
        success: false,
        error: `Audit creation failed: ${response.status} ${errorText}`,
        devMode: usingDevMode
      };
    }

    const result = await response.json();
    console.log('✅ Audit creation response:', result);

    // STEP 6: Return success response with audit ID and actual product ID
    console.log('🎉 Audit created successfully!');
    
    return {
      success: true,
      auditId: result.data?.audit_id || result.auditId,
      actualProductId: result.data?.product_id || actualProductId,  // Return the actual product ID used
      devMode: usingDevMode
    };

  } catch (error) {
    // STEP 7: Handle any unexpected errors
    console.error('Unexpected error creating audit:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      devMode: false
    };
  }
}

/**
 * HELPER FUNCTION: updateAuditStatus
 * 
 * PURPOSE: Updates the status of an existing audit
 * 
 * WHEN THIS IS USED:
 * - When the entire analysis is complete (topics, personas, questions generated)
 * - When an audit fails and needs to be marked as 'failed'
 * 
 * DATABASE NOTE: 
 * - Uses 'audit' table (singular)
 * - Primary key is 'audit_id' not 'id'
 * - No 'updated_at' column exists, we only track 'created_timestamp'
 * 
 * @param auditId - The ID of the audit to update
 * @param status - New status ('completed', 'failed', etc.)
 */
export async function updateAuditStatus(auditId: string, status: string): Promise<boolean> {
  try {
    // Update the audit record with the new status
    // Note: Using correct table name 'audit' and column name 'audit_id'
    const { error } = await supabase
      .from('audit')                    // Correct table name (singular)
      .update({ 
        status: status                  // Update only the status field
        // Note: No updated_at field exists in this table schema
      })
      .eq('audit_id', auditId);         // Find the specific audit by its audit_id

    if (error) {
      console.error('Failed to update audit status:', error);
      return false;
    }

    console.log(`✅ Audit ${auditId} status updated to: ${status}`);
    return true;

  } catch (error) {
    console.error('Unexpected error updating audit status:', error);
    return false;
  }
}

/**
 * FUNCTION: Complete Audit
 * 
 * PURPOSE: Mark audit as 'completed' when user finishes the entire wizard
 * 
 * BUSINESS LOGIC:
 * - Called when user reaches the review step and submits
 * - Updates audit status from 'in_progress' to 'completed'
 * - Records completion timestamp for analytics
 * 
 * USAGE: Called from wizard's final submission process
 * 
 * @param auditId - ID of audit to mark as completed
 * @returns Promise with success/error status
 */
export async function completeAudit(auditId: string): Promise<AuditServiceResponse> {
  // DEV MODE CHECK: Works with fake or real user ID
  if (DEV_MODE) {
    console.log('🛠️ DEV MODE: Completing audit with development settings');
  }

  try {
    // VALIDATION: Check audit ID
    if (!auditId || auditId.trim() === '') {
      return {
        success: false,
        error: 'Audit ID is required'
      };
    }

    console.log('✅ Completing audit:', auditId);

    // UPDATE: Set audit status to completed
    const { data, error } = await supabase
      .from('audit')
      .update({ 
        status: 'completed',
        // Note: completion timestamp will be auto-updated if you have updated_at trigger
      })
      .eq('audit_id', auditId)
      .select()
      .single();

    if (error) {
      console.error('❌ Failed to complete audit:', error);
      return {
        success: false,
        error: `Database error: ${error.message}`
      };
    }

    if (!data) {
      return {
        success: false,
        error: 'Audit not found'
      };
    }

    console.log('✅ Audit completed successfully:', data.audit_id);

    return {
      success: true,
      data: data.audit_id
    };

  } catch (error) {
    console.error('💥 Unexpected error completing audit:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}

/**
 * FUNCTION: Get Audit Status
 * 
 * PURPOSE: Check current status of an audit
 * 
 * USAGE: Can be used to validate audit state before operations
 * 
 * @param auditId - ID of audit to check
 * @returns Promise with audit status information
 */
export async function getAuditStatus(auditId: string): Promise<AuditServiceResponse<{ status: string; created_timestamp: string }>> {
  try {
    if (!auditId || auditId.trim() === '') {
      return {
        success: false,
        error: 'Audit ID is required'
      };
    }

    const { data, error } = await supabase
      .from('audit')
      .select('status, created_timestamp')
      .eq('audit_id', auditId)
      .single();

    if (error) {
      console.error('❌ Failed to get audit status:', error);
      return {
        success: false,
        error: `Database error: ${error.message}`
      };
    }

    if (!data) {
      return {
        success: false,
        error: 'Audit not found'
      };
    }

    return {
      success: true,
      data: {
        status: data.status,
        created_timestamp: data.created_timestamp
      }
    };

  } catch (error) {
    console.error('💥 Unexpected error getting audit status:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
} 