import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { useGoodsReceipt } from "@/api/goods-receipts"
import { useSuppliers } from "@/api/suppliers"
import { useSKUs } from "@/api/masters"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
  grnId: string | null
}

export function GoodsReceiptDetailDialog({ open, onOpenChange, grnId }: Props) {
  const { data: grn, isLoading } = useGoodsReceipt(grnId || "")
  const { data: suppliersData } = useSuppliers(0, 100)
  const { data: skusData } = useSKUs()

  if (!open || !grnId) return null

  const suppliers = suppliersData?.data || []
  const getSupplierName = (id: string) => suppliers.find(s => s.id === id)?.name || id
  
  const getSkuCode = (id: string) => {
    const sku = skusData?.find((s: any) => s.id === id)
    return sku ? `${sku.sku_code} - ${sku.product?.product_name || ""}` : id
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Goods Receipt Note (GRN) Details</DialogTitle>
          <DialogDescription>
            Reference: {grn?.grn_number}
          </DialogDescription>
        </DialogHeader>

        {isLoading || !grn ? (
          <div className="py-12 text-center text-slate-500">Loading details...</div>
        ) : (
          <div className="space-y-6 pt-4">
            {/* Header Details */}
            <div className="grid grid-cols-2 gap-y-4 gap-x-8 text-sm bg-slate-50 p-4 rounded-lg border border-slate-100">
              <div>
                <span className="text-slate-500 block mb-1">Supplier</span>
                <span className="font-medium text-slate-900">{getSupplierName(grn.supplier_id)}</span>
              </div>
              <div>
                <span className="text-slate-500 block mb-1">Receipt Date</span>
                <span className="font-medium text-slate-900">{new Date(grn.receipt_date).toLocaleDateString()}</span>
              </div>
              <div>
                <span className="text-slate-500 block mb-1">Invoice Number</span>
                <span className="font-medium text-slate-900">{grn.invoice_number || "-"}</span>
              </div>
              <div>
                <span className="text-slate-500 block mb-1">Warehouse</span>
                <span className="font-medium text-slate-900">Main Warehouse</span>
              </div>
              <div className="col-span-2">
                <span className="text-slate-500 block mb-1">Remarks</span>
                <span className="font-medium text-slate-900">{grn.remarks || "-"}</span>
              </div>
            </div>

            {/* Inventory Impact */}
            <div>
              <h3 className="text-lg font-medium tracking-tight mb-4 text-slate-900 border-b pb-2">Inventory Impact</h3>
              <div className="rounded-md border bg-white overflow-hidden">
                <Table>
                  <TableHeader className="bg-slate-50">
                    <TableRow>
                      <TableHead>SKU</TableHead>
                      <TableHead className="text-right">Received Qty</TableHead>
                      <TableHead className="text-right">UOM</TableHead>
                      <TableHead>Movement Type</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {grn.items?.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{getSkuCode(item.sku_id)}</TableCell>
                        <TableCell className="text-right font-medium text-green-600">+{item.quantity}</TableCell>
                        <TableCell className="text-right text-slate-500">{item.unit_of_measure || "PCS"}</TableCell>
                        <TableCell>
                          <span className="inline-flex items-center rounded bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                            PURCHASE_RECEIPT
                          </span>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
            
            <div className="pt-4 text-xs text-slate-400 flex justify-between border-t">
              <span>Created by {grn.created_by || "System"} on {new Date(grn.created_on).toLocaleString()}</span>
              <span>Status: <span className="font-medium text-green-600">{grn.status}</span></span>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
