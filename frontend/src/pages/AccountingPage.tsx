import { useJournals } from "@/api/accounting"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { BookOpen, Download, Building, Landmark, Wallet, TrendingUp } from "lucide-react"

export function AccountingPage() {
  const { data: journals, isLoading } = useJournals()

  // Aggregate balances from journal lines for a business-level view
  const ledgerBalances: Record<string, number> = {}

  journals?.forEach(journal => {
    journal.lines.forEach(line => {
      if (!ledgerBalances[line.ledger_name]) {
        ledgerBalances[line.ledger_name] = 0
      }
      ledgerBalances[line.ledger_name] += (line.debit - line.credit)
    })
  })

  const cashInBank = (ledgerBalances['HDFC Current Account'] || 0) + (ledgerBalances['Cash'] || 0)
  const accountsReceivable = ledgerBalances['Shopdeck Receivable'] || 0
  const grossSales = Math.abs(ledgerBalances['Sales'] || 0)
  const platformFees = (ledgerBalances['Shopdeck Fees'] || 0) + (ledgerBalances['Razorpay Fees'] || 0)

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value)
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Financial State</h1>
          <p className="text-slate-500">Live ledger balances automatically generated from operations.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button className="gap-2 bg-indigo-600 hover:bg-indigo-700 w-full md:w-auto">
            <Download className="h-4 w-4" />
            Generate Monthly Export
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map(i => (
            <Card key={i} className="border-slate-200 h-32 animate-pulse bg-slate-50/50" />
          ))}
        </div>
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card className="border-slate-200 shadow-sm relative overflow-hidden group">
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                <CardTitle className="text-sm font-medium text-slate-500">Cash in Bank</CardTitle>
                <Landmark className="h-4 w-4 text-emerald-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-900">{formatCurrency(cashInBank)}</div>
                <p className="text-xs text-slate-500 mt-1">Liquid funds available</p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 shadow-sm relative overflow-hidden group">
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                <CardTitle className="text-sm font-medium text-slate-500">Accounts Receivable</CardTitle>
                <Building className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-900">{formatCurrency(accountsReceivable)}</div>
                <p className="text-xs text-slate-500 mt-1">Platform payout holds</p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 shadow-sm relative overflow-hidden group">
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                <CardTitle className="text-sm font-medium text-slate-500">Gross Sales</CardTitle>
                <TrendingUp className="h-4 w-4 text-indigo-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-900">{formatCurrency(grossSales)}</div>
                <p className="text-xs text-slate-500 mt-1">Total revenue generated</p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 shadow-sm relative overflow-hidden group">
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                <CardTitle className="text-sm font-medium text-slate-500">Platform Fees</CardTitle>
                <Wallet className="h-4 w-4 text-red-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-900">{formatCurrency(platformFees)}</div>
                <p className="text-xs text-slate-500 mt-1">Marketplace & gateway costs</p>
              </CardContent>
            </Card>
          </div>

          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="bg-slate-50/50 border-b">
              <CardTitle className="flex items-center gap-2 text-lg">
                <BookOpen className="h-5 w-5 text-indigo-500" />
                Ledger Breakdown
              </CardTitle>
              <CardDescription>
                High-level view of account balances (Technical double-entry details are hidden).
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-slate-100">
                {Object.entries(ledgerBalances)
                  .filter(([_, bal]) => bal !== 0)
                  .map(([name, bal], idx) => (
                  <div key={idx} className="p-4 flex items-center justify-between hover:bg-slate-50/50">
                    <p className="font-medium text-slate-900">{name}</p>
                    <div className="flex items-center gap-4">
                      {bal > 0 ? (
                        <span className="text-emerald-600 font-mono">{formatCurrency(bal)} (Dr)</span>
                      ) : (
                        <span className="text-indigo-600 font-mono">{formatCurrency(Math.abs(bal))} (Cr)</span>
                      )}
                    </div>
                  </div>
                ))}
                {Object.entries(ledgerBalances).filter(([_, bal]) => bal !== 0).length === 0 && (
                  <div className="p-8 text-center text-slate-500">
                    No ledger balances calculated yet. Run the matching and accounting pipeline.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
