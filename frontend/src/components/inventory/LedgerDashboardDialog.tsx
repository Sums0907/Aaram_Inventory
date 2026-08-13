import { formatQuantityValue } from "@/lib/utils"
import React from "react"
import { useInventoryLedger, useInventoryConfidence } from "@/api/inventory"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Loader2, CheckCircle2, AlertCircle, TrendingDown, TrendingUp, History } from "lucide-react"

interface LedgerDashboardDialogProps {
  skuId: string | null
  skuCode: string
  skuName: string
  isOpen: boolean
  onClose: () => void
}

export function LedgerDashboardDialog({ skuId, skuCode, skuName, isOpen, onClose }: LedgerDashboardDialogProps) {
  const { data: ledger, isLoading: isLedgerLoading } = useInventoryLedger(skuId)
  const { data: confidence, isLoading: isConfidenceLoading } = useInventoryConfidence(skuId)

  const isLoading = isLedgerLoading || isConfidenceLoading

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-5xl max-h-[85vh] overflow-hidden flex flex-col bg-slate-50 p-0 border-0 shadow-2xl rounded-2xl">
        <DialogHeader className="p-6 bg-white border-b border-slate-100 flex-shrink-0">
          <div className="flex justify-between items-start">
            <div>
              <DialogTitle className="text-2xl font-bold text-slate-900 tracking-tight">{skuName}</DialogTitle>
              <DialogDescription className="text-slate-500 font-mono mt-1">{skuCode}</DialogDescription>
            </div>
            {confidence && (
              <div className="flex flex-col items-end">
                <span className="text-sm text-slate-500 mb-1">Confidence Score</span>
                <Badge 
                  variant="outline" 
                  className={`text-lg px-3 py-1 font-bold ${
                    confidence.confidence_score >= 90 ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                    confidence.confidence_score >= 70 ? 'bg-amber-50 text-amber-700 border-amber-200' :
                    'bg-red-50 text-red-700 border-red-200'
                  }`}
                >
                  {confidence.confidence_score}%
                </Badge>
              </div>
            )}
          </div>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-48">
              <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
            </div>
          ) : (
            <div className="grid lg:grid-cols-3 gap-6">
              
              {/* Left Column: Confidence Engine Signals */}
              <div className="lg:col-span-1 space-y-6">
                <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-5">
                  <h3 className="font-semibold text-slate-900 flex items-center gap-2 mb-4">
                    <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                    Positive Signals
                  </h3>
                  <ul className="space-y-3">
                    {confidence?.positive_signals.map((sig, idx) => (
                      <li key={idx} className="text-sm text-slate-600 flex items-start gap-2 leading-relaxed">
                        <span className="text-emerald-500 font-bold">✓</span> {sig}
                      </li>
                    ))}
                    {confidence?.positive_signals.length === 0 && (
                      <li className="text-sm text-slate-400 italic">No positive signals found.</li>
                    )}
                  </ul>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-5">
                  <h3 className="font-semibold text-slate-900 flex items-center gap-2 mb-4">
                    <AlertCircle className="h-4 w-4 text-red-500" />
                    Negative Signals
                  </h3>
                  <ul className="space-y-3">
                    {confidence?.negative_signals.map((sig, idx) => (
                      <li key={idx} className="text-sm text-slate-600 flex items-start gap-2 leading-relaxed">
                        <span className="text-red-500 font-bold">⚠</span> {sig}
                      </li>
                    ))}
                    {confidence?.negative_signals.length === 0 && (
                      <li className="text-sm text-slate-400 italic">No negative signals found.</li>
                    )}
                  </ul>
                </div>
              </div>

              {/* Right Column: Inventory Ledger Timeline */}
              <div className="lg:col-span-2">
                <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-5 h-full">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                      <History className="h-4 w-4 text-indigo-500" />
                      Inventory Ledger
                    </h3>
                    <div className="text-sm">
                      <span className="text-slate-500">Closing Balance: </span>
                      <span className="font-bold text-slate-900 text-lg">{ledger?.closing_balance}</span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    {ledger?.entries.length === 0 ? (
                      <p className="text-sm text-slate-500 italic text-center py-8">No inventory movements recorded yet.</p>
                    ) : (
                      <div className="relative border-l border-slate-200 ml-3 space-y-6 pb-4 max-h-[500px] overflow-y-auto pr-4">
                        {ledger?.entries.map((entry, idx) => {
                          const isNegative = entry.movement.quantity < 0;
                          return (
                            <div key={idx} className="relative pl-6 group">
                              {/* Timeline Dot */}
                              <div className={`absolute -left-[5px] top-1.5 h-2.5 w-2.5 rounded-full ring-4 ring-white ${isNegative ? 'bg-amber-500' : 'bg-emerald-500'}`} />
                              
                              <div className="flex justify-between items-start p-2 -my-2 rounded-lg group-hover:bg-slate-50 transition-colors">
                                <div>
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                                      {new Date(entry.movement.movement_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })}
                                    </span>
                                    <Badge variant="secondary" className="text-[10px] uppercase font-mono px-2 py-0 h-5">
                                      {entry.movement.movement_type.replace('_', ' ')}
                                    </Badge>
                                  </div>
                                  <p className="text-sm text-slate-600 mt-1">
                                    {entry.movement.reference_type} <span className="font-mono text-slate-400">#{entry.movement.reference_number}</span>
                                  </p>
                                </div>
                                
                                <div className="text-right">
                                  <div className={`text-sm font-bold flex items-center justify-end gap-1 ${isNegative ? 'text-amber-600' : 'text-emerald-600'}`}>
                                    {isNegative ? <TrendingDown className="h-3 w-3" /> : <TrendingUp className="h-3 w-3" />}
                                    {entry.movement.quantity > 0 ? '+' : ''}{formatQuantityValue(entry.movement.quantity)}
                                  </div>
                                  <div className="text-xs text-slate-400 mt-1 font-mono bg-slate-100 px-2 py-0.5 rounded inline-block">
                                    Balance: {entry.running_balance}
                                  </div>
                                </div>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                </div>
              </div>

            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
