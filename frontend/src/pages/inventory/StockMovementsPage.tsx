import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { ArrowRightLeft } from "lucide-react"

export function StockMovementsPage() {
  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Stock Movements</h1>
        <p className="text-slate-500">The master ledger of all physical inventory transactions across all warehouses.</p>
      </div>

      <Card className="border-slate-200 shadow-sm h-[600px] flex flex-col">
        <CardHeader className="bg-slate-50/50 border-b flex-shrink-0">
          <CardTitle className="text-lg">Transaction History</CardTitle>
          <CardDescription>View, filter, and export the official record of inventory changes</CardDescription>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center text-slate-400">
          <ArrowRightLeft className="h-12 w-12 text-slate-300 mb-4" />
          <h3 className="text-lg font-medium text-slate-900">Movement Ledger Coming Soon</h3>
          <p className="text-sm text-center max-w-sm mt-2">
            This workspace will allow you to track every purchase receipt, customer return, and manual adjustment chronologically.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
