import { useInventoryBalances } from "@/api/inventory"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Package, Download, AlertTriangle, ArrowRightCircle } from "lucide-react"

export function InventoryPage() {
  const { data: balances, isLoading } = useInventoryBalances()

  // Business state derived from data
  const outOfStock = balances?.filter(b => b.balance <= 0) || []
  const lowStock = balances?.filter(b => b.balance > 0 && b.balance <= 10) || []
  const healthy = balances?.filter(b => b.balance > 10) || []

  const totalValueApproximation = (balances?.reduce((acc, curr) => acc + curr.balance, 0) || 0) * 1500 // Dummy value for UI demo

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Inventory Health</h1>
          <p className="text-slate-500">Live view of product availability across all fulfillment centers.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="gap-2 w-full md:w-auto">
            <Download className="h-4 w-4" />
            Download Stock Report
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-3">
          {[1, 2, 3].map(i => (
            <Card key={i} className="border-slate-200 h-32 animate-pulse bg-slate-50/50" />
          ))}
        </div>
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-3">
            {/* Out of stock */}
            <Card className="border-red-200 shadow-sm relative overflow-hidden bg-red-50/30">
              <div className="absolute top-0 left-0 w-1 h-full bg-red-500" />
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-red-900 flex items-center justify-between">
                  Out of Stock
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-700 tracking-tight">
                  {outOfStock.length}
                </div>
                <p className="text-xs text-red-600 mt-1">SKUs losing potential sales</p>
              </CardContent>
            </Card>

            {/* Low stock */}
            <Card className="border-amber-200 shadow-sm relative overflow-hidden bg-amber-50/30">
              <div className="absolute top-0 left-0 w-1 h-full bg-amber-500" />
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-amber-900 flex items-center justify-between">
                  Low Stock
                  <ArrowRightCircle className="h-4 w-4 text-amber-500" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-amber-700 tracking-tight">
                  {lowStock.length}
                </div>
                <p className="text-xs text-amber-600 mt-1">SKUs requiring reorder</p>
              </CardContent>
            </Card>

            {/* Healthy stock */}
            <Card className="border-emerald-200 shadow-sm relative overflow-hidden bg-emerald-50/30">
              <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500" />
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-emerald-900 flex items-center justify-between">
                  Healthy
                  <Package className="h-4 w-4 text-emerald-500" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-emerald-700 tracking-tight">
                  {healthy.length}
                </div>
                <p className="text-xs text-emerald-600 mt-1">
                  Est. Value: {new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(totalValueApproximation)}
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {outOfStock.length > 0 && (
              <Card className="border-slate-200 shadow-sm">
                <CardHeader className="bg-slate-50/50 border-b">
                  <CardTitle className="text-lg">Critical Reorders</CardTitle>
                  <CardDescription>Zero balance items across all warehouses</CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="divide-y divide-slate-100">
                    {outOfStock.map((item, idx) => (
                      <div key={idx} className="p-4 flex items-center justify-between hover:bg-slate-50/50">
                        <div>
                          <p className="font-medium text-slate-900">{item.sku_name}</p>
                          <p className="text-sm text-slate-500 font-mono mt-0.5">{item.sku_code}</p>
                        </div>
                        <Button variant="outline" size="sm" className="shrink-0 text-xs text-slate-600">
                          Create PO
                        </Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {lowStock.length > 0 && (
              <Card className="border-slate-200 shadow-sm">
                <CardHeader className="bg-slate-50/50 border-b">
                  <CardTitle className="text-lg">Approaching Zero</CardTitle>
                  <CardDescription>Items with 10 or fewer units remaining</CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="divide-y divide-slate-100">
                    {lowStock.map((item, idx) => (
                      <div key={idx} className="p-4 flex items-center justify-between hover:bg-slate-50/50">
                        <div>
                          <p className="font-medium text-slate-900">{item.sku_name}</p>
                          <p className="text-sm text-slate-500 font-mono mt-0.5">{item.sku_code}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="font-bold text-amber-600">{item.balance} left</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </>
      )}
    </div>
  )
}
