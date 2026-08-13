import { formatQuantityValue } from "@/lib/utils"
import { useState, useMemo } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useSKUs } from "@/api/masters"
import { usePendingStock, useCreateJobWorkReturn } from "@/api/job-works"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, SelectGroup, SelectLabel } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import { Loader2 } from "lucide-react"

interface JobWorkReturnDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  supplierId: string
  supplierName: string
  defaultSkuId?: string
}

export function JobWorkReturnDialog({ open, onOpenChange, supplierId, supplierName, defaultSkuId }: JobWorkReturnDialogProps) {
  const { toast } = useToast()
  const { data: skus } = useSKUs()
  const { data: pendingStock } = usePendingStock(supplierId)
  const returnMutation = useCreateJobWorkReturn()
  
  const [selectedSkuId, setSelectedSkuId] = useState<string>(defaultSkuId || "")
  const [quantity, setQuantity] = useState<string>("")
  const returnDate = new Date().toLocaleDateString()
  
  const selectedSku = useMemo(() => skus?.find(s => s.id === selectedSkuId), [skus, selectedSkuId])
  
  const skusWithPendingStock = useMemo(() => {
    if (!skus || !pendingStock) return []
    return skus.filter(sku => {
      const stock = pendingStock.find(s => s.item_id === sku.id)
      return stock && stock.pending_quantity > 0
    })
  }, [skus, pendingStock])

  const groupedSkus = useMemo(() => {
    const groups: Record<string, any[]> = {}
    skusWithPendingStock.forEach(sku => {
      const itemType = sku.product?.item_type?.replace("_", " ") || "UNKNOWN TYPE"
      const category = sku.product?.product_type || "Uncategorized"
      const groupName = `${itemType} — ${category}`
      if (!groups[groupName]) groups[groupName] = []
      groups[groupName].push(sku)
    })
    return groups
  }, [skusWithPendingStock])
  
  const pendingBalance = useMemo(() => {
    if (!selectedSkuId || !pendingStock) return 0
    const stock = pendingStock.find(s => s.item_id === selectedSkuId)
    return stock ? stock.pending_quantity : 0
  }, [pendingStock, selectedSkuId])

  const handleReturn = async () => {
    if (!selectedSkuId) {
      toast({ title: "Error", description: "Please select a material to return", variant: "destructive" })
      return
    }
    const numQuantity = parseFloat(quantity)
    if (isNaN(numQuantity) || numQuantity <= 0) {
      toast({ title: "Error", description: "Please enter a valid quantity", variant: "destructive" })
      return
    }
    
    if (numQuantity > pendingBalance) {
      toast({ title: "Error", description: `Return quantity cannot exceed pending quantity. Pending: ${pendingBalance} ${selectedSku?.uom?.unit_code || ""}`, variant: "destructive" })
      return
    }

    try {
      await returnMutation.mutateAsync({
        job_worker_id: supplierId,
        item_id: selectedSkuId,
        quantity: numQuantity
      })
      toast({ title: "Success", description: "Material returned successfully" })
      onOpenChange(false)
      setSelectedSkuId("")
      setQuantity("")
    } catch (error: any) {
      toast({ title: "Error", description: error?.response?.data?.message || "Failed to return material", variant: "destructive" })
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Record Material Return</DialogTitle>
          <DialogDescription>
            Record unused material returned by {supplierName}.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label>Job Worker</Label>
            <Input value={supplierName} disabled className="bg-slate-50" />
          </div>
          
          <div className="grid gap-2">
            <Label>Return Date</Label>
            <Input value={returnDate} disabled className="bg-slate-50" />
          </div>

          <div className="grid gap-2">
            <Label>Material</Label>
            <Select value={selectedSkuId} onValueChange={setSelectedSkuId}>
              <SelectTrigger>
                <SelectValue placeholder="Select pending material..." />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(groupedSkus).map(([groupName, groupSkus]) => (
                  <SelectGroup key={groupName}>
                    <SelectLabel className="bg-slate-50 text-slate-500 font-semibold sticky top-0">
                      {groupName}
                    </SelectLabel>
                    {groupSkus.map(sku => {
                      const stock = pendingStock?.find(s => s.item_id === sku.id)
                      const name = `${sku.product?.product_name || "Unknown"} (${sku.sku_code})`
                      return (
                        <SelectItem key={sku.id} value={sku.id} className="pl-6">
                          {name} · {stock?.pending_quantity || 0} {sku.uom?.unit_code || "units"} pending
                        </SelectItem>
                      )
                    })}
                  </SelectGroup>
                ))}
                {skusWithPendingStock?.length === 0 && (
                  <SelectItem value="none" disabled>
                    No pending material to return
                  </SelectItem>
                )}
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-2">
            <Label>Pending Stock</Label>
            <div className="text-sm font-medium text-slate-700">
              {selectedSku ? `${pendingBalance} ${selectedSku.uom?.unit_code || ""}` : "-"}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label>Quantity</Label>
              <Input 
                type="number" 
                value={quantity} 
                onChange={e => setQuantity(e.target.value)}
                placeholder="e.g. 50"
                step="any"
              />
            </div>
            <div className="grid gap-2">
              <Label>UOM</Label>
              <Input 
                value={selectedSku?.uom?.unit_code || ""} 
                disabled 
                placeholder="-"
                className="bg-slate-50"
              />
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleReturn} disabled={returnMutation.isPending || pendingBalance === 0}>
            {returnMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Record Return
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
