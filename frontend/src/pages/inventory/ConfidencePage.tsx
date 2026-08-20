// @ts-nocheck
import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { useInventoryBalances, useInventoryConfidence } from "@/api/inventory"
import { ShieldCheck, ShieldAlert, ArrowRight, Search } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"

export function ConfidencePage() {
  const [selectedSkuId, setSelectedSkuId] = useState<string | null>(null)
  const [search, setSearch] = useState("")
  
  const { data: balances, isLoading } = useInventoryBalances()
  const { data: confidenceData, isLoading: isConfidenceLoading } = useInventoryConfidence(selectedSkuId)

  // Filter and sort by lowest confidence first
  const sortedBalances = [...(balances || [])]
    .filter(b => {
      if (!search) return true;
      const s = search.toLowerCase();
      return (b.sku_name?.toLowerCase().includes(s)) || (b.sku_code?.toLowerCase().includes(s));
    })
    .sort((a, b) => a.confidence_score - b.confidence_score)

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-600 bg-emerald-50"
    if (score >= 50) return "text-amber-600 bg-amber-50"
    return "text-rose-600 bg-rose-50"
  }

  const getProgressColor = (score: number) => {
    if (score >= 80) return "bg-emerald-500"
    if (score >= 50) return "bg-amber-500"
    return "bg-rose-500"
  }

  const selectedItem = balances?.find(b => b.sku_id === selectedSkuId)

  return (
    <div className="h-full flex flex-col space-y-6 max-w-5xl mx-auto w-full pb-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Inventory Confidence</h1>
        <p className="text-sm text-slate-500">System-generated trust scores based on movement patterns and count frequency.</p>
      </div>

      <div className="flex items-center gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input 
            placeholder="Search SKUs..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 bg-slate-50 border-slate-200"
          />
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex-1 flex flex-col">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Loading confidence scores...</div>
        ) : sortedBalances.length === 0 ? (
          <div className="p-8 text-center text-slate-500">No inventory balances found.</div>
        ) : (
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 text-slate-500 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 font-medium">Item</th>
                <th className="px-6 py-3 font-medium text-right">System Balance</th>
                <th className="px-6 py-3 font-medium text-right">Confidence Score</th>
                <th className="px-6 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sortedBalances.map(balance => (
                <tr 
                  key={balance.sku_id} 
                  className="hover:bg-slate-50 cursor-pointer transition-colors"
                  onClick={() => setSelectedSkuId(balance.sku_id)}
                >
                  <td className="px-6 py-4">
                    <div className="font-medium text-slate-900">{balance.sku_name}</div>
                    <div className="text-xs text-slate-500">{balance.sku_code}</div>
                  </td>
                  <td className="px-6 py-4 text-right font-mono font-medium text-slate-700">
                    {balance.balance}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-end gap-3">
                      <div className="flex flex-col items-end w-32">
                        <span className={cn("text-xs font-bold px-2 py-0.5 rounded-full mb-1", getScoreColor(balance.confidence_score))}>
                          {balance.confidence_score}%
                        </span>
                        <Progress value={balance.confidence_score} indicatorClassName={getProgressColor(balance.confidence_score)} className="h-1.5" />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <ArrowRight className="h-4 w-4 text-slate-400 inline-block" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Sheet open={!!selectedSkuId} onOpenChange={(o) => !o && setSelectedSkuId(null)}>
        <SheetContent className="sm:max-w-md overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Confidence Analysis</SheetTitle>
            <SheetDescription>
              Explainable AI breakdown of the confidence score.
            </SheetDescription>
          </SheetHeader>
          
          {selectedItem && (
            <div className="mt-6 space-y-6">
              <div className="flex items-center gap-4 bg-slate-50 p-4 rounded-xl border border-slate-100">
                <div className={cn("flex h-12 w-12 items-center justify-center rounded-full font-bold text-lg", getScoreColor(selectedItem.confidence_score))}>
                  {selectedItem.confidence_score}%
                </div>
                <div>
                  <h3 className="font-medium text-slate-900">{selectedItem.sku_name}</h3>
                  <div className="text-sm text-slate-500 font-mono">{selectedItem.sku_code}</div>
                </div>
              </div>

              {isConfidenceLoading ? (
                <div className="text-center text-sm text-slate-500 py-4">Analyzing patterns...</div>
              ) : confidenceData ? (
                <div className="space-y-6">
                  {confidenceData.positive_signals.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-emerald-700 flex items-center gap-2 mb-3">
                        <ShieldCheck className="h-4 w-4" /> Positive Signals
                      </h4>
                      <ul className="space-y-2">
                        {confidenceData.positive_signals.map((signal, idx) => (
                          <li key={idx} className="text-sm text-slate-600 bg-emerald-50/50 px-3 py-2 rounded-md border border-emerald-100">
                            {signal}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {confidenceData.negative_signals.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-rose-700 flex items-center gap-2 mb-3">
                        <ShieldAlert className="h-4 w-4" /> Negative Signals
                      </h4>
                      <ul className="space-y-2">
                        {confidenceData.negative_signals.map((signal, idx) => (
                          <li key={idx} className="text-sm text-slate-600 bg-rose-50/50 px-3 py-2 rounded-md border border-rose-100">
                            {signal}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {confidenceData.confidence_score < 70 && (
                    <div className="pt-4 flex gap-3">
                      <Button className="w-full bg-indigo-600 hover:bg-indigo-700">Request Physical Count</Button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-sm text-slate-500">Could not load detailed analysis.</div>
              )}
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  )
}
