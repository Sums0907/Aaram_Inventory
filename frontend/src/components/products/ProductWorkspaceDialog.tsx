import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useDeactivateSKU, useArchiveSKU, type SKUResponse } from "@/api/masters"
import { ImageIcon, Package, Info, History, ShieldAlert, Tag, Box, FileText, BarChart3, AlertCircle, CheckCircle2, Edit, EyeOff, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { SKUFormDialog } from "./SKUFormDialog"
import { useState } from "react"

import { QuickInventoryActionCard } from "./QuickInventoryActionCard"

interface ProductWorkspaceDialogProps {
  sku: SKUResponse | null
  open: boolean
  onOpenChange: (open: boolean) => void
  inventoryCount: number
}

export function ProductWorkspaceDialog({ sku, open, onOpenChange, inventoryCount }: ProductWorkspaceDialogProps) {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [activeTab, setActiveTab] = useState("overview")
  const deactivateMutation = useDeactivateSKU()
  const archiveMutation = useArchiveSKU()

  if (!sku) return null

  const handleHide = async () => {
    if (confirm("Are you sure you want to hide this SKU? It will become inactive.")) {
      await deactivateMutation.mutateAsync(sku.id)
    }
  }

  const handleDelete = async () => {
    if (confirm("Are you sure you want to delete/archive this SKU?")) {
      await archiveMutation.mutateAsync(sku.id)
      onOpenChange(false)
    }
  }

  const getProductHealth = () => {
    // Mock product health calculation
    let score = 100
    if (!sku.images?.length) score -= 20
    if (!sku.pricing?.selling_price) score -= 15
    if (!sku.description) score -= 10
    return score
  }

  const healthScore = getProductHealth()
  const healthStatus = healthScore > 90 ? "Excellent" : healthScore > 70 ? "Good" : "Needs Attention"

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[95vw] h-[90vh] p-0 flex flex-col gap-0 overflow-hidden bg-slate-50">
        
        {/* Header area */}
        <DialogHeader className="p-6 bg-white border-b flex-shrink-0 flex flex-row items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 bg-slate-100 rounded-lg border overflow-hidden flex items-center justify-center">
              {sku.images?.length ? (
                <img src={sku.images[0].image_url} alt={sku.sku_code} className="h-full w-full object-cover" />
              ) : (
                <ImageIcon className="h-6 w-6 text-slate-300" />
              )}
            </div>
            <div>
              <DialogTitle className="text-2xl font-bold text-slate-900 flex items-center gap-3">
                {sku.product?.product_name || "Unknown Product"}
                <Badge variant={sku.status?.toUpperCase() === 'ACTIVE' ? 'default' : 'secondary'} className={sku.status?.toUpperCase() === 'ACTIVE' ? 'bg-emerald-500 hover:bg-emerald-600' : ''}>
                  {sku.status}
                </Badge>
              </DialogTitle>
              <DialogDescription className="mt-1 font-mono text-sm text-slate-500 flex items-center gap-2">
                SKU: <span className="text-slate-900 font-semibold">{sku.sku_code}</span>
                {sku.product?.brand && (
                  <>
                    <span className="text-slate-300">•</span>
                    <span>Brand: {sku.product.brand}</span>
                  </>
                )}
              </DialogDescription>
            </div>
          </div>
          
          <div className="flex gap-4 text-right">
            <div className="flex flex-col items-end">
              <span className="text-xs text-slate-500 uppercase font-semibold">Inventory Balance</span>
              <span className={`text-2xl font-bold ${inventoryCount > 0 ? 'text-indigo-600' : 'text-rose-600'}`}>
                {inventoryCount} Units
              </span>
            </div>
            <div className="flex flex-col items-end border-l pl-4">
              <span className="text-xs text-slate-500 uppercase font-semibold">Product Health</span>
              <span className={`text-2xl font-bold ${healthScore > 90 ? 'text-emerald-600' : 'text-amber-500'}`}>
                {healthScore}%
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-2 mt-4 sm:mt-0 mr-8">
            <Button variant="outline" size="sm" className="gap-2" onClick={() => setIsEditDialogOpen(true)}>
              <Edit className="h-4 w-4" /> Edit
            </Button>
            {sku.status?.toUpperCase() === 'ACTIVE' && (
              <Button variant="outline" size="sm" className="gap-2 text-amber-600 hover:text-amber-700 hover:bg-amber-50 border-amber-200" onClick={handleHide} disabled={deactivateMutation.isPending}>
                <EyeOff className="h-4 w-4" /> {deactivateMutation.isPending ? "Hiding..." : "Hide"}
              </Button>
            )}
            <Button variant="outline" size="sm" className="gap-2 text-rose-600 hover:text-rose-700 hover:bg-rose-50 border-rose-200" onClick={handleDelete} disabled={archiveMutation.isPending}>
              <Trash2 className="h-4 w-4" /> {archiveMutation.isPending ? "Deleting..." : "Delete"}
            </Button>
          </div>
        </DialogHeader>

        {/* Workspace Body */}
        <div className="flex-1 overflow-hidden flex flex-col p-6 bg-slate-50">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col h-full w-full">
            <TabsList className="w-full justify-start border-b rounded-none h-12 bg-transparent p-0 mb-6 gap-6">
              <TabsTrigger value="overview" className="data-[state=active]:border-b-2 data-[state=active]:border-indigo-600 rounded-none h-full data-[state=active]:shadow-none data-[state=active]:bg-transparent px-0 font-medium text-slate-600">
                <Info className="h-4 w-4 mr-2" /> Overview
              </TabsTrigger>
              <TabsTrigger value="inventory" className="data-[state=active]:border-b-2 data-[state=active]:border-indigo-600 rounded-none h-full data-[state=active]:shadow-none data-[state=active]:bg-transparent px-0 font-medium text-slate-600">
                <Box className="h-4 w-4 mr-2" /> Inventory
              </TabsTrigger>
              <TabsTrigger value="pricing" className="data-[state=active]:border-b-2 data-[state=active]:border-indigo-600 rounded-none h-full data-[state=active]:shadow-none data-[state=active]:bg-transparent px-0 font-medium text-slate-600">
                <Tag className="h-4 w-4 mr-2" /> Pricing
              </TabsTrigger>
              <TabsTrigger value="specifications" className="data-[state=active]:border-b-2 data-[state=active]:border-indigo-600 rounded-none h-full data-[state=active]:shadow-none data-[state=active]:bg-transparent px-0 font-medium text-slate-600">
                <FileText className="h-4 w-4 mr-2" /> Specifications
              </TabsTrigger>
              <TabsTrigger value="ledger" className="data-[state=active]:border-b-2 data-[state=active]:border-indigo-600 rounded-none h-full data-[state=active]:shadow-none data-[state=active]:bg-transparent px-0 font-medium text-slate-600">
                <History className="h-4 w-4 mr-2" /> Ledger
              </TabsTrigger>
              <TabsTrigger value="confidence" className="data-[state=active]:border-b-2 data-[state=active]:border-indigo-600 rounded-none h-full data-[state=active]:shadow-none data-[state=active]:bg-transparent px-0 font-medium text-slate-600">
                <ShieldAlert className="h-4 w-4 mr-2" /> Confidence
              </TabsTrigger>
            </TabsList>

            <ScrollArea className="flex-1 h-full pr-4">
              
              <TabsContent value="overview" className="mt-0 space-y-6 h-full pb-10">
                {/* Product Identity */}
                <div className="grid grid-cols-3 gap-6">
                  
                  <div className="col-span-2 space-y-6">
                    <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-4">
                      <h3 className="font-semibold text-slate-900 border-b pb-2">Product Identity</h3>
                      <div className="grid grid-cols-2 gap-y-4 text-sm">
                        <div>
                          <span className="text-slate-500 block mb-1">Product Code</span>
                          <span className="font-medium text-slate-900">{sku.product?.product_code || "-"}</span>
                        </div>
                        <div>
                          <span className="text-slate-500 block mb-1">Category</span>
                          <span className="font-medium text-slate-900">{sku.product?.product_type || "-"}</span>
                        </div>
                        <div>
                          <span className="text-slate-500 block mb-1">Barcode</span>
                          <span className="font-medium text-slate-900">{sku.barcode || "-"}</span>
                        </div>
                        <div>
                          <span className="text-slate-500 block mb-1">Created On</span>
                          <span className="font-medium text-slate-900">{new Date(sku.created_on).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-4">
                      <h3 className="font-semibold text-slate-900 border-b pb-2">Inventory Snapshot</h3>
                      <div className="grid grid-cols-4 gap-4">
                         <div className="p-4 bg-slate-50 rounded-lg border text-center">
                           <p className="text-sm text-slate-500 mb-1">Current Stock</p>
                           <p className="text-xl font-bold text-slate-900">{inventoryCount}</p>
                         </div>
                         <div className="p-4 bg-slate-50 rounded-lg border text-center opacity-70">
                           <p className="text-sm text-slate-500 mb-1">Reserved</p>
                           <p className="text-xl font-bold text-slate-900">0</p>
                         </div>
                         <div className="p-4 bg-slate-50 rounded-lg border text-center opacity-70">
                           <p className="text-sm text-slate-500 mb-1">Incoming</p>
                           <p className="text-xl font-bold text-slate-900">0</p>
                         </div>
                         <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-100 text-center">
                           <p className="text-sm text-emerald-600 mb-1">Confidence</p>
                           <p className="text-xl font-bold text-emerald-700">98%</p>
                         </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-6">
                    <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm space-y-4 h-full">
                      <h3 className="font-semibold text-slate-900 border-b pb-2">Product Health</h3>
                      <div className="flex items-center justify-between mb-4">
                        <span className="text-3xl font-bold text-slate-900">{healthScore}%</span>
                        <Badge variant="outline" className={healthScore > 90 ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}>
                          {healthStatus}
                        </Badge>
                      </div>
                      
                      <div className="space-y-3 text-sm">
                        <div className="flex items-center gap-2">
                          {sku.images?.length ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <AlertCircle className="h-4 w-4 text-amber-500" />}
                          <span className="text-slate-600">Images Uploaded</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {sku.pricing?.selling_price ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <AlertCircle className="h-4 w-4 text-amber-500" />}
                          <span className="text-slate-600">Pricing Complete</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                          <span className="text-slate-600">Inventory Verified</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <AlertCircle className="h-4 w-4 text-amber-500" />
                          <span className="text-slate-600">Physical Count Pending</span>
                        </div>
                      </div>
                    </div>
                    
                    <QuickInventoryActionCard
                      skuId={sku.id}
                      currentStock={inventoryCount}
                      itemType={sku.product?.item_type}
                      onViewLedger={() => setActiveTab("ledger")}
                    />
                  </div>
                  
                </div>
              </TabsContent>

              <TabsContent value="specifications" className="mt-0 bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                <h3 className="font-semibold text-slate-900 border-b pb-4 mb-6">Product Specifications</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-y-6 gap-x-8 text-sm">
                  <div>
                    <span className="text-slate-500 block mb-1">Color</span>
                    <span className="font-medium text-slate-900">{sku.color || "-"}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block mb-1">Size</span>
                    <span className="font-medium text-slate-900">{sku.size || "-"}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block mb-1">Pattern</span>
                    <span className="font-medium text-slate-900">{sku.pattern || "-"}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block mb-1">Material</span>
                    <span className="font-medium text-slate-900">{sku.material || "-"}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block mb-1">Thread Count</span>
                    <span className="font-medium text-slate-900">{sku.thread_count || "-"}</span>
                  </div>
                </div>
                {Object.keys(sku.attribute_values || {}).length > 0 && (
                  <>
                    <h4 className="font-medium text-slate-700 mt-8 mb-4 border-b pb-2">Other Attributes</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-y-6 gap-x-8 text-sm">
                      {Object.entries(sku.attribute_values).map(([key, value]) => (
                        <div key={key}>
                          <span className="text-slate-500 block mb-1 capitalize">{key.replace(/_/g, ' ')}</span>
                          <span className="font-medium text-slate-900">{value as React.ReactNode}</span>
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </TabsContent>

              <TabsContent value="pricing" className="mt-0 bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
                <h3 className="font-semibold text-slate-900 border-b pb-4 mb-6">Commercial Information</h3>
                <div className="grid grid-cols-3 gap-6">
                  <div className="p-6 bg-slate-50 rounded-lg border text-center">
                    <p className="text-sm text-slate-500 uppercase tracking-wider font-semibold mb-2">Selling Price</p>
                    <p className="text-3xl font-bold text-slate-900">₹{sku.pricing?.selling_price || 0}</p>
                  </div>
                  <div className="p-6 bg-slate-50 rounded-lg border text-center">
                    <p className="text-sm text-slate-500 uppercase tracking-wider font-semibold mb-2">MRP</p>
                    <p className="text-3xl font-medium text-slate-600 line-through">₹{sku.pricing?.mrp || 0}</p>
                  </div>
                  <div className="p-6 bg-slate-50 rounded-lg border text-center">
                    <p className="text-sm text-slate-500 uppercase tracking-wider font-semibold mb-2">Cost Price</p>
                    <p className="text-3xl font-medium text-slate-700">₹{sku.pricing?.cost_price || 0}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-6 mt-8 border-t pt-8 text-sm">
                  <div>
                    <span className="text-slate-500 block mb-1">GST Percentage</span>
                    <span className="font-medium text-slate-900">{sku.pricing?.gst_percentage || 0}%</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block mb-1">HSN Code</span>
                    <span className="font-medium text-slate-900">{sku.pricing?.hsn_code || "-"}</span>
                  </div>
                </div>
              </TabsContent>

              {/* Placeholder Tabs */}
              <TabsContent value="inventory" className="mt-0 h-full pb-10">
                <div className="grid grid-cols-3 gap-6 h-full">
                  <div className="col-span-2 space-y-6">
                    <div className="bg-white p-12 text-center rounded-lg border border-slate-200 shadow-sm">
                      <Box className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-slate-900 mb-2">Inventory Management</h3>
                      <p className="text-slate-500 max-w-md mx-auto">This tab will contain warehouse-wise stock, reserved stock, and incoming purchases.</p>
                    </div>
                  </div>
                  <div className="col-span-1">
                    <QuickInventoryActionCard
                      skuId={sku.id}
                      currentStock={inventoryCount}
                      itemType={sku.product?.item_type}
                      onViewLedger={() => setActiveTab("ledger")}
                    />
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="ledger" className="mt-0 bg-white p-12 text-center rounded-lg border border-slate-200 shadow-sm">
                <History className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-slate-900 mb-2">Inventory Ledger</h3>
                <p className="text-slate-500 max-w-md mx-auto">Chronological record of every inventory movement for this SKU, directly from the Truth Engine.</p>
              </TabsContent>

              <TabsContent value="confidence" className="mt-0 bg-white p-12 text-center rounded-lg border border-slate-200 shadow-sm">
                <ShieldAlert className="h-12 w-12 text-emerald-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-slate-900 mb-2">Inventory Confidence: 98%</h3>
                <p className="text-slate-500 max-w-md mx-auto">This tab will provide actionable reasons and warnings for why the system trusts the inventory count.</p>
              </TabsContent>

            </ScrollArea>
          </Tabs>
        </div>
      </DialogContent>
      {open && (
        <SKUFormDialog
          open={isEditDialogOpen}
          onOpenChange={setIsEditDialogOpen}
          initialData={sku}
        />
      )}
    </Dialog>
  )
}
