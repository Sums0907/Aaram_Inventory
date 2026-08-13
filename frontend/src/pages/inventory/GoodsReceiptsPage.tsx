import { useState } from "react"
import { useGoodsReceipts } from "@/api/goods-receipts"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Plus, Eye } from "lucide-react"
import { GRNFormDialog } from "@/components/inbound/GRNFormDialog"
import { GoodsReceiptDetailDialog } from "@/components/inbound/GoodsReceiptDetailDialog"
import { useSuppliers } from "@/api/suppliers"

export function GoodsReceiptsPage() {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [detailOpen, setDetailOpen] = useState(false)
  const [selectedGrn, setSelectedGrn] = useState<string | null>(null)
  
  const { data, isLoading } = useGoodsReceipts(0, 100)
  const { data: suppliersData } = useSuppliers(0, 100)
  
  const grns = data?.data || []
  const suppliers = suppliersData?.data || []
  
  const getSupplierName = (id: string) => suppliers.find(s => s.id === id)?.name || id
  
  const handleView = (id: string) => {
    setSelectedGrn(id)
    setDetailOpen(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Goods Receipts</h1>
          <p className="text-sm text-slate-500">
            Record inbound inventory movements and link them to suppliers.
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setDialogOpen(true)} className="bg-indigo-600 hover:bg-indigo-700">
            <Plus className="mr-2 h-4 w-4" />
            Receive Goods
          </Button>
        </div>
      </div>
      
      <div className="rounded-md border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>GRN Number</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Supplier</TableHead>
              <TableHead>Invoice</TableHead>
              <TableHead>Warehouse</TableHead>
              <TableHead className="text-right">SKUs</TableHead>
              <TableHead className="text-right">Units</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created By</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead className="w-[100px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={11} className="text-center h-24 text-slate-500">
                  Loading goods receipts...
                </TableCell>
              </TableRow>
            ) : grns.length === 0 ? (
              <TableRow>
                <TableCell colSpan={11} className="text-center h-24 text-slate-500">
                  No Goods Receipts recorded yet.
                </TableCell>
              </TableRow>
            ) : (
              grns.map((grn) => {
                const totalUnits = grn.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;
                
                return (
                <TableRow key={grn.id} className="cursor-pointer hover:bg-slate-50" onClick={() => handleView(grn.id)}>
                  <TableCell className="font-medium text-indigo-600">{grn.grn_number}</TableCell>
                  <TableCell>{new Date(grn.receipt_date).toLocaleDateString()}</TableCell>
                  <TableCell>{getSupplierName(grn.supplier_id)}</TableCell>
                  <TableCell className="text-slate-500">{grn.invoice_number || "-"}</TableCell>
                  <TableCell className="text-slate-500">Main Warehouse</TableCell>
                  <TableCell className="text-right">{grn.items?.length || 0}</TableCell>
                  <TableCell className="text-right font-medium">{totalUnits}</TableCell>
                  <TableCell>
                    <span className="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                      {grn.status}
                    </span>
                  </TableCell>
                  <TableCell className="text-slate-500 text-xs truncate max-w-[100px]">System</TableCell>
                  <TableCell className="text-slate-500 text-xs">{new Date(grn.created_on).toLocaleString()}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); handleView(grn.id); }}>
                      <Eye className="h-4 w-4 mr-2 text-slate-400" />
                      View
                    </Button>
                  </TableCell>
                </TableRow>
                )
              })
            )}
          </TableBody>
        </Table>
      </div>

      <GRNFormDialog 
        open={dialogOpen} 
        onOpenChange={setDialogOpen}
      />

      <GoodsReceiptDetailDialog
        open={detailOpen}
        onOpenChange={setDetailOpen}
        grnId={selectedGrn}
      />
    </div>
  )
}
