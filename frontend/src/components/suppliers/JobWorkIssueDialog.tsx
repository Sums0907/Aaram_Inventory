import { formatQuantityValue } from "@/lib/utils"
import { useState, useMemo } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useSKUs } from "@/api/masters"
import { useInventoryBalances } from "@/api/inventory"
import { useCreateJobWorkIssue } from "@/api/job-works"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, SelectGroup, SelectLabel } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import { Loader2 } from "lucide-react"

interface JobWorkIssueDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  supplierId: string
  supplierName: string
}

export function JobWorkIssueDialog({ open, onOpenChange, supplierId, supplierName }: JobWorkIssueDialogProps) {
  const { toast } = useToast()
  const { data: skus } = useSKUs()
  const { data: balances } = useInventoryBalances()
  const issueMutation = useCreateJobWorkIssue()
  
  const [selectedSkuId, setSelectedSkuId] = useState<string>("")
  const [quantity, setQuantity] = useState<string>("")
  const issueDate = new Date().toLocaleDateString() // Default current date
  
  const selectedSku = useMemo(() => skus?.find(s => s.id === selectedSkuId), [skus, selectedSkuId])
  
  const issuableSkus = useMemo(() => {
    return skus?.filter(sku => sku.product?.item_type !== "FINISHED_GOODS") || []
  }, [skus])

  const groupedSkus = useMemo(() => {
    const groups: Record<string, any[]> = {}
    issuableSkus.forEach(sku => {
      const itemType = sku.product?.item_type?.replace("_", " ") || "UNKNOWN TYPE"
      const category = sku.product?.product_type || "Uncategorized"
      const groupName = `${itemType} — ${category}`
      if (!groups[groupName]) groups[groupName] = []
      groups[groupName].push(sku)
    })
    return groups
  }, [issuableSkus])

  // Find balance for selected SKU across any warehouse (Primary Inventory)
  const availableBalance = useMemo(() => {
    if (!selectedSkuId || !balances) return 0
    return balances.filter(b => b.sku_id === selectedSkuId).reduce((acc, curr) => acc + (curr.balance || 0), 0)
  }, [balances, selectedSkuId])

  const handleIssue = async () => {
    if (!selectedSkuId) {
      toast({ title: "Error", description: "Please select a material to issue", variant: "destructive" })
      return
    }
    const numQuantity = parseFloat(quantity)
    if (isNaN(numQuantity) || numQuantity <= 0) {
      toast({ title: "Error", description: "Please enter a valid quantity", variant: "destructive" })
      return
    }
    
    if (numQuantity > availableBalance) {
      toast({ title: "Error", description: `Insufficient inventory. Available: ${availableBalance} ${selectedSku?.uom?.unit_code || ""}`, variant: "destructive" })
      return
    }

    try {
      await issueMutation.mutateAsync({
        job_worker_id: supplierId,
        item_id: selectedSkuId,
        quantity: numQuantity
      })
      toast({ title: "Success", description: "Material issued successfully" })
      onOpenChange(false)
      setSelectedSkuId("")
      setQuantity("")
    } catch (error: any) {
      toast({ title: "Error", description: error?.response?.data?.message || "Failed to issue material", variant: "destructive" })
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Issue Material to Job Worker</DialogTitle>
          <DialogDescription>
            Record material sent to {supplierName} for processing.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label>Job Worker</Label>
            <Input value={supplierName} disabled className="bg-slate-50" />
          </div>
          
          <div className="grid gap-2">
            <Label>Issue Date</Label>
            <Input value={issueDate} disabled className="bg-slate-50" />
          </div>

          <div className="grid gap-2">
            <Label>Material</Label>
            <Select value={selectedSkuId} onValueChange={setSelectedSkuId}>
              <SelectTrigger>
                <SelectValue placeholder="Select inventory item..." />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(groupedSkus).map(([groupName, groupSkus]) => (
                  <SelectGroup key={groupName}>
                    <SelectLabel className="bg-slate-50 text-slate-500 font-semibold sticky top-0">
                      {groupName}
                    </SelectLabel>
                    {groupSkus.map(sku => {
                      const bal = balances?.filter(b => b.sku_id === sku.id)?.reduce((a,c) => a + (c.balance || 0), 0) || 0
                      const name = `${sku.product?.product_name || "Unknown"} (${sku.sku_code})`
                      return (
                        <SelectItem key={sku.id} value={sku.id} className="pl-6">
                          {name} · {bal} {sku.uom?.unit_code || "units"} available
                        </SelectItem>
                      )
                    })}
                  </SelectGroup>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-2">
            <Label>Available Stock</Label>
            <div className="text-sm font-medium text-slate-700">
              {selectedSku ? `${availableBalance} ${selectedSku.uom?.unit_code || ""}` : "-"}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label>Quantity</Label>
              <Input 
                type="number" 
                value={quantity} 
                onChange={e => setQuantity(e.target.value)}
                placeholder="e.g. 280"
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
          <Button onClick={handleIssue} disabled={issueMutation.isPending}>
            {issueMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Issue Material
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
