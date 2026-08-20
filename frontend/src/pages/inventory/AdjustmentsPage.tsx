// @ts-nocheck
import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { useInventoryBalances, useCreateManualAdjustment } from "@/api/inventory"
import { Settings2, Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { cn } from "@/lib/utils"
import { Textarea } from "@/components/ui/textarea"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet"

export function AdjustmentsPage() {
  const { toast } = useToast()
  const [search, setSearch] = useState("")
  const [selectedSku, setSelectedSku] = useState<any>(null)
  
  const [adjQuantity, setAdjQuantity] = useState("")
  const [adjReason, setAdjReason] = useState("")
  
  const { data: balances, isLoading } = useInventoryBalances()
  const adjustmentMutation = useCreateManualAdjustment()

  const filteredBalances = balances?.filter(b => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (b.sku_name?.toLowerCase().includes(s)) || (b.sku_code?.toLowerCase().includes(s))
  }) || []

  const handleAdjust = () => {
    if (!selectedSku) return
    const qty = parseInt(adjQuantity, 10)
    if (isNaN(qty) || qty === 0) {
      toast({ title: "Invalid Quantity", description: "Adjustment must be non-zero.", variant: "destructive" })
      return
    }
    
    adjustmentMutation.mutate(
      {
        warehouse_id: selectedSku.warehouse_id,
        sku_id: selectedSku.sku_id,
        quantity: qty,
        reason: adjReason,
        reference_number: `ADJ-${Date.now().toString().slice(-6)}`,
        adjustment_date: new Date().toISOString().split('T')[0]
      },
      {
        onSuccess: () => {
          toast({ title: "Adjustment Created", description: `Successfully adjusted inventory by ${qty}.` })
          setSelectedSku(null)
          setAdjQuantity("")
          setAdjReason("")
        }
      }
    )
  }

  return (
    <div className="h-full flex flex-col space-y-6 max-w-5xl mx-auto w-full pb-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Manual Adjustments</h1>
        <p className="text-sm text-slate-500">Correct inventory balances ad-hoc.</p>
      </div>

      <div className="flex items-center gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input 
            placeholder="Search SKUs to adjust..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 bg-slate-50 border-slate-200"
          />
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex-1 flex flex-col">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Loading inventory...</div>
        ) : filteredBalances.length === 0 ? (
          <div className="p-8 text-center text-slate-500">No inventory found matching your search.</div>
        ) : (
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 sticky top-0 z-10">
              <tr>
                <th className="px-6 py-3 font-medium">Inventory Item</th>
                <th className="px-6 py-3 font-medium text-right w-32">System Qty</th>
                <th className="px-6 py-3 font-medium w-32 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredBalances.map(balance => (
                <tr key={balance.sku_id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-medium text-slate-900">{balance.sku_name}</div>
                    <div className="text-xs text-slate-500">{balance.sku_code}</div>
                  </td>
                  <td className="px-6 py-4 text-right font-mono text-slate-500">
                    {balance.balance}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <Button
                      size="sm"
                      onClick={() => setSelectedSku(balance)}
                      className="w-full gap-2"
                      variant="outline"
                    >
                      <Settings2 className="h-4 w-4" />
                      Adjust
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Sheet open={!!selectedSku} onOpenChange={(o) => !o && setSelectedSku(null)}>
        <SheetContent className="sm:max-w-md">
          <SheetHeader>
            <SheetTitle>Manual Adjustment</SheetTitle>
            <SheetDescription>
              Increase or decrease the system quantity.
            </SheetDescription>
          </SheetHeader>
          
          {selectedSku && (
            <div className="mt-6 space-y-6">
              <div>
                <h3 className="text-sm font-medium text-slate-500 mb-1">Item</h3>
                <div className="text-lg font-semibold text-slate-900">{selectedSku.sku_name}</div>
                <div className="text-sm text-slate-500 font-mono">{selectedSku.sku_code}</div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-slate-500 mb-1">Current Balance</h3>
                  <div className="text-xl font-mono text-slate-700">{selectedSku.balance}</div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-slate-500 mb-1">Adjustment Qty</h3>
                  <Input 
                    type="number" 
                    placeholder="e.g. -5 or 10" 
                    value={adjQuantity}
                    onChange={(e) => setAdjQuantity(e.target.value)}
                    className="font-mono"
                  />
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-slate-500 mb-1">Reason for Adjustment</h3>
                <Textarea 
                  placeholder="Explain why this adjustment is being made..."
                  value={adjReason}
                  onChange={(e) => setAdjReason(e.target.value)}
                  className="min-h-[120px]"
                />
              </div>

              <div className="pt-4 flex gap-3">
                <Button 
                  onClick={handleAdjust} 
                  disabled={adjustmentMutation.isPending || !adjQuantity || !adjReason.trim()}
                  className="w-full bg-indigo-600 hover:bg-indigo-700"
                >
                  {adjustmentMutation.isPending ? "Adjusting..." : "Confirm Adjustment"}
                </Button>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  )
}
