import React from 'react';
import type { TreeNode } from './InventoryExplorerTree';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Package, Layers, Activity, AlertTriangle, ArrowRightLeft, ShieldCheck, MoreHorizontal, Edit, Archive } from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { useDashboardKPIs, useDashboardExceptions, useInventoryBalances, useInventoryPosition } from '@/api/inventory';
import { useSKUs } from '@/api/masters';
import { Badge } from '@/components/ui/badge';

interface HierarchyNodeWorkspaceProps {
  node: TreeNode | null;
  onCreateCategory?: (parentType: string, parentId?: string) => void;
  onCreateProduct?: (categoryId: string) => void;
  onEditProduct?: (productId: string, currentName: string) => void;
  onEditCategory?: (categoryId: string, currentName: string) => void;
  onArchiveCategory?: (categoryId: string) => void;
  onDeleteCategory?: (categoryId: string) => void;
  onArchiveProduct?: (productId: string) => void;
  onDeleteProduct?: (productId: string) => void;
  hierarchy?: any;
}

export function HierarchyNodeWorkspace({ node, onCreateCategory, onCreateProduct, onEditProduct, onEditCategory, onArchiveCategory, onDeleteCategory, onArchiveProduct, onDeleteProduct, hierarchy }: HierarchyNodeWorkspaceProps) {
  const { data: kpis } = useDashboardKPIs();
  const { data: exceptions } = useDashboardExceptions();
  const { data: balances } = useInventoryBalances();
  const { data: positions } = useInventoryPosition();
  const { data: allSkus } = useSKUs();

  const getProductStock = (product: any) => {
    if (!positions || !allSkus) return 0;
    
    // Find SKUs for this product
    const productSkus = allSkus.filter((s: any) => s.product?.id === product.id || s.product_id === product.id);
    
    let totalStock = 0;
    for (const sku of productSkus) {
      const pos = positions.find((p: any) => p.sku_id === sku.id);
      if (pos) {
        totalStock += pos.total_stock;
      }
    }
    return totalStock;
  };

  const getProductPosition = (product: any) => {
    if (!positions || !allSkus) return null;
    const productSkus = allSkus.filter((s: any) => s.product?.id === product.id || s.product_id === product.id);
    
    let total = 0;
    let wh = 0;
    let jw = 0;
    let jobWorkers: { [key: string]: number } = {};
    
    for (const sku of productSkus) {
      const pos = positions.find((p: any) => p.sku_id === sku.id);
      if (pos) {
        total += pos.total_stock;
        wh += pos.warehouse_stock;
        jw += pos.job_worker_total;
        pos.job_workers.forEach((worker: any) => {
           jobWorkers[worker.name] = (jobWorkers[worker.name] || 0) + worker.stock;
        });
      }
    }
    
    return {
      total_stock: total,
      warehouse_stock: wh,
      job_worker_total: jw,
      job_workers: Object.entries(jobWorkers).map(([name, stock]) => ({ name, stock }))
    };
  };

  const getProductVariantCount = (product: any) => {
    if (!allSkus) return 0;
    return allSkus.filter((s: any) => s.product?.id === product.id || s.product_id === product.id).length;
  };

  if (!node) {
    const rootCategories = hierarchy?.categories?.filter((c: any) => !c.parent_id) || [];
    
    return (
      <div className="p-6 h-full overflow-y-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Inventory Catalog</h1>
            <p className="text-slate-500">Overview of all inventory categories and master items.</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => onCreateCategory?.('FINISHED_GOODS')} className="bg-slate-900">
              <Package className="mr-2 h-4 w-4" />
              New Root Category
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-blue-50/50 border-blue-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-blue-800">Total Items</CardTitle>
              <Package className="h-4 w-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-900">{kpis?.total_items || 0}</div>
            </CardContent>
          </Card>
          <Card className="bg-emerald-50/50 border-emerald-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-emerald-800">Total Value</CardTitle>
              <Layers className="h-4 w-4 text-emerald-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-900">₹{(kpis?.total_value || 0).toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card className="bg-amber-50/50 border-amber-100">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-amber-800">Low Stock Alerts</CardTitle>
              <AlertTriangle className="h-4 w-4 text-amber-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-amber-900">{kpis?.low_stock_alerts || 0}</div>
            </CardContent>
          </Card>
          <Card className="bg-slate-50/50 border-slate-200">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-700">Open Exceptions</CardTitle>
              <Activity className="h-4 w-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-800">{exceptions?.length || 0}</div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-4">
          {rootCategories.map((cat: any) => {
            const subCategories = hierarchy?.categories?.filter((c: any) => c.parent_id === cat.id) || [];
            const masterItems = hierarchy?.products?.filter((p: any) => p.category_id === cat.id) || [];
            
            return (
              <Card key={cat.id} className="border-slate-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{cat.category_name}</CardTitle>
                    <Badge variant="outline" className="text-xs font-normal">
                      {cat.item_type.replace('_', ' ')}
                    </Badge>
                  </div>
                  <CardDescription className="line-clamp-2">
                    {cat.description || `Root category containing ${subCategories.length} subcategories and ${masterItems.length} items.`}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {subCategories.length > 0 ? (
                    <div className="space-y-2">
                      <p className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wider">Subcategories</p>
                      <div className="flex flex-wrap gap-2">
                        {subCategories.slice(0, 6).map((sub: any) => (
                          <Badge key={sub.id} variant="secondary" className="font-normal bg-slate-100 text-slate-700 hover:bg-slate-200">
                            {sub.category_name}
                          </Badge>
                        ))}
                        {subCategories.length > 6 && (
                          <Badge variant="secondary" className="font-normal text-slate-500">
                            +{subCategories.length - 6} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  ) : masterItems.length > 0 ? (
                    <div className="space-y-2">
                      <p className="text-xs font-medium text-slate-500 mb-2 uppercase tracking-wider">Master Items</p>
                      <div className="space-y-1">
                        {masterItems.slice(0, 4).map((item: any) => (
                          <div key={item.id} className="text-sm text-slate-700 flex items-center truncate">
                            <span className="w-1.5 h-1.5 rounded-full bg-slate-300 mr-2 flex-shrink-0" />
                            <span className="truncate">{item.product_name}</span>
                          </div>
                        ))}
                        {masterItems.length > 4 && (
                          <div className="text-xs text-slate-400 pl-3 pt-1">
                            +{masterItems.length - 4} more items
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-6 text-center text-slate-400">
                      <Layers className="h-8 w-8 mb-2 opacity-20" />
                      <p className="text-sm">Empty Category</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    );
  }

  const currentStockStr = node.type === 'PRODUCT' 
    ? getProductStock(node.data).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    : "---";

  const positionNode = node.type === 'PRODUCT' ? getProductPosition(node.data) : null;

  return (
    <div className="p-6 h-full overflow-y-auto space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-1">
            {node.type.replace('_', ' ')}
          </p>
          <h2 className="text-2xl font-semibold tracking-tight">{node.label}</h2>
          {node.data?.description && (
            <p className="text-muted-foreground mt-1">{node.data.description}</p>
          )}
        </div>
        
        <div className="flex gap-2">
          {node.type === 'INVENTORY_TYPE' && (
            <Button size="sm" onClick={() => onCreateCategory?.(node.id)}>New Category</Button>
          )}
          {node.type === 'CATEGORY' && (
            <>
              {node.data?.item_type !== 'PACKAGING' && (
                <Button size="sm" variant="outline" onClick={() => onCreateCategory && onCreateCategory(node.data?.item_type || 'FINISHED_GOODS', node.id)}>
                  + Subcategory
                </Button>
              )}
              <Button size="sm" onClick={() => onCreateProduct && onCreateProduct(node.id)}>
                + Master Item
              </Button>
              <Button size="sm" variant="secondary" onClick={() => onEditCategory && onEditCategory(node.id, node.name)}>
                Edit Category
              </Button>
              {node.data?.status === 'archived' ? (
                <Button size="sm" variant="destructive" onClick={() => onDeleteCategory && onDeleteCategory(node.id)}>
                  Delete Category
                </Button>
              ) : (
                <Button size="sm" variant="destructive" onClick={() => onArchiveCategory && onArchiveCategory(node.id)}>
                  Archive Category
                </Button>
              )}
            </>
          )}
          {node.type === 'PRODUCT' && (
            <>
              <Button size="sm" variant="outline">Receive Goods</Button>
              <Button size="sm" onClick={() => onEditProduct && onEditProduct(node.id, node.name)}>Edit Item</Button>
              {node.data?.status === 'archived' ? (
                <Button size="sm" variant="destructive" onClick={() => onDeleteProduct && onDeleteProduct(node.id)}>Delete Item</Button>
              ) : (
                <Button size="sm" variant="destructive" onClick={() => onArchiveProduct && onArchiveProduct(node.id)}>Archive Item</Button>
              )}
            </>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Items</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{node.itemCount ?? 1}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Stock</CardTitle>
            <Layers className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-800">
              {currentStockStr}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Low Stock Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">In last 7 days</p>
          </CardContent>
        </Card>
      </div>

      {node.type === 'PRODUCT' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Inventory Position</CardTitle>
              <CardDescription>Comprehensive stock holding overview across Warehouse and Job Workers.</CardDescription>
            </CardHeader>
            <CardContent>
              {positionNode ? (
                <div className="font-mono text-sm leading-relaxed text-slate-700 bg-slate-50 p-6 rounded-lg border border-slate-200">
                  <div className="flex">
                    <span className="w-56 font-bold text-slate-900">Total Stock</span>
                    <span className="text-blue-700 font-bold">{positionNode.total_stock.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                  </div>
                  <div className="text-slate-400">│</div>
                  <div className="flex">
                    <span className="w-56"><span className="text-slate-400">├──</span> Warehouse Stock</span>
                    <span className="text-emerald-700 font-medium">{positionNode.warehouse_stock.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                  </div>
                  <div className="text-slate-400">│</div>
                  <div>
                    <div className="flex">
                      <span className="w-56"><span className="text-slate-400">└──</span> Job Worker Pending</span>
                      <span className="text-amber-700 font-medium">{positionNode.job_worker_total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                    </div>
                    {positionNode.job_workers.length > 0 && (
                      <div className="ml-9 border-l border-slate-300 mt-1 pb-1">
                        {positionNode.job_workers.map((jw: any, idx: number) => {
                          const isLast = idx === positionNode.job_workers.length - 1;
                          const prefix = isLast ? "└──" : "├──";
                          return (
                            <div key={jw.name} className="flex pt-1 text-slate-600">
                              <span className="w-[188px]"><span className="text-slate-400 ml-4 mr-2">{prefix}</span> {jw.name}</span>
                              <span className="">{jw.stock.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-sm text-muted-foreground p-4 bg-muted/50 rounded-md text-center">
                  Loading inventory position...
                </div>
              )}
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Variants (SKUs)</CardTitle>
              <CardDescription>All variants associated with this item.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground p-4 bg-muted/50 rounded-md text-center">
                Variant management will be integrated here.
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Related Items</CardTitle>
              <CardDescription>Bill of Materials & Packaging.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground p-4 bg-muted/50 rounded-md text-center border border-dashed">
                Related items (e.g., Raw Materials, Packaging) will appear here.
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {node.type !== 'PRODUCT' && (() => {
        // Calculate items to display
        const itemsToDisplay = hierarchy?.products?.filter((p: any) => {
          if (node.type === 'CATEGORY') return p.category_id === node.id;
          if (node.type === 'INVENTORY_TYPE') return p.item_type === node.id;
          return false;
        }) || [];

        return (
          <Card className="col-span-full">
            <CardHeader>
              <CardTitle>Inventory Items</CardTitle>
              <CardDescription>Items belonging to this {node.type.toLowerCase().replace('_', ' ')}.</CardDescription>
            </CardHeader>
            <CardContent>
              {itemsToDisplay.length > 0 ? (
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Code</TableHead>
                        <TableHead>Name</TableHead>
                        <TableHead>Brand</TableHead>
                        <TableHead className="text-right">Variants</TableHead>
                        <TableHead className="text-right">Total Stock</TableHead>
                        <TableHead className="w-[80px]"></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {itemsToDisplay.map((item: any) => (
                        <TableRow key={item.id}>
                          <TableCell className="font-medium">{item.product_code}</TableCell>
                          <TableCell>{item.product_name}</TableCell>
                          <TableCell>{item.brand || '-'}</TableCell>
                          <TableCell className="text-right">{getProductVariantCount(item)}</TableCell>
                          <TableCell className="text-right font-semibold">
                            {getProductStock(item)}
                          </TableCell>
                          <TableCell>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon" className="h-8 w-8"><MoreHorizontal className="h-4 w-4" /></Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem onClick={() => onEditProduct && onEditProduct(item.id, item.product_name)}>
                                  <Edit className="h-4 w-4 mr-2" /> Edit
                                </DropdownMenuItem>
                                {item.status === 'archived' ? (
                                  <DropdownMenuItem className="text-destructive font-medium" onClick={() => onDeleteProduct?.(item.id)}>
                                    Delete Item
                                  </DropdownMenuItem>
                                ) : (
                                  <DropdownMenuItem className="text-destructive" onClick={() => onArchiveProduct && onArchiveProduct(item.id)}>
                                    <Archive className="h-4 w-4 mr-2" /> Archive
                                  </DropdownMenuItem>
                                )}
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <div className="text-sm text-muted-foreground p-8 bg-muted/30 rounded-md text-center border border-dashed">
                  No items found. Click "New Inventory Item" from the context menu to create one.
                </div>
              )}
            </CardContent>
          </Card>
        );
      })()}
    </div>
  );
}
