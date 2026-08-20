// @ts-nocheck
import React, { useState, useEffect } from 'react';
import { useInventoryHierarchy } from '@/api/hierarchy';
import { useUpdateCategory, useArchiveCategory, useDeleteCategory, useUpdateProduct, useArchiveProduct, useDeleteProduct, useSKUs } from '@/api/masters';
import type { CategoryInfo, SKUResponse } from '@/api/masters';
import { InventoryExplorerTree } from '@/components/dashboard/InventoryExplorerTree';
import type { TreeNode } from '@/components/dashboard/InventoryExplorerTree';
import { HierarchyNodeWorkspace } from '@/components/dashboard/HierarchyNodeWorkspace';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Search } from 'lucide-react';
import { InventoryItemFormDialog } from '@/components/products/InventoryItemFormDialog';
import { CategoryFormDialog } from '@/components/products/CategoryFormDialog';

export function InventoryExplorerDashboard() {
  const [showArchived, setShowArchived] = useState(false);
  const { data: hierarchy, isLoading, error } = useInventoryHierarchy(showArchived);
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null);
  
  // Modals state
  const [isItemFormOpen, setIsItemFormOpen] = useState(false);
  const [isCategoryFormOpen, setIsCategoryFormOpen] = useState(false);
  const [defaultItemType, setDefaultItemType] = useState('FINISHED_GOODS');
  const [defaultCategoryId, setDefaultCategoryId] = useState<string | undefined>(undefined);
  const [defaultParentId, setDefaultParentId] = useState<string | undefined>(undefined);
  
  const [editingCategory, setEditingCategory] = useState<CategoryInfo | null>(null);
  const [editingProductSKU, setEditingProductSKU] = useState<SKUResponse | null>(null);

  const updateCategoryMutation = useUpdateCategory();
  const archiveCategoryMutation = useArchiveCategory();
  const deleteCategoryMutation = useDeleteCategory();
  const updateProductMutation = useUpdateProduct();
  const archiveProductMutation = useArchiveProduct();
  const deleteProductMutation = useDeleteProduct();
  
  const { data: skus } = useSKUs();

  // Sync selectedNode with hierarchy changes (renames/archives)
  useEffect(() => {
    if (hierarchy && selectedNode) {
      if (selectedNode.type === 'CATEGORY' || selectedNode.type === 'INVENTORY_TYPE') {
        const cat = hierarchy.categories.find(c => c.id === selectedNode.id);
        if (!cat && selectedNode.type === 'CATEGORY') {
          setSelectedNode(null);
        } else if (cat && cat.category_name !== selectedNode.label) {
          setSelectedNode(prev => prev ? { ...prev, label: cat.category_name, data: cat } : null);
        }
      } else if (selectedNode.type === 'PRODUCT') {
        const prod = hierarchy.products.find(p => p.id === selectedNode.id);
        if (!prod) {
          setSelectedNode(null);
        } else if (prod.product_name !== selectedNode.label) {
          setSelectedNode(prev => prev ? { ...prev, label: prod.product_name, data: prod } : null);
        }
      }
    }
  }, [hierarchy, selectedNode?.id]);

  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground">Loading Explorer...</div>;
  }

  if (error || !hierarchy) {
    return <div className="p-8 text-center text-destructive">Failed to load Inventory Hierarchy.</div>;
  }

  const handleCreateCategory = (parentType: string, parentId?: string) => {
    setDefaultItemType(parentType);
    setDefaultParentId(parentId);
    setEditingCategory(null);
    setIsCategoryFormOpen(true);
  };
  
  const handleCreateProduct = (categoryId: string) => {
    const category = hierarchy?.categories.find(c => c.id === categoryId);
    setDefaultItemType(category?.item_type || 'FINISHED_GOODS');
    setDefaultCategoryId(categoryId);
    setEditingProductSKU(null);
    setIsItemFormOpen(true);
  };

  const handleRenameCategory = async (categoryId: string, currentName: string) => {
    const category = hierarchy?.categories.find(c => c.id === categoryId);
    if (category) {
      setEditingCategory(category);
      setIsCategoryFormOpen(true);
    }
  };

  const handleArchiveCategory = async (categoryId: string) => {
    if (window.confirm("Are you sure you want to archive this category? It will no longer appear in active views.")) {
      try {
        await archiveCategoryMutation.mutateAsync(categoryId);
      } catch (err: any) {
        if (err?.response?.status === 422) {
           console.warn("Category is already archived or cannot be archived.", err);
        } else {
           console.error("Failed to archive category", err);
        }
      }
    }
  };

  const handleArchiveProduct = async (productId: string) => {
    if (window.confirm("Are you sure you want to archive this master item? It will no longer appear in active views.")) {
      try {
        await archiveProductMutation.mutateAsync(productId);
      } catch (err: any) {
        if (err?.response?.status === 422) {
           console.warn("Product is already archived or cannot be archived.", err);
        } else {
           console.error("Failed to archive product", err);
        }
      }
    }
  };

  const handleDeleteCategory = async (categoryId: string) => {
    if (window.confirm("Are you sure you want to permanently delete this archived category? This action cannot be undone.")) {
      try {
        await deleteCategoryMutation.mutateAsync(categoryId);
      } catch (err: any) {
        console.error("Failed to delete category", err);
      }
    }
  };

  const handleDeleteProduct = async (productId: string) => {
    if (window.confirm("Are you sure you want to permanently delete this archived product? This action cannot be undone.")) {
      try {
        await deleteProductMutation.mutateAsync(productId);
      } catch (err: any) {
        console.error("Failed to delete product", err);
      }
    }
  };

  const handleEditProduct = async (productId: string, currentName: string) => {
    const sku = skus?.find(s => s.product?.id === productId);
    if (sku) {
      setEditingProductSKU(sku);
      setIsItemFormOpen(true);
    } else {
      // Fallback: create a synthetic SKU to open the dialog for editing the master item name
      const syntheticSku: any = {
        id: 'new-sku',
        status: 'ACTIVE',
        product_id: productId,
        product: { id: productId, product_name: currentName, category_id: '' }
      };
      setEditingProductSKU(syntheticSku);
      setIsItemFormOpen(true);
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background">
      {/* Explorer Sidebar */}
      <div className="w-80 border-r flex flex-col bg-muted/20">
        <div className="p-4 border-b">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input 
              type="search" 
              placeholder="Global Inventory Search..." 
              className="w-full bg-background pl-8"
            />
          </div>
          <div className="flex items-center space-x-2 mt-4 px-1">
            <Switch 
              id="show-archived" 
              checked={showArchived}
              onCheckedChange={setShowArchived}
            />
            <Label htmlFor="show-archived" className="text-sm text-muted-foreground cursor-pointer">
              Show Archived
            </Label>
          </div>
        </div>
        <div className="flex-1 overflow-hidden">
          <InventoryExplorerTree
            hierarchy={hierarchy}
            selectedNodeId={selectedNode?.id || null}
            onSelectNode={setSelectedNode}
            onCreateCategory={handleCreateCategory}
            onCreateProduct={handleCreateProduct}
            onEditCategory={handleRenameCategory}
            onArchiveCategory={handleArchiveCategory}
            onDeleteCategory={handleDeleteCategory}
            onEditProduct={handleEditProduct}
            onArchiveProduct={handleArchiveProduct}
            onDeleteProduct={handleDeleteProduct}
          />
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 overflow-hidden bg-background">
        <HierarchyNodeWorkspace 
          node={selectedNode}
          hierarchy={hierarchy} 
          onCreateCategory={handleCreateCategory}
          onCreateProduct={handleCreateProduct}
          onEditProduct={handleEditProduct}
          onEditCategory={handleRenameCategory}
          onArchiveCategory={handleArchiveCategory}
          onDeleteCategory={handleDeleteCategory}
          onArchiveProduct={handleArchiveProduct}
          onDeleteProduct={handleDeleteProduct}
        />
      </div>

      <InventoryItemFormDialog 
        open={isItemFormOpen} 
        onOpenChange={setIsItemFormOpen} 
        defaultItemType={defaultItemType}
        defaultCategoryId={defaultCategoryId}
        initialData={editingProductSKU}
      />
      
      <CategoryFormDialog
        open={isCategoryFormOpen}
        onOpenChange={setIsCategoryFormOpen}
        defaultItemType={defaultItemType}
        defaultParentId={defaultParentId}
        initialData={editingCategory}
      />
    </div>
  );
}
