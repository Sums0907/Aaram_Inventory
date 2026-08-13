import React, { useState } from 'react';
import { ChevronRight, ChevronDown, Folder, Package, FileBox } from 'lucide-react';
import type { CategoryInfo, ProductInfo } from '@/api/masters';
import type { HierarchyResponse } from '@/api/hierarchy';
import { cn } from '@/lib/utils';
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from '@/components/ui/context-menu';

export type TreeNodeType = 'ROOT' | 'INVENTORY_TYPE' | 'CATEGORY' | 'PRODUCT';

export interface TreeNode {
  id: string;
  type: TreeNodeType;
  label: string;
  children: TreeNode[];
  data?: any; // The original category or product data
  itemCount?: number; // Total items under this node
}

interface InventoryExplorerTreeProps {
  hierarchy: HierarchyResponse;
  selectedNodeId: string | null;
  onSelectNode: (node: TreeNode) => void;
  onCreateCategory: (parentType: string, parentId?: string) => void;
  onCreateProduct: (categoryId: string) => void;
  onEditCategory?: (categoryId: string, currentName: string) => void;
  onArchiveCategory?: (categoryId: string) => void;
  onDeleteCategory?: (categoryId: string) => void;
  onEditProduct?: (productId: string, currentName: string) => void;
  onArchiveProduct?: (productId: string) => void;
  onDeleteProduct?: (productId: string) => void;
}

export function buildTree(hierarchy: HierarchyResponse): TreeNode[] {
  const { categories, products } = hierarchy;

  const typeNodes: Record<string, TreeNode> = {
    'FINISHED_GOODS': { id: 'FINISHED_GOODS', type: 'INVENTORY_TYPE', label: 'Finished Goods', children: [], itemCount: 0 },
    'RAW_MATERIAL': { id: 'RAW_MATERIAL', type: 'INVENTORY_TYPE', label: 'Raw Materials', children: [], itemCount: 0 },
    'PACKAGING_MATERIAL': { id: 'PACKAGING_MATERIAL', type: 'INVENTORY_TYPE', label: 'Packaging', children: [], itemCount: 0 },
    'CONSUMABLE': { id: 'CONSUMABLE', type: 'INVENTORY_TYPE', label: 'Consumables', children: [], itemCount: 0 },
    'ASSET': { id: 'ASSET', type: 'INVENTORY_TYPE', label: 'Assets', children: [], itemCount: 0 },
  };

  const categoryNodes: Record<string, TreeNode> = {};

  // First pass: create all category nodes
  categories.forEach(cat => {
    categoryNodes[cat.id] = {
      id: cat.id,
      type: 'CATEGORY',
      label: cat.category_name,
      children: [],
      data: cat,
      itemCount: 0
    };
  });

  // Second pass: attach subcategories and top-level categories
  categories.forEach(cat => {
    const node = categoryNodes[cat.id];
    if (cat.parent_id && categoryNodes[cat.parent_id]) {
      categoryNodes[cat.parent_id].children.push(node);
    } else {
      if (typeNodes[cat.item_type]) {
        typeNodes[cat.item_type].children.push(node);
      }
    }
  });

  // Third pass: attach products
  products.forEach(prod => {
    const node: TreeNode = {
      id: prod.id,
      type: 'PRODUCT',
      label: prod.product_name,
      children: [],
      data: prod
    };
    if (prod.category_id && categoryNodes[prod.category_id]) {
      categoryNodes[prod.category_id].children.push(node);
      // Increment category item count
      let currentCat = categoryNodes[prod.category_id];
      currentCat.itemCount = (currentCat.itemCount || 0) + 1;
      
      // We should technically bubble up counts, but for simplicity we just count direct children here. 
      // If we need recursive counts, we can do a post-order traversal.
    } else {
      // If product has no category, it goes under the type node
      if (prod.item_type && typeNodes[prod.item_type]) {
        typeNodes[prod.item_type].children.push(node);
        typeNodes[prod.item_type].itemCount = (typeNodes[prod.item_type].itemCount || 0) + 1;
      }
    }
  });

  // Post-order traversal to bubble up counts
  const bubbleUpCounts = (node: TreeNode): number => {
    let count = node.type === 'PRODUCT' ? 1 : 0;
    node.children.forEach(child => {
      count += bubbleUpCounts(child);
    });
    if (node.type !== 'PRODUCT') {
      node.itemCount = count;
    }
    return count;
  };

  Object.values(typeNodes).forEach(node => bubbleUpCounts(node));

  return Object.values(typeNodes);
}

export function InventoryExplorerTree({ hierarchy, selectedNodeId, onSelectNode, onCreateCategory, onCreateProduct, onRenameCategory, onDeleteCategory, onEditProduct }: InventoryExplorerTreeProps) {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['FINISHED_GOODS']));
  
  const tree = buildTree(hierarchy);

  const toggleExpand = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setExpandedNodes(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const renderNode = (node: TreeNode, depth: number = 0) => {
    const isExpanded = expandedNodes.has(node.id);
    const isSelected = selectedNodeId === node.id;
    const hasChildren = node.children.length > 0;

    return (
      <div key={node.id} className="select-none">
        <ContextMenu>
          <ContextMenuTrigger>
            <div 
              className={cn(
                "flex items-center py-1 px-2 cursor-pointer text-sm hover:bg-accent rounded-sm group",
                isSelected && "bg-accent text-accent-foreground font-medium",
                node.data?.status === 'archived' && "line-through opacity-60"
              )}
              style={{ paddingLeft: `${depth * 16 + 8}px` }}
              onClick={() => onSelectNode(node)}
            >
              <div 
                className="w-4 h-4 mr-1 flex items-center justify-center cursor-pointer text-muted-foreground hover:text-foreground"
                onClick={(e) => hasChildren && toggleExpand(e, node.id)}
              >
                {hasChildren ? (
                  isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />
                ) : <span className="w-4 h-4" />}
              </div>
              
              <div className="mr-2 text-muted-foreground flex-shrink-0">
                {node.type === 'INVENTORY_TYPE' && <Folder className="h-4 w-4 text-blue-500" fill="currentColor" fillOpacity={0.2} />}
                {node.type === 'CATEGORY' && <Folder className="h-4 w-4 text-yellow-500" fill="currentColor" fillOpacity={0.2} />}
                {node.type === 'PRODUCT' && <Package className="h-4 w-4 text-emerald-500" />}
              </div>
              
              <span className="truncate flex-1">{node.label}</span>
              
              {node.type !== 'PRODUCT' && node.itemCount !== undefined && (
                <span className="text-xs text-muted-foreground ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {node.itemCount}
                </span>
              )}
            </div>
          </ContextMenuTrigger>
          <ContextMenuContent className="w-48">
            {node.type === 'INVENTORY_TYPE' && (
              <ContextMenuItem onSelect={() => setTimeout(() => onCreateCategory(node.id), 0)}>
                New Category...
              </ContextMenuItem>
            )}
            {node.type === 'CATEGORY' && (
              <>
                <ContextMenuItem onSelect={() => setTimeout(() => onCreateCategory(node.data.item_type, node.id), 0)}>
                  New Subcategory...
                </ContextMenuItem>
                <ContextMenuItem onSelect={() => setTimeout(() => onCreateProduct(node.id), 0)}>
                  New Inventory Item...
                </ContextMenuItem>
                <ContextMenuItem onSelect={() => setTimeout(() => onEditCategory?.(node.id, node.data.category_name), 0)}>
                  Edit Category...
                </ContextMenuItem>
                {node.data?.status === 'archived' ? (
                  <ContextMenuItem className="text-destructive font-medium" onSelect={() => setTimeout(() => onDeleteCategory?.(node.id), 0)}>
                    Delete Category (Permanent)
                  </ContextMenuItem>
                ) : (
                  <ContextMenuItem className="text-destructive" onSelect={() => setTimeout(() => onArchiveCategory?.(node.id), 0)}>
                    Archive Category
                  </ContextMenuItem>
                )}
              </>
            )}
            {node.type === 'PRODUCT' && (
              <>
                <ContextMenuItem onSelect={() => setTimeout(() => onEditProduct?.(node.id, node.data.product_name), 0)}>
                  Edit Master Item...
                </ContextMenuItem>
                {node.data?.status === 'archived' ? (
                  <ContextMenuItem className="text-destructive font-medium" onSelect={() => setTimeout(() => onDeleteProduct?.(node.id), 0)}>
                    Delete Master Item (Permanent)
                  </ContextMenuItem>
                ) : (
                  <ContextMenuItem className="text-destructive" onSelect={() => setTimeout(() => onArchiveProduct?.(node.id), 0)}>
                    Archive Master Item
                  </ContextMenuItem>
                )}
              </>
            )}
          </ContextMenuContent>
        </ContextMenu>

        {isExpanded && hasChildren && (
          <div>
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="w-full h-full overflow-y-auto pr-2 pb-4 pt-2">
      {tree.map(node => renderNode(node, 0))}
    </div>
  );
}
