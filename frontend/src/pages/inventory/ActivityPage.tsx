// @ts-nocheck
import React, { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { format } from "date-fns"
import { 
  ArrowDownToLine, 
  ArrowUpFromLine, 
  RefreshCcw, 
  Settings2, 
  ArrowRightLeft,
  Search,
  Filter,
  Download,
  FileText
} from "lucide-react"

import { inventoryActivitiesApi } from "@/api/activities"
import { cn, formatQuantityValue } from "@/lib/utils"
import type { ActivityResponse } from "@/api/activities"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

function getActivityIcon(type: string) {
  switch (type) {
    case 'PURCHASE_RECEIPT': return <ArrowDownToLine className="h-4 w-4 text-emerald-600" />
    case 'SALES_FULFILLMENT': return <ArrowUpFromLine className="h-4 w-4 text-amber-600" />
    case 'CUSTOMER_RETURN': return <RefreshCcw className="h-4 w-4 text-emerald-600" />
    case 'MANUAL_ADJUSTMENT': return <Settings2 className="h-4 w-4 text-slate-600" />
    case 'STOCK_COUNT_ADJUSTMENT': return <Settings2 className="h-4 w-4 text-slate-600" />
    case 'JOB_WORK_ISSUE': return <ArrowUpFromLine className="h-4 w-4 text-indigo-600" />
    case 'JOB_WORK_RECEIPT': return <ArrowDownToLine className="h-4 w-4 text-indigo-600" />
    default: return <ArrowRightLeft className="h-4 w-4 text-slate-600" />
  }
}

function getActivityColor(qty: number) {
  if (qty > 0) return "text-emerald-700 bg-emerald-50 border-emerald-200"
  if (qty < 0) return "text-rose-700 bg-rose-50 border-rose-200"
  return "text-slate-700 bg-slate-50 border-slate-200"
}

export function ActivityPage() {
  const [search, setSearch] = useState("")
  const [selectedActivity, setSelectedActivity] = useState<ActivityResponse | null>(null)
  
  const [itemType, setItemType] = useState<string>("ALL")
  const [activityType, setActivityType] = useState<string>("ALL")
  const [dateRange, setDateRange] = useState<string>("ALL")

  const { data, isLoading } = useQuery({
    queryKey: ['inventory-activities', itemType, activityType, dateRange],
    queryFn: () => {
      const params: any = { limit: 200 }
      if (itemType !== "ALL") params.item_type = itemType
      if (activityType !== "ALL") params.movement_type = activityType
      
      if (dateRange !== "ALL") {
        const today = new Date();
        if (dateRange === "TODAY") {
          params.date_from = today.toISOString().split('T')[0]
        } else if (dateRange === "LAST_7_DAYS") {
          const pastDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
          params.date_from = pastDate.toISOString().split('T')[0]
        } else if (dateRange === "LAST_30_DAYS") {
          const pastDate = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
          params.date_from = pastDate.toISOString().split('T')[0]
        }
      }
      
      return inventoryActivitiesApi.getActivities(params)
    }
  })

  // Group by date
  const filteredItems = (data?.items || []).filter(act => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (
      act.inventory_item.name.toLowerCase().includes(s) ||
      act.inventory_item.inventory_code.toLowerCase().includes(s) ||
      act.reference.number.toLowerCase().includes(s)
    );
  }) || [];

  const grouped = filteredItems.reduce((acc, act) => {
    const d = act.date
    if (!acc[d]) acc[d] = []
    acc[d].push(act)
    return acc
  }, {} as Record<string, ActivityResponse[]>)

  return (
    <div className="h-full flex flex-col space-y-6 max-w-7xl mx-auto w-full pb-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Inventory Activity</h1>
          <p className="text-sm text-slate-500">Chronological ledger of all inventory activities across the system.</p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" className="gap-2 bg-white">
            <Download className="h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      <div className="flex items-center gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input 
            placeholder="Search activities, items, references..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 bg-slate-50 border-slate-200"
          />
        </div>
        
        <Select value={itemType} onValueChange={setItemType}>
          <SelectTrigger className="w-[180px] bg-white border-slate-200">
            <SelectValue placeholder="Entire Inventory" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">Entire Inventory</SelectItem>
            <SelectItem value="FINISHED_GOODS">Finished Goods</SelectItem>
            <SelectItem value="RAW_MATERIAL">Raw Materials</SelectItem>
            <SelectItem value="PACKAGING">Packaging</SelectItem>
            <SelectItem value="CONSUMABLE">Consumables</SelectItem>
          </SelectContent>
        </Select>

        <Select value={activityType} onValueChange={setActivityType}>
          <SelectTrigger className="w-[180px] bg-white border-slate-200">
            <SelectValue placeholder="All Activities" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All Activities</SelectItem>
            <SelectItem value="PURCHASE_RECEIPT">Goods Received</SelectItem>
            <SelectItem value="SALES_FULFILLMENT">Daily Sales</SelectItem>
            <SelectItem value="CUSTOMER_RETURN">Sales Return</SelectItem>
            <SelectItem value="JOB_WORK_ISSUE">Job Work Issue</SelectItem>
            <SelectItem value="JOB_WORK_RECEIPT">Job Work Receipt</SelectItem>
            <SelectItem value="MANUAL_ADJUSTMENT">Manual Adjustment</SelectItem>
          </SelectContent>
        </Select>

        <Select value={dateRange} onValueChange={setDateRange}>
          <SelectTrigger className="w-[150px] bg-white border-slate-200">
            <SelectValue placeholder="All Time" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All Time</SelectItem>
            <SelectItem value="TODAY">Today</SelectItem>
            <SelectItem value="LAST_7_DAYS">Last 7 Days</SelectItem>
            <SelectItem value="LAST_30_DAYS">Last 30 Days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex-1 flex flex-col">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Loading activities...</div>
        ) : !grouped || Object.keys(grouped).length === 0 ? (
          <div className="p-8 text-center text-slate-500">No activities found.</div>
        ) : (
          <div className="overflow-y-auto flex-1 p-0">
            <table className="w-full text-sm text-left">
              <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 sticky top-0 z-10">
                <tr>
                  <th className="px-6 py-3 font-medium">Activity</th>
                  <th className="px-6 py-3 font-medium">Type</th>
                  <th className="px-6 py-3 font-medium">Inventory Item</th>
                  <th className="px-6 py-3 font-medium text-right">Qty</th>
                  <th className="px-6 py-3 font-medium text-right">Balance</th>
                  <th className="px-6 py-3 font-medium">Reference</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {Object.entries(grouped).sort((a, b) => b[0].localeCompare(a[0])).map(([dateStr, activities]) => (
                  <React.Fragment key={dateStr}>
                    {/* Date Group Header */}
                    <tr className="bg-slate-50/50">
                      <td colSpan={6} className="px-6 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                        {format(new Date(dateStr), "d MMM yyyy")}
                      </td>
                    </tr>
                    
                    {/* Activities */}
                    {activities.map((act) => (
                      <tr 
                        key={act.id} 
                        onClick={() => setSelectedActivity(act)}
                        className="hover:bg-slate-50 cursor-pointer transition-colors group"
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 border border-slate-200 group-hover:bg-white group-hover:border-slate-300 transition-colors">
                              {getActivityIcon(act.activity_type)}
                            </div>
                            <span className="font-medium text-slate-700">{act.activity_name}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-slate-500 capitalize">{act.inventory_item.type.replace('_', ' ').toLowerCase()}</span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-col">
                            <span className="font-medium text-slate-900">{act.inventory_item.name}</span>
                            <span className="text-xs text-slate-500">{act.inventory_item.inventory_code}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <Badge variant="outline" className={cn("px-2 py-0.5 font-mono text-sm", getActivityColor(act.quantity))}>
                            {act.quantity > 0 ? '+' : ''}{formatQuantityValue(act.quantity)}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 text-right font-mono text-slate-600">
                          {act.balance_after_activity !== null ? formatQuantityValue(act.balance_after_activity) : '-'}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2 text-slate-600">
                            <FileText className="h-4 w-4 text-slate-400" />
                            <span className="font-mono text-sm">{act.reference.number}</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Sheet open={!!selectedActivity} onOpenChange={(o) => !o && setSelectedActivity(null)}>
        <SheetContent className="sm:max-w-md">
          <SheetHeader>
            <SheetTitle>Activity Details</SheetTitle>
            <SheetDescription>
              Detailed view of the inventory activity.
            </SheetDescription>
          </SheetHeader>
          
          {selectedActivity && (
            <div className="mt-6 space-y-6">
              <div>
                <h3 className="text-sm font-medium text-slate-500 mb-1">Item</h3>
                <div className="text-lg font-semibold text-slate-900">{selectedActivity.inventory_item.name}</div>
                <div className="text-sm text-slate-500 font-mono">{selectedActivity.inventory_item.inventory_code}</div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 border-y border-slate-100 py-4">
                <div>
                  <h3 className="text-sm font-medium text-slate-500 mb-1">Activity</h3>
                  <div className="flex items-center gap-2 text-slate-900 font-medium">
                    {getActivityIcon(selectedActivity.activity_type)}
                    {selectedActivity.activity_name}
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-slate-500 mb-1">Quantity</h3>
                  <Badge variant="outline" className={cn("font-mono text-sm", getActivityColor(selectedActivity.quantity))}>
                    {selectedActivity.quantity > 0 ? '+' : ''}{formatQuantityValue(selectedActivity.quantity)}
                  </Badge>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-slate-500 mb-1">Source Document</h3>
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-slate-400" />
                  <span className="font-mono text-slate-900">{selectedActivity.reference.number}</span>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-slate-500 mb-1">Date Logged</h3>
                <div className="text-slate-900">{format(new Date(selectedActivity.created_on), "d MMM yyyy, h:mm a")}</div>
              </div>
              
              <div className="pt-6 border-t border-slate-100 flex gap-3">
                <Button className="w-full bg-indigo-600 hover:bg-indigo-700">Open Document</Button>
                <Button variant="outline" className="w-full">View Ledger</Button>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  )
}
