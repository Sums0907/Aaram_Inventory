// @ts-nocheck
import React, { useState, useEffect } from 'react';
import { useInventoryHierarchy } from '@/api/hierarchy';
import { useUpdateCategory, useArchiveCategory, useDeleteCategory, useUpdateProduct, useArchiveProduct, useDeleteProduct, useSKUs } from '@/api/masters';
import type { CategoryInfo, SKUResponse } from '@/api/masters';
import { HierarchyNodeWorkspace } from '@/components/dashboard/HierarchyNodeWorkspace';
import type { TreeNodeType, TreeNode } from '@/components/dashboard/HierarchyNodeWorkspace';
import { InventoryExplorerTree } from '@/components/dashboard/InventoryExplorerTree';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Search, ChevronRight, Home } from 'lucide-react';
import { InventoryItemFormDialog } from '@/components/products/InventoryItemFormDialog';
import { CategoryFormDialog } from '@/components/products/CategoryFormDialog';
import { Button } from '@/components/ui/button';

export function InventoryExplorerDashboard() {
  const [showArchived, setShowArchived] = useState(false);
  const { data: hierarchy, isLoading, error } = useInventoryHierarchy(showArchived);
  const [path, setPath] = useState<TreeNode[]>([]);
  const selectedNode = path.length > 0 ? path[path.length - 1] : null;
  
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
          // It was deleted or archived (and we hide archived). Pop it off.
          setPath(prev => prev.slice(0, -1));
        } else if (cat && cat.category_name !== selectedNode.label) {
          // Rename node in path
          setPath(prev => prev.map((n, i) => i === prev.length - 1 ? { ...n, label: cat.category_name, data: cat } : n));
        }
      } else if (selectedNode.type === 'PRODUCT') {
        const prod = hierarchy.products.find(p => p.id === selectedNode.id);
        if (!prod) {
          setPath(prev => prev.slice(0, -1));
        } else if (prod.product_name !== selectedNode.label) {
          setPath(prev => prev.map((n, i) => i === prev.length - 1 ? { ...n, label: prod.product_name, data: prod } : n));
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

  const handleNavigateToNode = (node: TreeNode) => {
    setPath(prev => [...prev, node]);
  };

  const handleNavigateToBreadcrumb = (index: number) => {
    setPath(prev => prev.slice(0, index + 1));
  };

  const handleGoHome = () => {
    setPath([]);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-background">
      {/* Top Bar with Breadcrumbs and Search */}
      <div className="w-full border-b bg-white flex items-center justify-between px-6 py-3 shadow-sm z-10 relative">
        <div className="flex items-center space-x-2 text-sm font-medium">
          <Button variant="ghost" size="sm" onClick={handleGoHome} className="text-slate-500 hover:text-slate-900 px-2">
            <Home className="h-4 w-4" />
          </Button>
          
          {path.map((p, index) => (
            <React.Fragment key={p.id}>
              <ChevronRight className="h-4 w-4 text-slate-300" />
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => handleNavigateToBreadcrumb(index)}
                className={`px-2 ${index === path.length - 1 ? 'text-indigo-600 bg-indigo-50 hover:bg-indigo-100' : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'}`}
              >
                {p.label}
              </Button>
            </React.Fragment>
          ))}
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Switch 
              id="show-archived" 
              checked={showArchived}
              onCheckedChange={setShowArchived}
            />
            <Label htmlFor="show-archived" className="text-sm text-slate-500 cursor-pointer whitespace-nowrap">
              Show Archived
            </Label>
          </div>
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
            <Input 
              type="search" 
              placeholder="Search Catalog..." 
              className="w-full bg-slate-50 pl-8 focus-visible:ring-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden bg-slate-50/50">
        <div className="w-80 border-r bg-slate-50 flex flex-col shadow-sm z-0 relative">
          <InventoryExplorerTree
            hierarchy={hierarchy}
            selectedNodeId={selectedNode?.id || null}
            onSelectNode={handleNavigateToNode}
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
        <div className="flex-1 overflow-hidden">
          <HierarchyNodeWorkspace 
            node={selectedNode}
            hierarchy={hierarchy} 
            onNavigate={handleNavigateToNode}
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
