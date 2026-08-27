// @ts-nocheck
import React, { useState } from 'react';
import type { TreeNode } from './InventoryExplorerTree';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Package, Layers, Activity, AlertTriangle, ArrowRightLeft, ShieldCheck, MoreHorizontal, Edit, Archive, LayoutGrid, List } from 'lucide-react';
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
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
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

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pt-4">
          {rootCategories.map((cat: any, index: number) => {
            const subCategories = hierarchy?.categories?.filter((c: any) => c.parent_id === cat.id) || [];
            const masterItems = hierarchy?.products?.filter((p: any) => p.category_id === cat.id) || [];
            
            // A subtle gradient background based on index to make the grid look varied and premium
            const gradients = [
              "from-indigo-500 to-purple-600",
              "from-blue-500 to-cyan-600",
              "from-emerald-500 to-teal-600",
              "from-rose-500 to-orange-600",
              "from-slate-700 to-gray-900"
            ];
            const gradientClass = gradients[index % gradients.length];
            
            return (
              <div 
                key={cat.id} 
                className="group relative flex flex-col bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer h-[320px]"
                onClick={() => onNavigate?.({
                  id: cat.id,
                  type: 'CATEGORY',
                  label: cat.category_name,
                  children: [],
                  data: cat
                })}
              >
                {/* Visual Header */}
                <div className={`h-36 w-full bg-gradient-to-br ${gradientClass} p-5 relative overflow-hidden`}>
                  {/* Abstract background pattern */}
                  <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '16px 16px' }}></div>
                  
                  <div className="relative z-10 flex justify-between items-start">
                    <Badge variant="secondary" className="bg-white/20 hover:bg-white/30 text-white border-none backdrop-blur-md font-medium tracking-wide">
                      {cat.item_type.replace('_', ' ')}
                    </Badge>
                    <div className="h-10 w-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-md">
                      <Layers className="h-5 w-5 text-white" />
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div className="p-6 flex-1 flex flex-col relative bg-white">
                  {/* Overlapping title block to create depth */}
                  <div className="-mt-12 mb-3 z-20">
                    <h3 className="text-xl font-bold text-slate-900 drop-shadow-sm bg-white inline-block px-3 py-1.5 rounded-lg border border-slate-100 shadow-sm leading-tight line-clamp-1">
                      {cat.category_name}
                    </h3>
                  </div>
                  
                  <p className="text-sm text-slate-500 line-clamp-2 mb-4 leading-relaxed">
                    {cat.description || "Manage products and inventory configurations for this master category."}
                  </p>
                  
                  {/* Stats Grid */}
                  <div className="mt-auto grid grid-cols-2 gap-3">
                    <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 flex flex-col">
                      <span className="text-2xl font-black text-indigo-600 tracking-tight">{masterItems.length}</span>
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mt-1">Master Items</span>
                    </div>
                    <div className="bg-slate-50 rounded-xl p-3 border border-slate-100 flex flex-col">
                      <span className="text-2xl font-black text-slate-700 tracking-tight">{subCategories.length}</span>
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mt-1">Subcategories</span>
                    </div>
                  </div>
                  
                  {/* Hover reveal action */}
                  <div className="absolute inset-x-0 bottom-0 h-1 bg-indigo-500 transform translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
                </div>
              </div>
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
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle>Inventory Items</CardTitle>
                <CardDescription>Items belonging to this {node.type.toLowerCase().replace('_', ' ')}.</CardDescription>
              </div>
              <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200 h-10">
                <button 
                  onClick={() => setViewMode("grid")}
                  className={`h-full px-3 rounded-md flex items-center justify-center transition-all duration-200 ${viewMode === "grid" ? "bg-white text-indigo-600 shadow-sm font-medium" : "text-slate-500 hover:text-slate-700 hover:bg-slate-200/50"}`}
                  title="Grid View"
                >
                  <LayoutGrid className="h-4 w-4 mr-2" />
                  Grid
                </button>
                <button 
                  onClick={() => setViewMode("list")}
                  className={`h-full px-3 rounded-md flex items-center justify-center transition-all duration-200 ${viewMode === "list" ? "bg-white text-indigo-600 shadow-sm font-medium" : "text-slate-500 hover:text-slate-700 hover:bg-slate-200/50"}`}
                  title="List View"
                >
                  <List className="h-4 w-4 mr-2" />
                  List
                </button>
              </div>
            </CardHeader>
            <CardContent>
              {itemsToDisplay.length > 0 ? (
                viewMode === "grid" ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pt-2">
                  {itemsToDisplay.map((item: any) => {
                    const stock = getProductStock(item);
                    const variants = getProductVariantCount(item);
                    // Determine stock status for color coding
                    let stockStatusColor = "bg-emerald-500";
                    let stockStatusText = "In Stock";
                    if (stock === 0) {
                      stockStatusColor = "bg-red-500";
                      stockStatusText = "Out of Stock";
                    } else if (stock < 20) {
                      stockStatusColor = "bg-amber-500";
                      stockStatusText = "Low Stock";
                    }

                    // A subtle gradient background based on ID to make the grid look varied and premium
                    const gradients = [
                      "from-indigo-100 to-purple-100",
                      "from-blue-100 to-cyan-100",
                      "from-emerald-100 to-teal-100",
                      "from-rose-100 to-orange-100",
                      "from-slate-100 to-gray-200"
                    ];
                    const gradientClass = gradients[item.product_name.length % gradients.length];

                    return (
                      <div 
                        key={item.id}
                        className="group relative flex flex-col bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all overflow-hidden cursor-pointer"
                        onClick={() => onNavigate?.({
                          id: item.id,
                          type: 'PRODUCT',
                          label: item.product_name,
                          children: [],
                          data: item
                        })}
                      >
                        {/* Action Menu (Floating) */}
                        <div className="absolute top-2 right-2 z-10" onClick={(e) => e.stopPropagation()}>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="secondary" size="icon" className="h-8 w-8 bg-white/80 backdrop-blur-sm hover:bg-white border shadow-sm">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
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
                        </div>

                        {/* Image Placeholder */}
                        <div className={`h-40 w-full bg-gradient-to-br ${gradientClass} flex items-center justify-center opacity-80 group-hover:opacity-100 transition-opacity`}>
                          <Package className="h-12 w-12 text-slate-800/20" />
                        </div>

                        {/* Details */}
                        <div className="p-4 flex-1 flex flex-col">
                          <div className="mb-1">
                            <span className="text-xs font-medium text-slate-500 tracking-wider uppercase">{item.product_code}</span>
                          </div>
                          <h3 className="text-base font-semibold text-slate-900 leading-tight mb-2 line-clamp-2">
                            {item.product_name}
                          </h3>
                          
                          <div className="mt-auto pt-4 space-y-3">
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-slate-500">{variants} {variants === 1 ? 'Variant' : 'Variants'}</span>
                              <span className="font-medium text-slate-700">{item.brand || 'No Brand'}</span>
                            </div>
                            
                            {/* Stock Indicator */}
                            <div className="space-y-1.5">
                              <div className="flex items-center justify-between text-xs font-medium">
                                <span className="text-slate-600">{stockStatusText}</span>
                                <span className="text-slate-900">{stock} units</span>
                              </div>
                              <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                                <div 
                                  className={`h-full rounded-full ${stockStatusColor}`} 
                                  style={{ width: `${Math.min(100, Math.max(5, (stock / 100) * 100))}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                  </div>
                ) : (
                  <div className="overflow-x-auto pt-2">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Item Name</TableHead>
                          <TableHead>Code</TableHead>
                          <TableHead>Brand</TableHead>
                          <TableHead>Variants</TableHead>
                          <TableHead className="text-right">Total Stock</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {itemsToDisplay.map((item: any) => {
                          const stock = getProductStock(item);
                          const variants = getProductVariantCount(item);
                          return (
                            <TableRow key={item.id} className="cursor-pointer hover:bg-slate-50" onClick={() => onNavigate?.({ id: item.id, type: 'PRODUCT', label: item.product_name, children: [], data: item })}>
                              <TableCell className="font-medium">
                                <div className="flex items-center">
                                  <div className="h-8 w-8 rounded bg-slate-100 flex items-center justify-center mr-3">
                                    <Package className="h-4 w-4 text-slate-400" />
                                  </div>
                                  {item.product_name}
                                </div>
                              </TableCell>
                              <TableCell>{item.product_code}</TableCell>
                              <TableCell>{item.brand || '-'}</TableCell>
                              <TableCell>{variants}</TableCell>
                              <TableCell className="text-right">
                                <Badge variant={stock > 0 ? "secondary" : "outline"}>{stock} units</Badge>
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </div>
                )
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
