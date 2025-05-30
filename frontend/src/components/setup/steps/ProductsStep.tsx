/* 
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Product } from "@/types/brandTypes";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PlusCircle, X, Edit, Trash2 } from "lucide-react";
import { nanoid } from "nanoid";

interface ProductsStepProps {
  products: Product[];
  setProducts: (products: Product[]) => void;
}

export const ProductsStep = ({ products, setProducts }: ProductsStepProps) => {
  const [productName, setProductName] = useState("");
  const [valueProp, setValueProp] = useState("");
  const [valueProps, setValueProps] = useState<string[]>([]);
  const [editingProductId, setEditingProductId] = useState<string | null>(null);

  const resetForm = () => {
    setProductName("");
    setValueProps([]);
    setEditingProductId(null);
  };

  const addValueProp = () => {
    if (valueProp.trim()) {
      setValueProps((prev) => [...prev, valueProp.trim()]);
      setValueProp("");
    }
  };

  const removeValueProp = (index: number) => {
    const updated = [...valueProps];
    updated.splice(index, 1);
    setValueProps(updated);
  };

  const addProduct = () => {
    if (!productName.trim() || valueProps.length === 0) {
      return;
    }

    const newProduct: Product = {
      id: editingProductId || nanoid(),
      name: productName.trim(),
      valueProps: [...valueProps],
    };

    if (editingProductId) {
      setProducts(
        products.map((p) => (p.id === editingProductId ? newProduct : p))
      );
    } else {
      setProducts([...products, newProduct]);
    }

    resetForm();
  };

  const editProduct = (product: Product) => {
    setProductName(product.name);
    setValueProps(product.valueProps);
    setEditingProductId(product.id);
  };

  const deleteProduct = (id: string) => {
    setProducts(products.filter((p) => p.id !== id));
  };

  const generateAIValueProps = () => {
    // In a real implementation, this would call an AI service
    // For now, let's simulate with some example value props
    if (productName) {
      const simulatedProps = [
        "High quality",
        "Affordable pricing",
        "Fast delivery",
        "Customer satisfaction guaranteed",
      ];
      setValueProps(simulatedProps);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold mb-2">Products & Offerings</h2>
        <p className="text-muted-foreground">
          Add your brand's products or service offerings.
        </p>
      </div>

      <div className="border rounded-lg p-4 space-y-4 bg-slate-50">
        <div className="grid grid-cols-1 gap-4">
          <div className="space-y-2">
            <Label htmlFor="product-name">Product Name</Label>
            <Input
              id="product-name"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="e.g., FlexFit Joggers"
            />
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <Label>Value Propositions</Label>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={generateAIValueProps}
              disabled={!productName}
            >
              Generate with AI
            </Button>
          </div>
          <div className="flex space-x-2">
            <Input
              value={valueProp}
              onChange={(e) => setValueProp(e.target.value)}
              placeholder="e.g., affordable, eco-friendly"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  addValueProp();
                  e.preventDefault();
                }
              }}
            />
            <Button type="button" onClick={addValueProp}>
              <PlusCircle className="h-4 w-4 mr-2" /> Add
            </Button>
          </div>

          {valueProps.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {valueProps.map((prop, index) => (
                <div
                  key={index}
                  className="flex items-center bg-white border rounded-full px-3 py-1"
                >
                  <span className="text-sm">{prop}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-5 w-5 p-0 ml-1"
                    onClick={() => removeValueProp(index)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end">
          <Button onClick={addProduct}>
            {editingProductId ? "Update Product" : "Add Product"}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        {products.map((product) => (
          <Card key={product.id}>
            <CardHeader>
              <CardTitle>{product.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {product.valueProps.map((prop, index) => (
                  <span
                    key={index}
                    className="bg-slate-100 px-2 py-1 rounded-md text-sm"
                  >
                    {prop}
                  </span>
                ))}
              </div>
            </CardContent>
            <CardFooter className="flex justify-end space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => editProduct(product)}
              >
                <Edit className="h-4 w-4 mr-2" /> Edit
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="text-red-500"
                onClick={() => deleteProduct(product.id as string)}
              >
                <Trash2 className="h-4 w-4 mr-2" /> Delete
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      {products.length === 0 && (
        <div className="text-center p-8 border-2 border-dashed rounded-lg">
          <p className="text-muted-foreground">
            No products added yet. Add your first product above.
          </p>
        </div>
      )}
    </div>
  );
};
 */