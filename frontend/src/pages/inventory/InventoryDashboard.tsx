import { useState } from "react"
import { useInventoryBalances, useDashboardKPIs, useDashboardExceptions, type InventoryBalanceResponse } from "@/api/inventory"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Package, AlertTriangle, ShieldCheck, Activity, Search, ListFilter } from "lucide-react"
import { LedgerDashboardDialog } from "@/components/inventory/LedgerDashboardDialog"

export function InventoryPage() {
  const { data: balances, isLoading: isBalancesLoading } = useInventoryBalances()
  const { data: kpis, isLoading: isKpisLoading } = useDashboardKPIs()
  const { data: exceptions, isLoading: isExceptionsLoading } = useDashboardExceptions()
  
  const [selectedSku, setSelectedSku] = useState<InventoryBalanceResponse | null>(null)
  const [searchQuery, setSearchQuery] = useState("")

  const isLoading = isBalancesLoading || isKpisLoading || isExceptionsLoading

  // Compute Total Current Stock (Sum of all balances)
  const totalStock = balances?.reduce((acc: number, curr: InventoryBalanceResponse) => acc + curr.balance, 0) || 0

  // Filter balances based on search
  const filteredBalances = balances?.filter(b => 
    b.sku_name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    b.sku_code.toLowerCase().includes(searchQuery.toLowerCase())
  ) || []

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Inventory Intelligence</h1>
          <p className="text-slate-500">Operational command center for physical inventory tracking.</p>
        </div>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => (
            <Card key={i} className="border-slate-200 h-32 animate-pulse bg-slate-50/50" />
          ))}
        </div>
      ) : (
        <>
          {/* Operational KPIs */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-500 flex items-center justify-between">
                  Tracked SKUs
                  <Package className="h-4 w-4 text-slate-400" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold tracking-tight text-slate-900">
                  {kpis?.total_skus_tracked || 0}
                </div>
                <p className="text-xs text-slate-500 mt-1">Total physical items mapped</p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-500 flex items-center justify-between">
                  Current Stock
                  <Activity className="h-4 w-4 text-emerald-500" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold tracking-tight text-emerald-600">
                  {new Intl.NumberFormat('en-IN').format(totalStock)}
                </div>
                <p className="text-xs text-slate-500 mt-1">Total projected units</p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-500 flex items-center justify-between">
                  Average Confidence
                  <ShieldCheck className="h-4 w-4 text-indigo-500" />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold tracking-tight text-indigo-600">
                  {kpis?.average_confidence_score || 0}%
                </div>
                <p className="text-xs text-slate-500 mt-1">System-wide data integrity</p>
              </CardContent>
            </Card>

            <Card className={`border-slate-200 shadow-sm relative overflow-hidden ${(kpis?.total_negative_inventory || 0) > 0 ? 'bg-red-50/30 border-red-200' : ''}`}>
              {(kpis?.total_negative_inventory || 0) > 0 && (
                <div className="absolute top-0 left-0 w-1 h-full bg-red-500" />
              )}
              <CardHeader className="pb-2">
                <CardTitle className={`text-sm font-medium flex items-center justify-between ${(kpis?.total_negative_inventory || 0) > 0 ? 'text-red-900' : 'text-slate-500'}`}>
                  Negative Stock
                  <AlertTriangle className={`h-4 w-4 ${(kpis?.total_negative_inventory || 0) > 0 ? 'text-red-500' : 'text-slate-400'}`} />
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-3xl font-bold tracking-tight ${(kpis?.total_negative_inventory || 0) > 0 ? 'text-red-700' : 'text-slate-900'}`}>
                  {kpis?.total_negative_inventory || 0}
                </div>
                <p className={`text-xs mt-1 ${(kpis?.total_negative_inventory || 0) > 0 ? 'text-red-600' : 'text-slate-500'}`}>SKUs with unviable balances</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            
            {/* Exceptions Workbench */}
            <Card className="border-slate-200 shadow-sm lg:col-span-1 flex flex-col h-[500px]">
              <CardHeader className="bg-slate-50/50 border-b flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-lg text-slate-900">Exceptions Workbench</CardTitle>
                    <CardDescription>Actionable inventory discrepancies</CardDescription>
                  </div>
                  <Badge variant="secondary" className="bg-red-100 text-red-700 hover:bg-red-100">
                    {exceptions?.length || 0} Open
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="p-0 overflow-y-auto flex-1 bg-slate-50/20">
                {exceptions && exceptions.length > 0 ? (
                  <div className="divide-y divide-slate-100">
                    {exceptions.map((exc: any, idx: number) => (
                      <div key={idx} className="p-4 bg-white hover:bg-slate-50 transition-colors">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4 text-red-500" />
                            <span className="font-semibold text-sm text-slate-900">{exc.resolution_notes || 'Negative Inventory'}</span>
                          </div>
                          <span className="text-xs text-slate-500 font-mono">{exc.exception_number}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm mt-3">
                          <div className="flex flex-col">
                            <span className="text-slate-500 text-xs">Projected</span>
                            <span className="font-semibold text-red-600">{exc.actual_quantity} units</span>
                          </div>
                          <div className="flex flex-col text-right">
                            <span className="text-slate-500 text-xs">Action Required</span>
                            <span className="text-blue-600 font-medium cursor-pointer hover:underline">Resolve issue</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-slate-400 space-y-3">
                    <ShieldCheck className="h-10 w-10 text-emerald-400" />
                    <p className="text-sm">No open exceptions</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* SKU Directory */}
            <Card className="border-slate-200 shadow-sm lg:col-span-2 flex flex-col h-[500px]">
              <CardHeader className="bg-slate-50/50 border-b flex-shrink-0 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-lg">SKU Directory</CardTitle>
                    <CardDescription>Search and explore individual stock ledger timelines</CardDescription>
                  </div>
                </div>
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
                  <input 
                    type="text" 
                    placeholder="Search by SKU Name or Code..." 
                    className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
              </CardHeader>
              <CardContent className="p-0 overflow-y-auto flex-1">
                <div className="divide-y divide-slate-100">
                  {filteredBalances.map((item, idx) => (
                    <div 
                      key={idx} 
                      className="p-4 flex flex-col sm:flex-row sm:items-center justify-between hover:bg-indigo-50/30 cursor-pointer transition-colors group"
                      onClick={() => setSelectedSku(item)}
                    >
                      <div className="mb-3 sm:mb-0">
                        <p className="font-medium text-slate-900 group-hover:text-indigo-700 transition-colors">{item.sku_name}</p>
                        <p className="text-sm text-slate-500 font-mono mt-0.5">{item.sku_code}</p>
                      </div>
                      <div className="flex items-center justify-between sm:justify-end gap-6">
                        <div className="flex flex-col items-end">
                          <span className="text-xs text-slate-500 mb-1">Stock</span>
                          <span className={`font-bold text-lg ${item.balance < 0 ? 'text-red-600' : 'text-slate-900'}`}>
                            {item.balance}
                          </span>
                        </div>
                        <div className="flex flex-col items-end w-24">
                          <span className="text-xs text-slate-500 mb-1">Confidence</span>
                          <Badge variant="outline" className={item.confidence_score >= 90 ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : item.confidence_score >= 70 ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-red-50 text-red-700 border-red-200'}>
                            {item.confidence_score}%
                          </Badge>
                        </div>
                        <Button variant="ghost" size="icon" className="hidden sm:inline-flex opacity-0 group-hover:opacity-100 transition-opacity">
                          <ListFilter className="h-4 w-4 text-indigo-600" />
                        </Button>
                      </div>
                    </div>
                  ))}
                  
                  {filteredBalances.length === 0 && (
                    <div className="p-8 text-center text-slate-500">
                      No SKUs match your search query.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}

      {selectedSku && (
        <LedgerDashboardDialog
          isOpen={true}
          onClose={() => setSelectedSku(null)}
          skuId={selectedSku.sku_id}
          skuCode={selectedSku.sku_code}
          skuName={selectedSku.sku_name}
        />
      )}
    </div>
  )
}
