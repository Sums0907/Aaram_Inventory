// @ts-nocheck
import { useDashboardSummary } from "@/api/dashboard"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { 
  IndianRupee, 
  Activity,
  CreditCard,
  CheckCircle2,
  Package,
  TrendingUp,
  RefreshCcw
} from "lucide-react"
import { Button } from "@/components/ui/button"

export function DashboardPage() {
  const { data: summary, isLoading, isError, refetch, isFetching } = useDashboardSummary()

  const formatCurrency = (value: number | undefined) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value || 0)
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Business Health</h1>
          <p className="text-slate-500">Live aggregated metrics from all connected sales channels.</p>
        </div>
        <Button 
          onClick={() => refetch()} 
          disabled={isFetching}
          className="gap-2 bg-indigo-600 hover:bg-indigo-700 w-full md:w-auto"
        >
          <RefreshCcw className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
          Sync Latest Data
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map(i => (
            <Card key={i} className="border-slate-200">
              <CardContent className="p-6">
                <div className="h-4 w-24 bg-slate-100 animate-pulse rounded mb-4"></div>
                <div className="h-8 w-32 bg-slate-100 animate-pulse rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : isError ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-600">
          Failed to load business data. Please check connection.
        </div>
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Revenue Card */}
            <Card className="border-slate-200 shadow-sm relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0 relative">
                <CardTitle className="text-sm font-medium text-slate-500">
                  Total Gross Revenue
                </CardTitle>
                <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                  <IndianRupee className="h-4 w-4" />
                </div>
              </CardHeader>
              <CardContent className="relative">
                <div className="text-3xl font-bold text-slate-900 tracking-tight">
                  {formatCurrency(summary?.["Total Revenue"])}
                </div>
                <p className="text-xs text-emerald-600 mt-2 flex items-center gap-1 font-medium">
                  <TrendingUp className="h-3 w-3" />
                  +12% from last month
                </p>
              </CardContent>
            </Card>

            {/* Settlements Card */}
            <Card className="border-slate-200 shadow-sm relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0 relative">
                <CardTitle className="text-sm font-medium text-slate-500">
                  Net Settlements (Bank)
                </CardTitle>
                <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg">
                  <CreditCard className="h-4 w-4" />
                </div>
              </CardHeader>
              <CardContent className="relative">
                <div className="text-3xl font-bold text-slate-900 tracking-tight">
                  {formatCurrency(summary?.["Total Settlements"])}
                </div>
                <p className="text-xs text-slate-500 mt-2 flex items-center gap-1">
                  Platform Fees: {formatCurrency(summary?.["Platform Fees"])}
                </p>
              </CardContent>
            </Card>

            {/* Fulfillment Card */}
            <Card className="border-slate-200 shadow-sm relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0 relative">
                <CardTitle className="text-sm font-medium text-slate-500">
                  Fulfillment Rate
                </CardTitle>
                <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                  <Package className="h-4 w-4" />
                </div>
              </CardHeader>
              <CardContent className="relative">
                <div className="text-3xl font-bold text-slate-900 tracking-tight">
                  {summary?.["Fulfillment Rate"]}%
                </div>
                <p className="text-xs text-slate-500 mt-2 flex items-center gap-1">
                  {summary?.["Tax Invoices"]} / {summary?.["Sales Orders"]} Orders fulfilled
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="bg-slate-50/50 border-b">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Activity className="h-5 w-5 text-indigo-500" />
                  System Health
                </CardTitle>
                <CardDescription>Automated reconciliation and sync status.</CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-slate-900">Data Integrity Check</h4>
                      <p className="text-sm text-slate-500">Automated verification of ledger balances</p>
                    </div>
                    {summary?.["Golden Dataset Status"] === 'PASS' ? (
                      <div className="flex items-center gap-2 text-emerald-600 font-medium bg-emerald-50 px-3 py-1 rounded-full text-sm">
                        <CheckCircle2 className="h-4 w-4" />
                        Verified
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 text-amber-600 font-medium bg-amber-50 px-3 py-1 rounded-full text-sm">
                        Pending
                      </div>
                    )}
                  </div>
                  
                  <div className="h-px bg-slate-100" />
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-slate-900">Active Integrations</h4>
                      <p className="text-sm text-slate-500">Connections to sales channels</p>
                    </div>
                    <div className="flex items-center gap-2 text-slate-700 font-medium">
                      2 Platforms
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
