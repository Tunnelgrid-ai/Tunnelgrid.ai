/**
 * BRAND INFO STEP - UPDATED WITH EDITING CAPABILITIES
 * 
 * PURPOSE: This component handles the brand information display and product selection.
 * NEW FUNCTIONALITY: Users can now edit and save brand descriptions to Supabase.
 */

import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { BrandEntity, SocialLink, Product } from "@/types/brandTypes";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { createAudit, CreateAuditRequest } from "@/services/auditService";
import { brandService } from "@/services/brandService";
import { supabase } from "@/integrations/supabase/client";
import { v4 as uuidv4 } from 'uuid';
import { User } from "@supabase/supabase-js";
import { CheckCircle, Target, Edit3, Save, X } from "lucide-react";

interface BrandInfoStepProps {
  brandInfo: BrandEntity;
  setBrandInfo: (brandInfo: BrandEntity) => void;
  products: Product[];
  setProducts: (products: Product[]) => void;
  brandDescription?: string;
  availableProducts?: Product[];
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
  brandId,
  onAuditCreated,
  setTriggerAuditCreation
}: BrandInfoStepProps) => {
  const [customProduct, setCustomProduct] = useState("");
  const [selectedProductId, setSelectedProductId] = useState<string | null>(null);
  const [isCreatingAudit, setIsCreatingAudit] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);
  
  // State for editing brand description
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [editedDescription, setEditedDescription] = useState(brandDescription || "");
  const [isSavingDescription, setIsSavingDescription] = useState(false);
  
  // NEW: Ref for textarea auto-resize
  const textareaRef = useRef<HTMLTextAreaElement>(null);

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

  // Auto-resize textarea when editing starts or content changes
  useEffect(() => {
    if (isEditingDescription && textareaRef.current) {
      const textarea = textareaRef.current;
      // Reset height to auto to get the natural scroll height
      textarea.style.height = 'auto';
      // Set height to scrollHeight to show all content
      textarea.style.height = textarea.scrollHeight + 'px';
    }
  }, [isEditingDescription, editedDescription]);

  // Get current user information when component loads
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

  // Initialize edited description when brandDescription changes
  useEffect(() => {
    if (brandDescription) {
      setEditedDescription(brandDescription);
    }
  }, [brandDescription]);

  // Initialize selected product when returning to this step
  useEffect(() => {
    if (products.length > 0) {
      setSelectedProductId(products[0].id || null);
    }
  }, [products]);

  // Register audit creation trigger with wizard
  useEffect(() => {
    if (setTriggerAuditCreation) {
      setTriggerAuditCreation(() => handleNext);
    }

    return () => {
      if (setTriggerAuditCreation) {
        setTriggerAuditCreation(null);
      }
    };
  }, [setTriggerAuditCreation, selectedProductId, products, brandId, currentUser]);

  // Auto-resize function for textarea
  const handleTextareaResize = () => {
    if (textareaRef.current) {
      const textarea = textareaRef.current;
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';
    }
  };

  // Save description changes via backend API
  const handleSaveDescription = async () => {
    if (!brandId) {
      alert('Brand ID is required to save description.');
      return;
    }
    
    setIsSavingDescription(true);
    try {
      // Call backend API to update brand description
      const response = await brandService.updateBrandDescription(brandId, editedDescription.trim());

      if (!response.success) {
        throw new Error(response.message || 'Failed to save description');
      }

      // Update local state
      setBrandInfo({
        ...brandInfo,
        description: editedDescription.trim(),
        editedByUser: true
      });

      setIsEditingDescription(false);
      console.log('✅ Brand description updated successfully via API');
      
    } catch (error) {
      console.error('❌ Error saving description via API:', error);
      alert('Failed to save description. Please try again.');
    } finally {
      setIsSavingDescription(false);
    }
  };

  // Cancel editing and revert changes
  const handleCancelEdit = () => {
    setEditedDescription(brandDescription || "");
    setIsEditingDescription(false);
  };

  // Product selection handler
  const handleProductSelection = (productId: string) => {
    setSelectedProductId(productId);
    const selectedProduct = availableProducts.find(p => p.id === productId);
    if (selectedProduct) {
      setProducts([{
        id: selectedProduct.id,
        name: selectedProduct.name,
        valueProps: selectedProduct.valueProps || []
      }]);
    }
    setCustomProduct("");
  };

  // Custom product input changes
  const handleCustomProductChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCustomProduct(e.target.value);
    if (e.target.value.trim()) {
      setSelectedProductId("custom");
    }
  };

  // Custom product field loses focus
  const handleCustomProductBlur = () => {
    if (customProduct.trim() && selectedProductId === "custom") {
      setProducts([{
        id: uuidv4(),
        name: customProduct.trim(),
        valueProps: []
      }]);
    } else if (selectedProductId === "custom" && !customProduct.trim()) {
      setProducts([]);
    }
  };

  // Main handler for Next button
  const handleNext = async () => {
    try {
      if (!selectedProductId || products.length === 0) {
        return;
      }

      if (!brandId) {
        return;
      }

      const selectedProduct = products[0];
      if (!selectedProduct?.id) {
        return;
      }

      setIsCreatingAudit(true);
      const userId = currentUser?.id || null;

      console.log('🚀 Starting audit creation with:', {
        brandId,
        productId: selectedProduct.id,
        userId: userId || '(will use dev mode fake ID)',
        productName: selectedProduct.name
      });

      const auditRequest: CreateAuditRequest = {
        brandId: brandId,
        productId: selectedProduct.id,
        userId: userId || "",
        productName: selectedProduct.name
      };

      const auditResponse = await createAudit(auditRequest);

      if (auditResponse.success && auditResponse.auditId) {
        console.log('✅ Audit created successfully:', auditResponse.auditId);
        
        if (auditResponse.actualProductId && auditResponse.actualProductId !== selectedProduct.id) {
          console.log('🔄 Updating product ID from frontend UUID to database ID:', {
            frontendId: selectedProduct.id,
            databaseId: auditResponse.actualProductId
          });
          
          setProducts([{
            ...selectedProduct,
            id: auditResponse.actualProductId
          }]);
        }

        if (onAuditCreated) {
          onAuditCreated(auditResponse.auditId);
        } else {
          console.warn('⚠️ No onAuditCreated callback provided by wizard');
        }
        
      } else {
        console.error('❌ Failed to create audit:', auditResponse.error);
      }

    } catch (error) {
      console.error('💥 Unexpected error in handleNext:', error);
    } finally {
      setIsCreatingAudit(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        {/* Informational Alert */}
        <Alert className="mb-6 border-accent/20 bg-accent/5">
          <Target className="h-4 w-4 text-accent" />
          <AlertDescription className="text-sm">
            <span className="text-accent font-medium">Verify the brand information we'll track.</span> This brand information powers the analysis - make updates as needed to ensure accuracy.
          </AlertDescription>
        </Alert>
      </div>

      {/* Brand Information Card */}
      <div className="p-6 rounded-lg border border-border/30 bg-[#232b36] shadow-sm">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center text-2xl font-bold text-white">
              {brandInfo.name.charAt(0)}
            </div>
            <div>
              <h3 className="font-semibold text-xl text-white">{brandInfo.name}</h3>
              <p className="text-accent text-sm">{brandInfo.website}</p>
            </div>
          </div>
        </div>
        
        {/* Editable Description Section */}
        <div className="space-y-3">
          {!isEditingDescription ? (
            <div className="flex items-start justify-between">
              <p className="text-text-secondary leading-relaxed flex-1 pr-4">
                {editedDescription || brandDescription || "No description available"}
              </p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsEditingDescription(true)}
                className="p-2 h-8 w-8"
              >
                <Edit3 className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              <Textarea
                ref={textareaRef}
                value={editedDescription}
                onChange={(e) => {
                  setEditedDescription(e.target.value);
                  handleTextareaResize();
                }}
                className="bg-background border border-input resize-none overflow-hidden"
                placeholder="Enter brand description..."
                style={{ 
                  minHeight: '60px'
                }}
              />
              <div className="flex gap-2 justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCancelEdit}
                  disabled={isSavingDescription}
                >
                  <X className="h-4 w-4 mr-1" />
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleSaveDescription}
                  disabled={isSavingDescription}
                  className="bg-accent hover:bg-accent/90 text-black"
                >
                  {isSavingDescription ? (
                    "Saving..."
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-1" />
                      Save
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      <Separator className="bg-border/30" />
      
      {/* Product Selection Section */}
      <div className="space-y-6">
        <div>
          <h3 className="text-xl font-semibold text-white mb-4">Select Products</h3>
          
          {/* Product Selection Info Alert */}
          <Alert className="mb-6 border-accent/20 bg-accent/5">
            <Target className="h-4 w-4 text-accent" />
            <AlertDescription className="text-sm">
              <span className="text-accent font-medium">Focus on a specific product or service</span> to get more targeted and actionable insights. This helps us analyze how AI systems specifically discuss your chosen offering.
            </AlertDescription>
          </Alert>
        </div>
        
        <RadioGroup 
          value={selectedProductId || ""} 
          onValueChange={handleProductSelection} 
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {availableProducts.map(product => (
            <div 
              key={product.id} 
              className={`flex items-center space-x-3 p-4 rounded-lg border transition-all cursor-pointer ${
                selectedProductId === product.id 
                  ? 'border-accent bg-accent/10 shadow-md' 
                  : 'border-border/30 hover:border-accent/40 bg-[#232b36]'
              }`}
              onClick={() => handleProductSelection(product.id)}
            >
              <RadioGroupItem 
                value={product.id} 
                id={product.id} 
                className="border-accent text-accent" 
              />
              <Label 
                htmlFor={product.id} 
                className="flex-grow font-medium text-white cursor-pointer"
              >
                {product.name}
              </Label>
            </div>
          ))}
            
          {/* Custom Product Option */}
          <div 
            className={`flex items-center space-x-3 p-4 rounded-lg border transition-all ${
              selectedProductId === "custom" 
                ? 'border-accent bg-accent/10 shadow-md' 
                : 'border-border/30 hover:border-accent/40 bg-[#232b36]'
            }`}
            onClick={() => handleProductSelection("custom")}
          >
            <RadioGroupItem 
              value="custom" 
              id="custom" 
              className="border-accent text-accent" 
            />
            <div className="flex-1 space-y-2">
              <Label htmlFor="custom-input" className="font-medium text-white">Custom Product</Label>
              <Input 
                id="custom-input"
                className="bg-background border border-input text-sm"
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
    </div>
  );
};
