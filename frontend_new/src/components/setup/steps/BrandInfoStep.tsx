/**
 * BRAND INFO STEP - UPDATED WITH AUDIT INTEGRATION VIA WIZARD STATE
 * 
 * PURPOSE: This component handles the brand information display and product selection.
 * NEW FUNCTIONALITY: Now creates audit entries and reports back to wizard state.
 * 
 * DEVELOPMENT MODE: Works without authentication using fake user ID for testing
 * 
 * USER FLOW:
 * 1. User sees brand info (name, description, domain) - populated from search
 * 2. User sees list of products - populated from API call
 * 3. User selects one product using radio buttons
 * 4. User clicks "Next" → THIS IS WHERE WE CREATE THE AUDIT ENTRY
 * 5. System creates audit record linking brand + product + user (real or fake)
 * 6. Wizard state stores audit ID and automatically proceeds to Topics step
 */

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { BrandEntity, SocialLink, Product } from "@/types/brandTypes";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";
// NEW IMPORT: Audit service for creating audit entries
import { createAudit, CreateAuditRequest } from "@/services/auditService";
// NEW IMPORT: Get current user information (optional in dev mode)
import { supabase } from "@/integrations/supabase/client";
// NEW IMPORT: UUID for generating proper product IDs
import { v4 as uuidv4 } from 'uuid';
import { User } from "@supabase/supabase-js";

interface BrandInfoStepProps {
  brandInfo: BrandEntity;
  setBrandInfo: (brandInfo: BrandEntity) => void;
  products: Product[];
  setProducts: (products: Product[]) => void;
  brandDescription?: string;
  availableProducts?: Product[];
  // NEW PROPS: From wizard state for audit management
  brandId?: string | null;
  onAuditCreated?: (auditId: string) => void;
  setTriggerAuditCreation?: (trigger: (() => void) | null) => void;
}

export const BrandInfoStep = ({
  brandInfo,
  setBrandInfo,
  products,
  setProducts,
  brandDescription,
  availableProducts: propAvailableProducts,
  // NEW: Get brand ID and audit callback from wizard
  brandId,
  onAuditCreated,
  setTriggerAuditCreation
}: BrandInfoStepProps) => {
  const [customProduct, setCustomProduct] = useState("");
  const [selectedProductId, setSelectedProductId] = useState<string | null>(null);
  // NEW STATE: Track if audit creation is in progress
  const [isCreatingAudit, setIsCreatingAudit] = useState(false);
  // NEW STATE: Store current user information (optional in dev mode)
  const [currentUser, setCurrentUser] = useState<any>(null);

  // Use available products from props if provided, fallback to sample products
  const availableProducts = propAvailableProducts && propAvailableProducts.length > 0 
    ? propAvailableProducts 
    : [
        { id: uuidv4(), name: "Premium Subscription", valueProps: [] },
        { id: uuidv4(), name: "Mobile Application", valueProps: [] },
        { id: uuidv4(), name: "Smart Device", valueProps: [] },
        { id: uuidv4(), name: "Online Course", valueProps: [] },
        { id: uuidv4(), name: "Analytics Platform", valueProps: [] }
      ];

  /**
   * EFFECT: Get current user information when component loads
   * 
   * WHY: We try to get real user ID, but it's okay if it fails (dev mode handles this)
   * WHEN: Component mounts
   * WHAT: Fetches current authenticated user from Supabase
   * 
   * DEVELOPMENT NOTE: 
   * - If user is not authenticated, audit service will use fake user ID
   * - This allows testing without setting up authentication
   */
  useEffect(() => {
    const getCurrentUser = async () => {
      try {
        const { data: { user }, error } = await supabase.auth.getUser();
        if (error) {
          console.warn('⚠️ No authenticated user found (this is OK in development):', error.message);
          setCurrentUser(null);
          return;
        }
        
        if (user) {
          setCurrentUser(user);
          console.log('✅ Authenticated user loaded:', user.id);
        } else {
          console.warn('⚠️ No user session found (this is OK in development)');
          setCurrentUser(null);
        }
      } catch (error) {
        console.warn('⚠️ Error getting user (this is OK in development):', error);
        setCurrentUser(null);
      }
    };

    getCurrentUser();
  }, []);

  /**
   * EFFECT: Initialize selected product when returning to this step
   * 
   * WHY: If user goes back from topics step, we want to remember their selection
   * WHEN: Products prop changes (e.g., when user returns to this step)
   * WHAT: Sets the selectedProductId based on existing products
   */
  useEffect(() => {
    if (products.length > 0) {
      setSelectedProductId(products[0].id || null);
    }
  }, [products]);

  /**
   * NEW EFFECT: Register audit creation trigger with wizard
   * 
   * PURPOSE: Allow WizardNavigation to trigger audit creation
   * WHEN: Component mounts or when dependencies change
   * WHAT: Registers the handleNext function as the audit trigger
   */
  useEffect(() => {
    if (setTriggerAuditCreation) {
      setTriggerAuditCreation(() => handleNext);
    }

    // Cleanup: unregister trigger when component unmounts
    return () => {
      if (setTriggerAuditCreation) {
        setTriggerAuditCreation(null);
      }
    };
  }, [setTriggerAuditCreation, selectedProductId, products, brandId, currentUser]); // Include dependencies that handleNext uses

  /**
   * HANDLER: Product selection via radio buttons
   * 
   * PURPOSE: Manages when user selects a product from the list
   * WHAT HAPPENS:
   * 1. Updates the selected product ID state
   * 2. Finds the selected product details
   * 3. Updates the products array with the selected product
   * 4. Clears any custom product input
   */
  const handleProductSelection = (productId: string) => {
    // Update which radio button is selected
    setSelectedProductId(productId);

    // Find the full product details from available products
    const selectedProduct = availableProducts.find(p => p.id === productId);
    if (selectedProduct) {
      // Update the wizard state with the selected product
      // WHY: The wizard needs to know which product was chosen
      setProducts([{
        id: selectedProduct.id,
        name: selectedProduct.name,
        valueProps: selectedProduct.valueProps || []
      }]);
    }

    // Clear custom product field since user selected from list
    setCustomProduct("");
  };

  /**
   * HANDLER: Custom product input changes
   * 
   * PURPOSE: Manages when user types in the custom product field
   * AUTO-BEHAVIOR: Automatically selects "custom" radio when user starts typing
   */
  const handleCustomProductChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCustomProduct(e.target.value);
    // Auto-select the custom radio button when user starts typing
    if (e.target.value.trim()) {
      setSelectedProductId("custom");
    }
  };

  /**
   * HANDLER: Custom product field loses focus
   * 
   * PURPOSE: Finalizes custom product selection when user finishes typing
   * WHAT HAPPENS:
   * 1. If custom field has text and is selected → add to products
   * 2. If custom field is empty but selected → clear products
   */
  const handleCustomProductBlur = () => {
    if (customProduct.trim() && selectedProductId === "custom") {
      // User typed a custom product name and it's selected
      setProducts([{
        id: uuidv4(), // Generate proper UUID for custom product
        name: customProduct.trim(),
        valueProps: []
      }]);
    } else if (selectedProductId === "custom" && !customProduct.trim()) {
      // Custom is selected but field is empty - clear selection
      setProducts([]);
    }
  };

  /**
   * MAIN HANDLER: Process "Next" button click with Wizard Integration
   * 
   * PURPOSE: This is the critical function that creates the audit entry and reports to wizard
   * 
   * UPDATED BEHAVIOR: Now uses wizard state for brand ID and audit callback
   * 
   * WORKFLOW:
   * 1. Validate that user has selected a product
   * 2. Validate that we have brand ID from wizard state
   * 3. Create audit entry in database (uses real or fake user ID)
   * 4. Call wizard's handleAuditCreated function to store audit ID and proceed
   * 5. Handle success/error cases
   */
  const handleNext = async () => {
    try {
      // VALIDATION 1: Ensure user has selected a product
      if (!selectedProductId || products.length === 0) {
        return;
      }

      // VALIDATION 2: Ensure we have the brand ID from wizard state
      if (!brandId) {
        return;
      }

      // VALIDATION 3: Get the selected product ID
      const selectedProduct = products[0];
      if (!selectedProduct?.id) {
        return;
      }

      // Show loading state while creating audit
      setIsCreatingAudit(true);

      // PREPARE USER ID: Use real user ID if available, otherwise audit service will use fake ID
      const userId = currentUser?.id || null;  // null is OK - audit service handles this

      // MAIN ACTION: Create the audit entry
      console.log('🚀 Starting audit creation with:', {
        brandId,
        productId: selectedProduct.id,
        userId: userId || '(will use dev mode fake ID)',
        productName: selectedProduct.name
      });

      const auditRequest: CreateAuditRequest = {
        brandId: brandId,
        productId: selectedProduct.id,
        userId: userId || "",  // Empty string will trigger dev mode in audit service
        productName: selectedProduct.name  // Include product name for database creation
      };

      const auditResponse = await createAudit(auditRequest);

      // HANDLE AUDIT CREATION RESULT
      if (auditResponse.success && auditResponse.auditId) {
        // SUCCESS: Audit created successfully
        console.log('✅ Audit created successfully:', auditResponse.auditId);
        
        // IMPORTANT: Update product ID with actual database ID if different
        if (auditResponse.actualProductId && auditResponse.actualProductId !== selectedProduct.id) {
          console.log('🔄 Updating product ID from frontend UUID to database ID:', {
            frontendId: selectedProduct.id,
            databaseId: auditResponse.actualProductId
          });
          
          // Update the products state with the real database product ID
          setProducts([{
            ...selectedProduct,
            id: auditResponse.actualProductId  // Use the actual database product ID
          }]);
        }

        // NEW: Call wizard's handleAuditCreated function
        if (onAuditCreated) {
          onAuditCreated(auditResponse.auditId);
        } else {
          console.warn('⚠️ No onAuditCreated callback provided by wizard');
        }
        
      } else {
        // ERROR: Audit creation failed
        console.error('❌ Failed to create audit:', auditResponse.error);
      }

    } catch (error) {
      // UNEXPECTED ERROR: Something went wrong
      console.error('💥 Unexpected error in handleNext:', error);
      
    } finally {
      // Always hide loading state
      setIsCreatingAudit(false);
    }
  };

  return <div className="space-y-8">
      <div>
        {/*<p className="text-sm text-muted-foreground mb-1">Step 1 of 5</p>*/}
        <h2 className="text-2xl font-heading font-semibold text-white mb-6">
          Brand & Product
        </h2>
      </div>

      {/* Non-editable brand information */}
      <div className="p-6 rounded-lg border border-border bg-card shadow-sm hover:shadow-md transition">
        <div className="flex items-center space-x-4 mb-4">
          <div className="w-16 h-16 rounded-full border border-border/40 flex items-center justify-center text-2xl font-heading">
            {brandInfo.name.charAt(0)}
          </div>
          <div>
            <h3 className="font-semibold text-lg">{brandInfo.name}</h3>
            <p className="text-text-secondary">{brandInfo.website}</p>
          </div>
        </div>
        
        <p className="text-text-secondary">{brandDescription || "sample description"}</p>
      </div>

      <Separator className="bg-black/20 my-8" />
      
      <div className="space-y-4">
        <h3 className="text-xl font-medium font-heading tracking-tight mb-4">Select a Product</h3>
        <p className="text-text-secondary mb-6">
          Choose one product or service you want to analyze consumer perception for.
        </p>
        
        <RadioGroup 
          value={selectedProductId || ""} 
          onValueChange={handleProductSelection} 
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {availableProducts.map(product => (
            <div 
              key={product.id} 
              className={`flex items-center space-x-3 p-4 rounded-lg border ${
                selectedProductId === product.id 
                  ? 'border-brand-purple bg-brand-purple/10' 
                  : 'border-border hover:border-brand-purple/40'
              } bg-card transition-shadow hover:shadow-md cursor-pointer`}
              onClick={() => handleProductSelection(product.id)}
            >
              <RadioGroupItem 
                value={product.id} 
                id={product.id} 
                className="radio-accent h-4 w-4" 
              />
              <Label 
                htmlFor={product.id} 
                className="flex-grow font-medium cursor-pointer"
              >
                {product.name}
              </Label>
            </div>
          ))}
            
          {/* Simplified custom product option */}
          <div 
            className={`flex items-center space-x-3 p-4 rounded-lg border ${
              selectedProductId === "custom" 
                ? 'border-brand-purple bg-brand-purple/10' 
                : 'border-border hover:border-brand-purple/40'
            } bg-card hover:shadow-md`}
            onClick={() => handleProductSelection("custom")}
          >
            <RadioGroupItem 
              value="custom" 
              id="custom" 
              className="radio-accent h-4 w-4" 
            />
            <div className="flex-1 space-y-1">
              <Label htmlFor="custom-input" className="font-medium">Custom Product</Label>
              <Input 
                id="custom-input"
                className="bg-background border border-input rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-brand-purple/40"
                placeholder="Enter your custom product" 
                value={customProduct} 
                onChange={handleCustomProductChange} 
                onBlur={handleCustomProductBlur} 
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          </div>
        </RadioGroup>
      </div>

      {/* REMOVED: Extra Next button - WizardNavigation handles this now */}
    </div>;
};
