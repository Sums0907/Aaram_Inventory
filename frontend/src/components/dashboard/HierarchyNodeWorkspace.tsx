import React from 'react';
import type { TreeNode } from './InventoryExplorerTree';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Package, Layers, Activity, AlertTriangle, ArrowRightLeft, ShieldCheck } from 'lucide-react';
import { useDashboardKPIs, useDashboardExceptions } from '@/api/inventory';
import { Badge } from '@/components/ui/badge';

interface HierarchyNodeWorkspaceProps {
  node: TreeNode | null;
  onCreateCategory?: (parentType: string, parentId?: string) => void;
  onCreateProduct?: (categoryId: string) => void;
}

export function HierarchyNodeWorkspace({ node, onCreateCategory, onCreateProduct }: HierarchyNodeWorkspaceProps) {
  const { data: kpis } = useDashboardKPIs();
  const { data: exceptions } = useDashboardExceptions();

  if (!node) {
    return (
      <div className="p-6 h-full overflow-y-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Inventory Intelligence</h1>
          <p className="text-slate-500">Operational command center for physical inventory tracking.</p>
        </div>

        {/* Operational KPIs */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-500 flex items-center justify-between">
                Tracked SKUs
                <Package className="h-4 w-4 text-slate-400" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold tracking-tight text-slate-900">
                {kpis?.total_skus_tracked || 0}
              </div>
              <p className="text-xs text-slate-500 mt-1">Total physical items mapped</p>
            </CardContent>
          </Card>

          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-500 flex items-center justify-between">
                Current Stock Value
                <Activity className="h-4 w-4 text-emerald-500" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold tracking-tight text-emerald-600">
                ---
              </div>
              <p className="text-xs text-slate-500 mt-1">Total projected units value</p>
            </CardContent>
          </Card>

          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-500 flex items-center justify-between">
                Average Confidence
                <ShieldCheck className="h-4 w-4 text-indigo-500" />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold tracking-tight text-indigo-600">
                {kpis?.average_confidence_score || 0}%
              </div>
              <p className="text-xs text-slate-500 mt-1">System-wide data integrity</p>
            </CardContent>
          </Card>

          <Card className={`border-slate-200 shadow-sm relative overflow-hidden ${(kpis?.total_negative_inventory || 0) > 0 ? 'bg-red-50/30 border-red-200' : ''}`}>
            {(kpis?.total_negative_inventory || 0) > 0 && (
              <div className="absolute top-0 left-0 w-1 h-full bg-red-500" />
            )}
            <CardHeader className="pb-2">
              <CardTitle className={`text-sm font-medium flex items-center justify-between ${(kpis?.total_negative_inventory || 0) > 0 ? 'text-red-900' : 'text-slate-500'}`}>
                Negative Stock
                <AlertTriangle className={`h-4 w-4 ${(kpis?.total_negative_inventory || 0) > 0 ? 'text-red-500' : 'text-slate-400'}`} />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold tracking-tight ${(kpis?.total_negative_inventory || 0) > 0 ? 'text-red-700' : 'text-slate-900'}`}>
                {kpis?.total_negative_inventory || 0}
              </div>
              <p className={`text-xs mt-1 ${(kpis?.total_negative_inventory || 0) > 0 ? 'text-red-600' : 'text-slate-500'}`}>SKUs with unviable balances</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Exceptions Workbench */}
          <Card className="border-slate-200 shadow-sm flex flex-col h-[400px]">
            <CardHeader className="bg-slate-50/50 border-b flex-shrink-0">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg text-slate-900">Exceptions Workbench</CardTitle>
                  <CardDescription>Actionable inventory discrepancies</CardDescription>
                </div>
                <Badge variant="secondary" className="bg-red-100 text-red-700 hover:bg-red-100">
                  {exceptions?.length || 0} Open
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-0 overflow-y-auto flex-1 bg-slate-50/20">
              {exceptions && exceptions.length > 0 ? (
                <div className="divide-y divide-slate-100">
                  {exceptions.map((exc: any, idx: number) => (
                    <div key={idx} className="p-4 bg-white hover:bg-slate-50 transition-colors">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4 text-red-500" />
                          <span className="font-semibold text-sm text-slate-900">{exc.resolution_notes || 'Negative Inventory'}</span>
                        </div>
                        <span className="text-xs text-slate-500 font-mono">{exc.exception_number}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 space-y-3">
                  <ShieldCheck className="h-10 w-10 text-emerald-400" />
                  <p className="text-sm">No open exceptions</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-slate-200 shadow-sm flex flex-col h-[400px]">
             <CardHeader className="bg-slate-50/50 border-b flex-shrink-0">
              <CardTitle className="text-lg text-slate-900">Recent Activity</CardTitle>
              <CardDescription>Latest movements across the warehouse</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center text-slate-400 p-8 text-center h-full">
              <Activity className="h-10 w-10 text-blue-400 mb-4" />
              <p className="text-sm">Select an inventory node to view detailed activity.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

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
              <Button size="sm" variant="outline" onClick={() => onCreateCategory?.(node.data?.item_type || 'FINISHED_GOODS', node.id)}>New Subcategory</Button>
              <Button size="sm" onClick={() => onCreateProduct?.(node.id)}>New Item</Button>
            </>
          )}
          {node.type === 'PRODUCT' && (
            <>
              <Button size="sm" variant="outline">Receive Goods</Button>
              <Button size="sm">Edit Item</Button>
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
            <CardTitle className="text-sm font-medium">Current Stock</CardTitle>
            <Layers className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">---</div>
            <p className="text-xs text-muted-foreground">Coming soon</p>
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

      {node.type !== 'PRODUCT' && (
        <Card className="col-span-full">
          <CardHeader>
            <CardTitle>Inventory Items</CardTitle>
            <CardDescription>Items belonging to this {node.type.toLowerCase().replace('_', ' ')}.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-muted-foreground p-4 bg-muted/50 rounded-md text-center">
              Item table will be rendered here.
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
