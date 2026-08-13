import { useState } from "react"
import { useJobWorkerRates } from "@/api/job-worker-accounting"
import { useSuppliers } from "@/api/suppliers"
import { useSKUs } from "@/api/masters"
import { JobWorkRateFormDialog } from "@/components/job-worker-accounting/JobWorkRateFormDialog"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, Plus, Calendar } from "lucide-react"

export function JobWorkRatesPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const { data: rates, isLoading: isLoadingRates } = useJobWorkerRates()
  const { data: suppliers } = useSuppliers()
  const { data: skus } = useSKUs()

  const getSupplierName = (id: string) => suppliers?.data?.find(s => s.id === id)?.name || id
  const getSKUName = (id: string) => {
    const sku = skus?.find(s => s.id === id)
    return sku ? (sku.product?.product_name || sku.item_code) : id
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2
    }).format(value)
  }

  const formatDate = (dateString: string) => {
    const d = new Date(dateString)
    return new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(d)
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Job Work Rates</h1>
          <p className="text-slate-500">Manage labour charges per piece for Job Workers.</p>
        </div>
        <Button onClick={() => setIsDialogOpen(true)} className="gap-2 bg-indigo-600 hover:bg-indigo-700">
          <Plus className="h-4 w-4" />
          Add Rate
        </Button>
      </div>

      <Card className="border-slate-200 shadow-sm">
        <CardHeader className="bg-slate-50/50 border-b">
          <CardTitle>Rate Master</CardTitle>
          <CardDescription>
            Configured rates are used to automatically calculate Job Work Expenses when Goods Receipts are posted.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {isLoadingRates ? (
            <div className="flex items-center justify-center p-12 text-slate-500">
              <Loader2 className="h-6 w-6 animate-spin mr-2" />
              Loading Job Worker Accounting...
            </div>
          ) : !rates || rates.length === 0 ? (
            <div className="text-center p-12">
              <div className="mx-auto w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                <Calendar className="h-6 w-6 text-slate-400" />
              </div>
              <h3 className="text-lg font-medium text-slate-900 mb-1">No Job Work rates configured yet</h3>
              <p className="text-slate-500 mb-4">You need to set up rates before posting Job Work Receipts.</p>
              <Button onClick={() => setIsDialogOpen(true)} variant="outline">
                + Add Rate
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-50 text-slate-500 border-b">
                  <tr>
                    <th className="px-6 py-3 font-medium">Job Worker</th>
                    <th className="px-6 py-3 font-medium">Job Worked Product</th>
                    <th className="px-6 py-3 font-medium text-right">Rate</th>
                    <th className="px-6 py-3 font-medium text-center">Basis</th>
                    <th className="px-6 py-3 font-medium text-center">Effective From</th>
                    <th className="px-6 py-3 font-medium text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {rates.map(rate => (
                    <tr key={rate.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-3 font-medium text-slate-900">{getSupplierName(rate.job_worker_id)}</td>
                      <td className="px-6 py-3 text-slate-600">{getSKUName(rate.sku_id)}</td>
                      <td className="px-6 py-3 text-right font-mono text-slate-900">{formatCurrency(rate.rate)}</td>
                      <td className="px-6 py-3 text-center text-slate-500">
                        {rate.rate_basis === 'PER_PIECE' ? 'Per Piece' : rate.rate_basis}
                      </td>
                      <td className="px-6 py-3 text-center text-slate-500">{formatDate(rate.effective_from)}</td>
                      <td className="px-6 py-3 text-center">
                        {rate.is_active ? (
                          <span className="inline-flex items-center rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">
                            Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center rounded-full bg-slate-50 px-2 py-1 text-xs font-medium text-slate-600 ring-1 ring-inset ring-slate-500/10">
                            Archived
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <JobWorkRateFormDialog 
        open={isDialogOpen} 
        onOpenChange={setIsDialogOpen} 
        suppliers={suppliers?.data || []}
        skus={skus || []}
      />
    </div>
  )
}
