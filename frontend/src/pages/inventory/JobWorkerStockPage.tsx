import { useState, useMemo, Fragment } from "react"
import { useAllPendingStock, useAllJobWorkerActivities } from "@/api/job-works"
import { useSKUs } from "@/api/masters"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Search, MapPin, Undo2, Factory, ScrollText, BookOpen } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { formatQuantityValue } from "@/lib/utils"
import { JobWorkReturnDialog } from "@/components/suppliers/JobWorkReturnDialog"
import { JobWorkerWorkspace } from "@/components/suppliers/JobWorkerWorkspace"
import { useAuth } from "@/hooks/use-auth"

export function JobWorkerStockPage() {
  const { hasPermission } = useAuth()
  const { data: stockData, isLoading } = useAllPendingStock()
  const { data: activities, isLoading: isLoadingActivities } = useAllJobWorkerActivities()
  const { data: skus } = useSKUs()
  
  const [searchQuery, setSearchQuery] = useState("")
  
  // Modals state
  const [returnDialogState, setReturnDialogState] = useState<{open: boolean, supplierId: string, supplierName: string, skuId?: string}>({ open: false, supplierId: "", supplierName: "" })
  const [workspaceDialogState, setWorkspaceDialogState] = useState<{open: boolean, supplierId: string, supplierName: string, initialTab?: string}>({ open: false, supplierId: "", supplierName: "" })
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({})

  const toggleRow = (id: string) => {
    setExpandedRows(prev => ({
      ...prev,
      [id]: !prev[id]
    }))
  }

  const filteredItems = useMemo(() => {
    const items = (stockData as any)?.items || (stockData as any)?.data?.items
    if (!items) return []
    if (!searchQuery) return items
    
    const query = searchQuery.toLowerCase()
    return items.filter((item: any) => 
      item?.job_worker_name?.toLowerCase().includes(query) ||
      item?.item_name?.toLowerCase().includes(query) ||
      item?.item_code?.toLowerCase().includes(query)
    )
  }, [stockData, searchQuery])

  const formatActivityType = (type: string) => {
    switch (type) {
      case "JOB_WORK_ISSUE": return <Badge variant="outline" className="bg-blue-50 text-blue-700">Issue</Badge>
      case "JOB_WORK_RETURN": return <Badge variant="outline" className="bg-orange-50 text-orange-700">Return</Badge>
      case "RAW_MATERIAL_CONSUMPTION": return <Badge variant="outline" className="bg-purple-50 text-purple-700">Consumption</Badge>
      case "JOB_WORK_RECEIPT": return <Badge variant="outline" className="bg-green-50 text-green-700">Receipt</Badge>
      default: return <Badge variant="outline">{type}</Badge>
    }
  }

  const formatQuantity = (qty: number, sku?: any) => {
    const sign = qty > 0 ? "+" : ""
    return `${sign}${formatQuantityValue(qty, sku?.uom?.unit_type)} ${sku?.uom?.unit_code || ""}`
  }

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-slate-500">Loading pending stock...</div>
      </div>
    )
  }

  const kpis = (stockData as any)?.kpis || (stockData as any)?.data?.kpis

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Job Worker Stock</h1>
          <p className="text-sm text-slate-500 mt-1">Operational view of inventory currently pending with job workers.</p>
        </div>
      </div>

      {kpis && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Card className="border-slate-200 shadow-sm">
            <CardContent className="p-6 flex items-center">
              <div className="rounded-md bg-indigo-50 p-3">
                <Factory className="h-5 w-5 text-indigo-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-500">Job Workers with Stock</p>
                <h3 className="text-2xl font-bold text-slate-900">{kpis.job_workers_with_stock}</h3>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-slate-200 shadow-sm">
            <CardContent className="p-6 flex items-center">
              <div className="rounded-md bg-emerald-50 p-3">
                <MapPin className="h-5 w-5 text-emerald-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-500">Items with Pending Stock</p>
                <h3 className="text-2xl font-bold text-slate-900">{kpis.items_with_pending_stock}</h3>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200 shadow-sm">
            <CardContent className="p-6 flex items-center">
              <div className="rounded-md bg-amber-50 p-3">
                <ScrollText className="h-5 w-5 text-amber-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-slate-500">Total Pending Lines</p>
                <h3 className="text-2xl font-bold text-slate-900">{kpis.total_pending_lines}</h3>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Card className="border-slate-200 shadow-sm overflow-hidden">
        <div className="border-b border-slate-200 bg-slate-50/50 p-4">
          <div className="relative max-w-sm">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
            <Input
              type="search"
              placeholder="Search job worker or item..."
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-medium">
              <tr>
                <th className="px-4 py-3">Job Worker</th>
                <th className="px-4 py-3">Item</th>
                <th className="px-4 py-3 text-right">UOM</th>
                <th className="px-4 py-3 text-right">Issued</th>
                <th className="px-4 py-3 text-right">Consumed</th>
                <th className="px-4 py-3 text-right">Returned</th>
                <th className="px-4 py-3 text-right text-indigo-700 font-bold bg-indigo-50/30">Pending</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredItems.map((item, idx) => {
                const rowId = `${item.job_worker_id}-${item.item_id}-${idx}`
                const isExpanded = !!expandedRows[rowId]
                return (
                  <Fragment key={rowId}>
                    <tr className="hover:bg-slate-50 transition-colors">
                      <td className="px-4 py-3 font-medium text-slate-900">
                        <button 
                          onClick={() => setWorkspaceDialogState({ open: true, supplierId: item.job_worker_id, supplierName: item.job_worker_name })}
                          className="text-indigo-600 hover:text-indigo-800 hover:underline cursor-pointer"
                        >
                          {item.job_worker_name}
                        </button>
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-medium text-slate-900">{item.item_name}</div>
                        <div className="text-xs text-slate-500">{item.item_code}</div>
                      </td>
                      <td className="px-4 py-3 text-right text-slate-500">{item.uom}</td>
                      <td className="px-4 py-3 text-right text-slate-600">{formatQuantityValue(item.issued_quantity)}</td>
                      <td className="px-4 py-3 text-right text-slate-600">{formatQuantityValue(item.consumed_quantity)}</td>
                      <td className="px-4 py-3 text-right text-slate-600">{formatQuantityValue(item.returned_quantity)}</td>
                      <td className="px-4 py-3 text-right text-indigo-700 font-bold bg-indigo-50/30 text-base">
                        {formatQuantityValue(item.pending_quantity)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => toggleRow(rowId)}
                            className="h-8"
                          >
                            {isExpanded ? "Hide History" : "History"}
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => setWorkspaceDialogState({ 
                              open: true, 
                              supplierId: item.job_worker_id, 
                              supplierName: item.job_worker_name,
                              initialTab: "ledger"
                            })}
                            className="h-8 text-indigo-600 border-indigo-200 hover:bg-indigo-50"
                          >
                            <BookOpen className="h-3.5 w-3.5 mr-1" />
                            Ledger
                          </Button>
                          {hasPermission("INVENTORY_JOBWORK_MANAGE") && (
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => setReturnDialogState({ 
                                open: true, 
                                supplierId: item.job_worker_id, 
                                supplierName: item.job_worker_name,
                                skuId: item.item_id
                              })}
                              className="h-8"
                            >
                              <Undo2 className="h-3.5 w-3.5 mr-1" />
                              Return
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                    {isExpanded && item.issues && item.issues.length > 0 && (
                      <tr className="bg-slate-50/50">
                        <td colSpan={8} className="p-4 border-b border-slate-200">
                          <div className="bg-white rounded-md border border-slate-200 p-4 shadow-sm">
                            <h4 className="font-semibold text-slate-900 mb-3 text-sm flex items-center">
                              <ScrollText className="h-4 w-4 mr-2 text-slate-500" />
                              Issue History & Pending Allocation
                            </h4>
                            <div className="overflow-x-auto">
                              <table className="w-full text-left text-xs whitespace-nowrap">
                                <thead className="bg-slate-50 text-slate-500">
                                  <tr>
                                    <th className="px-3 py-2 font-medium">Issue Ref</th>
                                    <th className="px-3 py-2 font-medium">Date</th>
                                    <th className="px-3 py-2 text-right font-medium">Issued</th>
                                    <th className="px-3 py-2 text-right font-medium">Consumed</th>
                                    <th className="px-3 py-2 text-right font-medium">Returned</th>
                                    <th className="px-3 py-2 text-right text-indigo-700 font-medium">Pending</th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                  {item.issues.map((issue: any) => (
                                    <tr key={issue.id} className="hover:bg-slate-50/50">
                                      <td className="px-3 py-2 font-medium text-slate-700">{issue.issue_reference}</td>
                                      <td className="px-3 py-2 text-slate-500">
                                        {new Date(issue.created_on).toLocaleDateString("en-GB")}
                                      </td>
                                      <td className="px-3 py-2 text-right">{formatQuantityValue(issue.issued_quantity)}</td>
                                      <td className="px-3 py-2 text-right">{formatQuantityValue(issue.consumed_quantity)}</td>
                                      <td className="px-3 py-2 text-right">{formatQuantityValue(issue.returned_quantity)}</td>
                                      <td className="px-3 py-2 text-right font-semibold text-indigo-700 bg-indigo-50/20">{formatQuantityValue(issue.pending_quantity)}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                )
              })}
              {filteredItems.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-slate-500">
                    No pending stock found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <Card className="border-slate-200 shadow-sm overflow-hidden">
        <div className="border-b border-slate-200 bg-slate-50/50 p-4">
          <h3 className="font-semibold text-slate-900">Recent Job Work Activity</h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-medium">
              <tr>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Item</th>
                <th className="px-4 py-3 text-right">Quantity</th>
                <th className="px-4 py-3">Reference</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoadingActivities ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                    Loading activities...
                  </td>
                </tr>
              ) : !(activities as unknown as any[]) || (activities as unknown as any[]).length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                    No recent activity found.
                  </td>
                </tr>
              ) : (
                (activities as unknown as any[]).map((act: any) => {
                  const sku = skus?.find((s: any) => s.id === act.sku_id)
                  return (
                    <tr key={act.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-4 py-3">
                        {new Date(act.movement_date || act.created_on || new Date()).toLocaleDateString("en-GB", {
                          day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit"
                        })}
                      </td>
                      <td className="px-4 py-3">{formatActivityType(act.movement_type)}</td>
                      <td className="px-4 py-3 font-medium text-slate-900">{sku?.product?.product_name || sku?.item_code || act.sku_id}</td>
                      <td className={`px-4 py-3 text-right font-medium ${act.quantity > 0 ? "text-green-600" : "text-red-600"}`}>
                        {formatQuantity(act.quantity, sku)}
                      </td>
                      <td className="px-4 py-3 text-slate-500">{act.reference_number}</td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Action Dialogs */}
      {returnDialogState.open && (
        <JobWorkReturnDialog 
          open={returnDialogState.open} 
          onOpenChange={(open) => setReturnDialogState(prev => ({ ...prev, open }))}
          supplierId={returnDialogState.supplierId}
          supplierName={returnDialogState.supplierName}
          defaultSkuId={returnDialogState.skuId}
        />
      )}
      
      {workspaceDialogState.open && (
        <JobWorkerWorkspace
          supplierId={workspaceDialogState.supplierId}
          supplierName={workspaceDialogState.supplierName}
          supplierCode=""
          open={workspaceDialogState.open}
          onOpenChange={(open) => setWorkspaceDialogState(prev => ({ ...prev, open }))}
          initialTab={workspaceDialogState.initialTab}
        />
      )}
    </div>
  )
}
