import { useState, Fragment } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"
import { useJobWorkerPayableLedger } from "@/api/job-worker-accounting"
import { useSuppliers } from "@/api/suppliers"
import { useSKUs } from "@/api/masters"
import { RecordJobWorkerPaymentDialog } from "@/components/job-worker-accounting/RecordJobWorkerPaymentDialog"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Loader2, ArrowLeft, Download, Wallet } from "lucide-react"

// -----------------------------------------------------------------------
// Inline Detail Card
// -----------------------------------------------------------------------
function PayableDetailCard({ entry, skus, onClose }: { entry: any; skus: any[]; onClose: () => void }) {
  const isGRN = entry.particular.includes("GRN") || entry.reference?.startsWith("GRN")
  const isPayment = entry.particular.includes("Payment") || entry.reference?.startsWith("PAY")
  const meta = entry.metadata || {}
  
  const col = isGRN 
    ? { bg: "bg-purple-50", border: "border-purple-200", text: "text-purple-800", accent: "text-purple-600" }
    : isPayment
    ? { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-800", accent: "text-emerald-600" }
    : { bg: "bg-slate-50", border: "border-slate-200", text: "text-slate-800", accent: "text-slate-600" }

  const label = isGRN ? "Goods Receipt Note (GRN)" : isPayment ? "Payment Recorded" : "Ledger Entry"
  
  const formatCurrency = (val: number) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val)
  const dateFormatted = entry.date ? new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'long', year: 'numeric' }).format(new Date(entry.date)) : "—"

  let desc = ""
  if (isGRN) {
    const sku = skus.find(s => s.id === meta.sku_id)
    const skuName = sku?.product?.product_name || sku?.item_code || "Unknown Item"
    desc = `Received ${meta.quantity || 0} ${sku?.uom?.unit_code || 'pcs'} of ${skuName} at a rate of ${formatCurrency(meta.rate || 0)} ${meta.rate_basis === 'PER_PIECE' ? 'per piece' : 'per unit'}. Total Job Work Expense: ${formatCurrency(entry.expense)}. Outstanding payable balance after this expense is ${formatCurrency(entry.outstanding)}.`
  } else if (isPayment) {
    const accountStr = meta.payment_account ? ` via ${meta.payment_account.replace('_', ' ')}` : ""
    const refStr = meta.payment_reference ? ` (Ref: ${meta.payment_reference})` : ""
    const notesStr = meta.notes ? ` Notes: ${meta.notes}` : ""
    desc = `A payment of ${formatCurrency(entry.payment)} was recorded${accountStr}${refStr}.${notesStr} The outstanding payable balance after this payment is ${formatCurrency(entry.outstanding)}.`
  }

  return (
    <tr>
      <td colSpan={5} className="px-0 py-0">
        <div className={`mx-4 mb-3 mt-1 rounded-lg border ${col.border} ${col.bg} px-4 py-3 text-xs relative shadow-sm`}>
          <button onClick={onClose} className="absolute top-2 right-2 text-slate-400 hover:text-slate-600 text-base leading-none font-bold" aria-label="Close">×</button>
          <div className={`font-semibold ${col.text} mb-1`}>{label}</div>
          <div className="grid grid-cols-3 gap-x-6 gap-y-1 text-slate-600 mt-1">
            <div><span className="text-slate-400">Document No.</span><br /><span className={`font-mono font-semibold ${col.accent}`}>{entry.reference}</span></div>
            <div><span className="text-slate-400">Date</span><br /><span className="font-medium">{dateFormatted}</span></div>
            <div><span className="text-slate-400">Balance after</span><br /><span className="font-bold text-indigo-700">{formatCurrency(entry.outstanding)}</span></div>
          </div>
          <p className="mt-2 text-slate-700 leading-relaxed font-medium">{desc}</p>
        </div>
      </td>
    </tr>
  )
}

export function JobWorkerPayablesWorkspace() {
  const [searchParams] = useSearchParams()
  const workerId = searchParams.get("workerId")
  const navigate = useNavigate()
  
  const [isPaymentDialogOpen, setIsPaymentDialogOpen] = useState(false)
  const [activeRef, setActiveRef] = useState<number | null>(null)
  const { data: ledger, isLoading } = useJobWorkerPayableLedger(workerId || undefined)
  const { data: skusData } = useSKUs()
  const skus = skusData || []

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value)
  }

  const formatDate = (dateString: string) => {
    const d = new Date(dateString)
    return new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(d)
  }

  const { data: suppliersData } = useSuppliers()
  const jobWorkers = suppliersData?.data.filter(s => s.is_job_worker) || []

  if (!workerId) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] space-y-6 animate-in fade-in">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-semibold tracking-tight">Job Worker Payables</h2>
          <p className="text-slate-500 max-w-sm">
            Select a Job Worker to view their ledger statement and record payments.
          </p>
        </div>
        
        <div className="w-full max-w-sm space-y-4">
          <select 
            className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            onChange={(e) => {
              if (e.target.value) {
                navigate(`/accounting/job-worker/payables?workerId=${e.target.value}`)
              }
            }}
            defaultValue=""
          >
            <option value="" disabled>Select Job Worker...</option>
            {jobWorkers.map(worker => (
              <option key={worker.id} value={worker.id}>{worker.name}</option>
            ))}
          </select>

          <Button onClick={() => navigate("/accounting/job-worker/dashboard")} variant="outline" className="w-full">
            Return to Dashboard
          </Button>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center text-slate-500">
        <Loader2 className="h-8 w-8 animate-spin mr-2" />
        Loading Payables Workspace...
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <div className="flex items-center gap-4 mb-2">
        <Button 
          variant="ghost" 
          size="icon"
          onClick={() => navigate("/accounting/job-worker/dashboard")}
          className="text-slate-500 hover:text-slate-900"
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">{ledger?.job_worker_name || "Job Worker"}</h1>
          <p className="text-slate-500">Payables Workspace & Ledger Statement</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="border-slate-200 shadow-sm relative overflow-hidden">
          <CardHeader className="pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-slate-500">Total Expense</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">{formatCurrency(ledger?.total_expenses || 0)}</div>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm relative overflow-hidden">
          <CardHeader className="pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-slate-500">Total Paid</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-600">{formatCurrency(ledger?.total_paid || 0)}</div>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm relative overflow-hidden bg-indigo-50/50">
          <CardHeader className="pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-indigo-700">Outstanding</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-indigo-700">{formatCurrency(ledger?.outstanding || 0)}</div>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-200 shadow-sm">
        <CardHeader className="bg-slate-50/50 border-b flex flex-row items-center justify-between">
          <div>
            <CardTitle>Account Statement</CardTitle>
            <CardDescription>
              Chronological ledger of Job Work expenses and payments.
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-2" onClick={() => window.print()}>
              <Download className="h-4 w-4" />
              Download PDF
            </Button>
            <Button 
              size="sm" 
              className="gap-2 bg-indigo-600 hover:bg-indigo-700"
              onClick={() => setIsPaymentDialogOpen(true)}
              disabled={!ledger || ledger.outstanding <= 0}
            >
              <Wallet className="h-4 w-4" />
              Record Payment
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {!ledger || ledger.entries.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              No ledger entries found for this Job Worker.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-50 text-slate-500 border-b">
                  <tr>
                    <th className="px-6 py-3 font-medium">Date</th>
                    <th className="px-6 py-3 font-medium">Particular</th>
                    <th className="px-6 py-3 font-medium text-right">Expense</th>
                    <th className="px-6 py-3 font-medium text-right">Payment</th>
                    <th className="px-6 py-3 font-medium text-right">Balance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  <tr className="bg-slate-50/30">
                    <td className="px-6 py-3 text-slate-500" colSpan={4}>Opening Balance</td>
                    <td className="px-6 py-3 text-right font-mono font-medium text-slate-900">₹0</td>
                  </tr>
                  {ledger.entries.map((entry, idx) => (
                    <Fragment key={idx}>
                      <tr className={`hover:bg-slate-50/80 transition-colors group ${activeRef === idx ? 'bg-slate-50 border-b-0' : ''}`}>
                        <td className="px-6 py-4 text-slate-500 whitespace-nowrap">
                          {formatDate(entry.date)}
                          <div className="text-[10px] mt-1">
                            {entry.reference !== "Opening Balance" && entry.reference !== "Closing Balance" ? (
                              <button 
                                onClick={() => setActiveRef(activeRef === idx ? null : idx)} 
                                className="text-indigo-600 hover:text-indigo-800 hover:underline cursor-pointer focus:outline-none"
                              >
                                {entry.reference}
                              </button>
                            ) : (
                              <span className="text-slate-400">{entry.reference}</span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`font-medium ${entry.expense !== null ? 'text-slate-900' : 'text-emerald-700'}`}>
                            {entry.particular.includes("GRN") || entry.particular.includes("PAY") ? (
                              <button 
                                onClick={() => setActiveRef(activeRef === idx ? null : idx)} 
                                className="hover:text-indigo-600 hover:underline cursor-pointer focus:outline-none text-left"
                              >
                                {entry.particular}
                              </button>
                            ) : (
                              entry.particular
                            )}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right font-mono text-slate-900">
                          {entry.expense !== null ? formatCurrency(entry.expense) : "—"}
                        </td>
                        <td className="px-6 py-4 text-right font-mono text-emerald-600">
                          {entry.payment !== null ? formatCurrency(entry.payment) : "—"}
                        </td>
                        <td className="px-6 py-4 text-right font-mono font-bold text-slate-900">
                          {formatCurrency(entry.outstanding)}
                        </td>
                      </tr>
                      {activeRef === idx && (
                        <PayableDetailCard entry={entry} skus={skus} onClose={() => setActiveRef(null)} />
                      )}
                    </Fragment>
                  ))}
                  <tr className="bg-slate-50/50 border-t-2 border-slate-200">
                    <td className="px-6 py-4 font-medium text-slate-900" colSpan={4}>Closing Balance</td>
                    <td className="px-6 py-4 text-right font-mono font-bold text-indigo-700 text-base">
                      {formatCurrency(ledger.outstanding)}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {ledger && (
        <RecordJobWorkerPaymentDialog
          open={isPaymentDialogOpen}
          onOpenChange={setIsPaymentDialogOpen}
          jobWorkerId={ledger.job_worker_id}
          jobWorkerName={ledger.job_worker_name}
          currentOutstanding={ledger.outstanding}
        />
      )}
    </div>
  )
}
