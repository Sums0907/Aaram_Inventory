// @ts-nocheck
import { useState } from "react"
import { useBOMs } from "@/api/boms"
import { useSKUs } from "@/api/masters"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Plus, Eye, Filter } from "lucide-react"
import { BOMFormDialog } from "@/components/products/BOMFormDialog"

export function BOMSetupPage() {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [selectedBom, setSelectedBom] = useState<any>(null)
  const [showArchived, setShowArchived] = useState(false)
  
  const { data: bomsData, isLoading } = useBOMs()
  const { data: skus } = useSKUs()
  const boms = bomsData || []

  const visibleBoms = boms.filter((bom: any) => showArchived || bom.status !== 'ARCHIVED')

  const getSkuName = (id: string) => {
    const sku = skus?.find((s: any) => s.id === id)
    if (!sku) return id
    return `${sku.product?.product_name || "Unknown"} ${sku.item_code ? `(${sku.item_code})` : ""}`
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Bill of Materials (BOM)</h1>
          <p className="text-sm text-slate-500">
            Manage recipes and conversion ratios for Job Work and Manufacturing.
          </p>
        </div>
        <div className="flex gap-3">
          <Button 
            variant="outline" 
            onClick={() => setShowArchived(!showArchived)}
            className={showArchived ? "bg-slate-100" : ""}
          >
            <Filter className="mr-2 h-4 w-4 text-slate-500" />
            {showArchived ? "Hide Archived" : "Show Archived"}
          </Button>
          <Button className="bg-indigo-600 hover:bg-indigo-700" onClick={() => setIsAddDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New BOM
          </Button>
        </div>
      </div>
      
      <div className="rounded-md border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>BOM Number</TableHead>
              <TableHead>Target Item</TableHead>
              <TableHead>Version</TableHead>
              <TableHead>Base Quantity</TableHead>
              <TableHead>Components</TableHead>
              <TableHead>Effective Dates</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-[100px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center h-24 text-slate-500">
                  Loading BOMs...
                </TableCell>
              </TableRow>
            ) : visibleBoms.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center h-24 text-slate-500">
                  No Bill of Materials found.
                </TableCell>
              </TableRow>
            ) : (
              visibleBoms.map((bom: any) => (
                <TableRow key={bom.id} className={`hover:bg-slate-50 transition-colors ${bom.status === 'ARCHIVED' ? 'opacity-75 bg-slate-50' : ''}`}>
                  <TableCell className="font-medium text-indigo-600">{bom.bom_number}</TableCell>
                  <TableCell className="font-medium">{getSkuName(bom.target_item_id)}</TableCell>
                  <TableCell>v{bom.version || 1}</TableCell>
                  <TableCell>{bom.target_quantity}</TableCell>
                  <TableCell>{bom.items?.length || 0} items</TableCell>
                  <TableCell className="text-sm text-slate-500">
                    {bom.effective_from ? new Date(bom.effective_from).toLocaleDateString() : 'Always'} 
                    {bom.effective_to ? ` - ${new Date(bom.effective_to).toLocaleDateString()}` : ''}
                  </TableCell>
                  <TableCell>
                    <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                      bom.status === 'ACTIVE' ? 'bg-green-50 text-green-700 ring-green-600/20' : 
                      bom.status === 'DRAFT' ? 'bg-amber-50 text-amber-700 ring-amber-600/20' : 
                      'bg-slate-50 text-slate-600 ring-slate-500/20'
                    }`}>
                      {bom.status}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" onClick={() => setSelectedBom(bom)}>
                      <Eye className="h-4 w-4 mr-2 text-slate-400" />
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
      <BOMFormDialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen} />
      <BOMFormDialog open={!!selectedBom} onOpenChange={(open) => !open && setSelectedBom(null)} bom={selectedBom} />
    </div>
  )
}
