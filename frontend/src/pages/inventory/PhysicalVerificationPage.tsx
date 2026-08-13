import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { useInventoryBalances, useCreateStockCountAdjustment } from "@/api/inventory"
import { ClipboardCheck, Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { cn } from "@/lib/utils"
import { format } from "date-fns"

export function PhysicalVerificationPage() {
  const { toast } = useToast()
  const [search, setSearch] = useState("")
  
  // State to hold the drafted physical counts per SKU ID
  const [physicalCounts, setPhysicalCounts] = useState<Record<string, string>>({})
  
  const { data: balances, isLoading } = useInventoryBalances()
  const stockCountMutation = useCreateStockCountAdjustment()

  const filteredBalances = balances?.filter(b => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (b.sku_name?.toLowerCase().includes(s)) || (b.sku_code?.toLowerCase().includes(s))
  }) || []

  // Default to a system-wide stock count ref
  const stockCountRef = `PC-${format(new Date(), 'yyyyMMdd')}`

  const handleCommitCount = (skuId: string, systemQty: number, warehouseId: string) => {
    const countStr = physicalCounts[skuId]
    if (countStr === undefined || countStr === "") return

    const physicalCount = parseInt(countStr, 10)
    if (isNaN(physicalCount) || physicalCount < 0) {
      toast({ title: "Invalid Count", description: "Please enter a valid positive number.", variant: "destructive" })
      return
    }

    const difference = physicalCount - systemQty
    if (difference === 0) {
      toast({ title: "No Variance", description: "Physical count matches system perfectly." })
      // We could optionally just clear the input here, but maybe we want to log a 0 adjustment to boost confidence.
      // For now we'll log it to explicitly record a stock count.
    }

    stockCountMutation.mutate(
      {
        warehouse_id: warehouseId,
        sku_id: skuId,
        system_quantity: systemQty,
        physical_count: physicalCount,
        difference: difference,
        stock_count_reference: stockCountRef,
        count_date: new Date().toISOString().split('T')[0]
      },
      {
        onSuccess: () => {
          toast({ title: "Stock Count Logged", description: "Physical verification recorded successfully." })
          setPhysicalCounts(prev => {
            const next = { ...prev }
            delete next[skuId]
            return next
          })
        }
      }
    )
  }

  return (
    <div className="h-full flex flex-col space-y-6 max-w-5xl mx-auto w-full pb-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Physical Verification</h1>
          <p className="text-sm text-slate-500">Conduct stock counts and automatically log variance adjustments.</p>
        </div>
        <div className="bg-slate-100 text-slate-600 px-3 py-1.5 rounded-md font-mono text-sm font-medium border border-slate-200">
          Ref: {stockCountRef}
        </div>
      </div>

      <div className="flex items-center gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input 
            placeholder="Search SKUs to verify..." 
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
                <th className="px-6 py-3 font-medium text-right w-48">Physical Count</th>
                <th className="px-6 py-3 font-medium text-right w-32">Variance</th>
                <th className="px-6 py-3 font-medium w-32 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredBalances.map(balance => {
                const countStr = physicalCounts[balance.sku_id]
                const hasInput = countStr !== undefined && countStr !== ""
                const physicalCount = parseInt(countStr || "0", 10)
                const variance = hasInput && !isNaN(physicalCount) ? physicalCount - balance.balance : null
                
                return (
                  <tr key={balance.sku_id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-900">{balance.sku_name}</div>
                      <div className="text-xs text-slate-500">{balance.sku_code}</div>
                    </td>
                    <td className="px-6 py-4 text-right font-mono text-slate-500">
                      {balance.balance}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Input
                        type="number"
                        placeholder="Count"
                        value={physicalCounts[balance.sku_id] ?? ""}
                        onChange={(e) => setPhysicalCounts({...physicalCounts, [balance.sku_id]: e.target.value})}
                        className="w-full text-right font-mono"
                        min="0"
                      />
                    </td>
                    <td className="px-6 py-4 text-right font-mono">
                      {variance !== null ? (
                        <span className={cn(
                          "px-2 py-0.5 rounded-full font-bold text-xs",
                          variance > 0 ? "bg-emerald-100 text-emerald-700" : 
                          variance < 0 ? "bg-rose-100 text-rose-700" : 
                          "bg-slate-100 text-slate-700"
                        )}>
                          {variance > 0 ? '+' : ''}{variance}
                        </span>
                      ) : (
                        <span className="text-slate-300">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <Button
                        size="sm"
                        disabled={!hasInput || stockCountMutation.isPending}
                        onClick={() => handleCommitCount(balance.sku_id, balance.balance, balance.warehouse)}
                        className={cn("w-full gap-2", hasInput ? "bg-indigo-600 hover:bg-indigo-700 text-white" : "")}
                        variant={hasInput ? "default" : "outline"}
                      >
                        <ClipboardCheck className="h-4 w-4" />
                        Log
                      </Button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
