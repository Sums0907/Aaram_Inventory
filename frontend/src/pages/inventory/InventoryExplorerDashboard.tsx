import React, { useState } from 'react';
import { useInventoryHierarchy } from '@/api/hierarchy';
import { InventoryExplorerTree } from '@/components/dashboard/InventoryExplorerTree';
import type { TreeNode } from '@/components/dashboard/InventoryExplorerTree';
import { HierarchyNodeWorkspace } from '@/components/dashboard/HierarchyNodeWorkspace';
import { Input } from '@/components/ui/input';
import { Search } from 'lucide-react';
import { InventoryItemFormDialog } from '@/components/products/InventoryItemFormDialog';
import { CategoryFormDialog } from '@/components/products/CategoryFormDialog';

export function InventoryExplorerDashboard() {
  const { data: hierarchy, isLoading, error } = useInventoryHierarchy();
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null);
  
  // Modals state
  const [isItemFormOpen, setIsItemFormOpen] = useState(false);
  const [isCategoryFormOpen, setIsCategoryFormOpen] = useState(false);
  const [defaultItemType, setDefaultItemType] = useState('FINISHED_GOODS');
  const [defaultCategoryId, setDefaultCategoryId] = useState<string | undefined>(undefined);
  const [defaultParentId, setDefaultParentId] = useState<string | undefined>(undefined);

  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground">Loading Explorer...</div>;
  }

  if (error || !hierarchy) {
    return <div className="p-8 text-center text-destructive">Failed to load Inventory Hierarchy.</div>;
  }

  const handleCreateProduct = (categoryId: string) => {
    // In a real app, we'd lookup the category to pass its type
    const category = hierarchy.categories.find(c => c.id === categoryId);
    setDefaultItemType(category?.item_type || 'FINISHED_GOODS');
    setDefaultCategoryId(categoryId);
    setIsItemFormOpen(true);
  };

  const handleCreateCategory = (parentType: string, parentId?: string) => {
    setDefaultItemType(parentType);
    setDefaultParentId(parentId);
    setIsCategoryFormOpen(true);
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
        </div>
        <div className="flex-1 overflow-hidden">
          <InventoryExplorerTree
            hierarchy={hierarchy}
            selectedNodeId={selectedNode?.id || null}
            onSelectNode={setSelectedNode}
            onCreateCategory={handleCreateCategory}
            onCreateProduct={handleCreateProduct}
          />
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 overflow-hidden bg-background">
        <HierarchyNodeWorkspace 
          node={selectedNode} 
          onCreateCategory={handleCreateCategory}
          onCreateProduct={handleCreateProduct}
        />
      </div>

      <InventoryItemFormDialog 
        open={isItemFormOpen} 
        onOpenChange={setIsItemFormOpen} 
        defaultItemType={defaultItemType}
        defaultCategoryId={defaultCategoryId}
      />
      
      <CategoryFormDialog
        open={isCategoryFormOpen}
        onOpenChange={setIsCategoryFormOpen}
        defaultItemType={defaultItemType}
        defaultParentId={defaultParentId}
      />
    </div>
  );
}
