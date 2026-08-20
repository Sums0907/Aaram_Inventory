// @ts-nocheck
import { useJobWorkerAccountingDashboard } from "@/api/job-worker-accounting"
import { useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Users, Banknote, IndianRupee, TrendingDown, Loader2 } from "lucide-react"

export function JobWorkerAccountingDashboard() {
  const { data: dashboard, isLoading } = useJobWorkerAccountingDashboard()
  const navigate = useNavigate()

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value)
  }

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center text-slate-500">
        <Loader2 className="h-8 w-8 animate-spin mr-2" />
        Loading Dashboard...
      </div>
    )
  }

  const hasData = dashboard && dashboard.job_workers.length > 0

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Job Worker Accounting</h1>
        <p className="text-slate-500">Overview of labour expenses, payments, and outstanding balances.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-200 shadow-sm relative overflow-hidden group">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Job Work Expense</CardTitle>
            <Banknote className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">{formatCurrency(dashboard?.total_job_work_expenses || 0)}</div>
            <p className="text-xs text-slate-500 mt-1">Total labour cost incurred</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm relative overflow-hidden group">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Total Paid</CardTitle>
            <IndianRupee className="h-4 w-4 text-emerald-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">{formatCurrency(dashboard?.total_paid || 0)}</div>
            <p className="text-xs text-slate-500 mt-1">Amount settled</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm relative overflow-hidden group">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Outstanding</CardTitle>
            <TrendingDown className="h-4 w-4 text-indigo-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-indigo-600">{formatCurrency(dashboard?.total_outstanding || 0)}</div>
            <p className="text-xs text-slate-500 mt-1">Total payable</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm relative overflow-hidden group">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-slate-500 uppercase tracking-wider">Workers Owed</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">{dashboard?.job_workers_with_outstanding || 0}</div>
            <p className="text-xs text-slate-500 mt-1">With active balance</p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-200 shadow-sm">
        <CardHeader className="bg-slate-50/50 border-b">
          <CardTitle>Job Worker Payables Summary</CardTitle>
          <CardDescription>
            List of all active Job Workers and their financial standing. Click a row to view the detailed ledger or record a payment.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {!hasData ? (
            <div className="p-12 text-center text-slate-500">
              <div className="mx-auto w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-slate-400" />
              </div>
              <p>No Job Workers found or no expenses recorded yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-50 text-slate-500 border-b">
                  <tr>
                    <th className="px-6 py-4 font-medium">Job Worker</th>
                    <th className="px-6 py-4 font-medium text-right">Job Work Expense</th>
                    <th className="px-6 py-4 font-medium text-right">Paid</th>
                    <th className="px-6 py-4 font-medium text-right">Outstanding</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {dashboard.job_workers.map((worker) => (
                    <tr 
                      key={worker.job_worker_id} 
                      className="hover:bg-slate-50/80 transition-colors cursor-pointer group"
                      onClick={() => navigate(`/accounting/job-worker/payables?workerId=${worker.job_worker_id}`)}
                    >
                      <td className="px-6 py-4 font-medium text-slate-900 group-hover:text-indigo-600 transition-colors">
                        {worker.job_worker_name}
                      </td>
                      <td className="px-6 py-4 text-right font-mono text-slate-600">
                        {formatCurrency(worker.total_expenses)}
                      </td>
                      <td className="px-6 py-4 text-right font-mono text-emerald-600">
                        {formatCurrency(worker.total_paid)}
                      </td>
                      <td className="px-6 py-4 text-right font-mono font-bold text-slate-900">
                        {formatCurrency(worker.outstanding)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
