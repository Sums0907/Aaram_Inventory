// @ts-nocheck
import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table"
import { Plus, ArrowLeftRight, BookOpen, ChevronDown, ChevronRight, PackageSearch } from "lucide-react"
import { usePendingStock, useJobWorkerActivities, useCustodyLedger, type CustodyLedgerItem } from "@/api/job-works"
import { useSKUs } from "@/api/masters"
import { JobWorkIssueDialog } from "./JobWorkIssueDialog"
import { JobWorkReturnDialog } from "./JobWorkReturnDialog"
import { formatQuantityValue } from "@/lib/utils"

interface JobWorkerWorkspaceProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  supplierId: string
  supplierName: string
  supplierCode?: string
  initialTab?: string
}

// -----------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------

/** Parse a decimal string from the backend — returns 0 for "—", null, undefined, or NaN */
function safeNum(val: string | null | undefined): number {
  if (!val || val === "—" || val === "-" || val.trim() === "") return 0
  const n = parseFloat(val)
  return isNaN(n) ? 0 : n
}

// -----------------------------------------------------------------------
// Particular badge colours
// -----------------------------------------------------------------------
function ParticularBadge({ text }: { text: string }) {
  if (text === "Material Issued")
    return <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 whitespace-nowrap">{text}</Badge>
  if (text === "Material Consumed")
    return <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200 whitespace-nowrap">{text}</Badge>
  if (text === "Material Returned")
    return <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200 whitespace-nowrap">{text}</Badge>
  return <Badge variant="outline" className="whitespace-nowrap">{text}</Badge>
}

// -----------------------------------------------------------------------
// Reference detail card — shown inline when a reference is clicked
// -----------------------------------------------------------------------
function docTypeLabel(particular: string): string {
  if (particular === "Material Issued")   return "Job Work Issue"
  if (particular === "Material Consumed") return "Goods Receipt Note (GRN)"
  if (particular === "Material Returned") return "Job Work Return"
  return "Transaction"
}

function docTypeColour(particular: string) {
  if (particular === "Material Issued")   return { bg: "bg-blue-50",   border: "border-blue-200",   text: "text-blue-800",   accent: "text-blue-600" }
  if (particular === "Material Consumed") return { bg: "bg-purple-50", border: "border-purple-200", text: "text-purple-800", accent: "text-purple-600" }
  if (particular === "Material Returned") return { bg: "bg-orange-50", border: "border-orange-200", text: "text-orange-800", accent: "text-orange-600" }
  return { bg: "bg-slate-50", border: "border-slate-200", text: "text-slate-800", accent: "text-slate-600" }
}

function descriptionFor(entry: { particular: string; issue: string; consumption: string; return: string; pending: string }, uom: string): string {
  if (entry.particular === "Material Issued")
    return `${safeNum(entry.issue).toFixed(2)} ${uom} was issued from the main warehouse to this Job Worker. Running custody balance after this event: ${safeNum(entry.pending).toFixed(2)} ${uom}.`
  if (entry.particular === "Material Consumed")
    return `${safeNum(entry.consumption).toFixed(2)} ${uom} was consumed to produce finished goods (via the GRN referenced above). Running custody balance after this event: ${safeNum(entry.pending).toFixed(2)} ${uom}.`
  if (entry.particular === "Material Returned")
    return `${safeNum(entry.return).toFixed(2)} ${uom} was returned from the Job Worker back to the main warehouse. Running custody balance after this event: ${safeNum(entry.pending).toFixed(2)} ${uom}.`
  return ""
}

interface ReferenceDetailCardProps {
  entry: { date: string; reference: string; particular: string; issue: string; consumption: string; return: string; pending: string }
  uom: string
  onClose: () => void
}

function ReferenceDetailCard({ entry, uom, onClose }: ReferenceDetailCardProps) {
  const col = docTypeColour(entry.particular)
  const label = docTypeLabel(entry.particular)
  const desc = descriptionFor(entry, uom)
  const dateFormatted = entry.date
    ? new Date(entry.date).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" })
    : "—"

  return (
    <tr>
      <td colSpan={7} className="px-0 py-0">
        <div className={`mx-4 mb-3 rounded-lg border ${col.border} ${col.bg} px-4 py-3 text-xs relative`}>
          <button
            onClick={onClose}
            className="absolute top-2 right-2 text-slate-400 hover:text-slate-600 text-base leading-none font-bold"
            aria-label="Close"
          >×</button>
          <div className={`font-semibold ${col.text} mb-1`}>{label}</div>
          <div className="grid grid-cols-3 gap-x-6 gap-y-1 text-slate-600 mt-1">
            <div><span className="text-slate-400">Document No.</span><br /><span className={`font-mono font-semibold ${col.accent}`}>{entry.reference}</span></div>
            <div><span className="text-slate-400">Date</span><br /><span className="font-medium">{dateFormatted}</span></div>
            <div><span className="text-slate-400">Pending after</span><br /><span className="font-bold text-indigo-700">{safeNum(entry.pending).toFixed(2)} {uom}</span></div>
          </div>
          <p className="mt-2 text-slate-500 leading-relaxed">{desc}</p>
        </div>
      </td>
    </tr>
  )
}

// -----------------------------------------------------------------------
// Custody Ledger — one item section (collapsible)
// -----------------------------------------------------------------------
function LedgerItemSection({ item }: { item: CustodyLedgerItem }) {
  const [open, setOpen] = useState(true)
  const [activeRef, setActiveRef] = useState<number | null>(null)

  // Compute totals from the last entry's running pending
  const lastEntry = item.entries[item.entries.length - 1]
  const totalIssued   = item.entries.reduce((s, e) => s + safeNum(e.issue), 0)
  const totalConsumed = item.entries.reduce((s, e) => s + safeNum(e.consumption), 0)
  const totalReturned = item.entries.reduce((s, e) => s + safeNum(e.return), 0)
  const pendingBalance = lastEntry ? safeNum(lastEntry.pending) : 0

  return (
    <div className="rounded-lg border border-slate-200 overflow-hidden">
      {/* Section header — always visible summary */}
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 hover:bg-slate-100 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          {open ? <ChevronDown className="h-4 w-4 text-slate-400" /> : <ChevronRight className="h-4 w-4 text-slate-400" />}
          <div>
            <span className="font-semibold text-slate-900 text-sm">{item.item_name}</span>
            <span className="ml-2 text-xs text-slate-500">{item.item_code}</span>
          </div>
          <Badge variant="outline" className="text-xs ml-1 text-slate-500">{item.uom}</Badge>
        </div>
        {/* Mini summary pills */}
        <div className="flex items-center gap-3 text-xs">
          <span className="text-blue-600 font-medium">Issued: {totalIssued.toFixed(2)}</span>
          <span className="text-purple-600 font-medium">Consumed: {totalConsumed.toFixed(2)}</span>
          <span className="text-orange-600 font-medium">Returned: {totalReturned.toFixed(2)}</span>
          <span className={`font-bold px-2 py-0.5 rounded ${pendingBalance > 0 ? "bg-indigo-50 text-indigo-700" : "bg-slate-100 text-slate-500"}`}>
            Pending: {pendingBalance.toFixed(2)} {item.uom}
          </span>
        </div>
      </button>

      {/* Detailed ledger table */}
      {open && (
        <div className="overflow-x-auto">
          <table className="w-full text-xs whitespace-nowrap">
            <thead className="bg-white border-b border-slate-100 text-slate-500">
              <tr>
                <th className="px-4 py-2 text-left font-medium">Date</th>
                <th className="px-4 py-2 text-left font-medium">Reference</th>
                <th className="px-4 py-2 text-left font-medium">Particular</th>
                <th className="px-4 py-2 text-right font-medium text-blue-600">Issue</th>
                <th className="px-4 py-2 text-right font-medium text-purple-600">Consumption</th>
                <th className="px-4 py-2 text-right font-medium text-orange-600">Return</th>
                <th className="px-4 py-2 text-right font-bold text-indigo-700 bg-indigo-50/40">Pending</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {item.entries.map((entry, idx) => {
                const issued   = safeNum(entry.issue)
                const consumed = safeNum(entry.consumption)
                const returned = safeNum(entry.return)
                const isActive = activeRef === idx
                return (
                  <>
                    <tr key={idx} className={`transition-colors ${isActive ? "bg-slate-50" : "hover:bg-slate-50/60"}`}>
                      <td className="px-4 py-2 text-slate-500">
                        {entry.date ? new Date(entry.date).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) : "—"}
                      </td>
                      <td className="px-4 py-2">
                        {/* Clickable reference */}
                        <button
                          onClick={() => setActiveRef(isActive ? null : idx)}
                          className={`font-mono underline decoration-dotted underline-offset-2 transition-colors cursor-pointer ${
                            entry.particular === "Material Issued"   ? "text-blue-700 hover:text-blue-900" :
                            entry.particular === "Material Consumed" ? "text-purple-700 hover:text-purple-900" :
                            entry.particular === "Material Returned" ? "text-orange-700 hover:text-orange-900" :
                            "text-slate-700 hover:text-slate-900"
                          }`}
                          title={`Click to see details for ${entry.reference}`}
                        >
                          {entry.reference || "—"}
                        </button>
                      </td>
                      <td className="px-4 py-2"><ParticularBadge text={entry.particular} /></td>
                      <td className="px-4 py-2 text-right text-blue-700 font-medium">
                        {issued > 0 ? issued.toFixed(2) : <span className="text-slate-300">—</span>}
                      </td>
                      <td className="px-4 py-2 text-right text-purple-700 font-medium">
                        {consumed > 0 ? consumed.toFixed(2) : <span className="text-slate-300">—</span>}
                      </td>
                      <td className="px-4 py-2 text-right text-orange-700 font-medium">
                        {returned > 0 ? returned.toFixed(2) : <span className="text-slate-300">—</span>}
                      </td>
                      <td className="px-4 py-2 text-right font-bold text-indigo-700 bg-indigo-50/30">
                        {safeNum(entry.pending).toFixed(2)}
                      </td>
                    </tr>
                    {isActive && (
                      <ReferenceDetailCard
                        key={`detail-${idx}`}
                        entry={entry}
                        uom={item.uom}
                        onClose={() => setActiveRef(null)}
                      />
                    )}
                  </>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

// -----------------------------------------------------------------------
// Stock Custody Ledger tab content
// -----------------------------------------------------------------------
function CustodyLedgerTab({ supplierId }: { supplierId: string }) {
  const { data: ledger, isLoading, isError } = useCustodyLedger(supplierId)

  if (isLoading) {
    return (
      <div className="flex h-48 items-center justify-center">
        <div className="text-slate-400 text-sm animate-pulse">Loading custody ledger…</div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex h-48 items-center justify-center">
        <div className="text-red-500 text-sm">Failed to load custody ledger. Please try again.</div>
      </div>
    )
  }

  if (!ledger || ledger.items.length === 0) {
    return (
      <div className="flex flex-col h-48 items-center justify-center gap-3 text-slate-400">
        <PackageSearch className="h-10 w-10 text-slate-200" />
        <p className="text-sm">No material has been issued to this Job Worker yet.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Header note */}
      <p className="text-xs text-slate-500 border-b border-slate-100 pb-2">
        Showing complete material passbook for <strong>{ledger.supplier_name}</strong>. 
        Each item shows a running balance of Issue → Consumption → Return → Pending.
      </p>
      {ledger.items.map(item => (
        <LedgerItemSection key={item.item_id} item={item} />
      ))}
    </div>
  )
}

// -----------------------------------------------------------------------
// Main component
// -----------------------------------------------------------------------
export function JobWorkerWorkspace({ open, onOpenChange, supplierId, supplierName, supplierCode, initialTab }: JobWorkerWorkspaceProps) {
  const { data: skus } = useSKUs()
  const { data: pendingStock, isLoading: isLoadingStock } = usePendingStock(supplierId)
  const { data: activities, isLoading: isLoadingActivities } = useJobWorkerActivities(supplierId)

  const [issueDialogOpen, setIssueDialogOpen] = useState(false)
  const [returnDialogOpen, setReturnDialogOpen] = useState(false)
  const [activeTab, setActiveTab] = useState(initialTab ?? "pending")

  const formatActivityType = (type: string) => {
    switch (type) {
      case "JOB_WORK_ISSUE":           return <Badge variant="outline" className="bg-blue-50 text-blue-700">Issue</Badge>
      case "JOB_WORK_RETURN":          return <Badge variant="outline" className="bg-orange-50 text-orange-700">Return</Badge>
      case "RAW_MATERIAL_CONSUMPTION": return <Badge variant="outline" className="bg-purple-50 text-purple-700">Consumption</Badge>
      case "JOB_WORK_RECEIPT":         return <Badge variant="outline" className="bg-green-50 text-green-700">Receipt</Badge>
      default:                          return <Badge variant="outline">{type}</Badge>
    }
  }

  const formatQuantity = (qty: number, sku?: any) => {
    const sign = qty > 0 ? "+" : ""
    return `${sign}${formatQuantityValue(qty, sku?.uom?.unit_type)} ${sku?.uom?.unit_code || ""}`
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-5xl max-h-[92vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl">{supplierName}</DialogTitle>
            <DialogDescription>
              {supplierCode ? `Job Worker Code: ${supplierCode}` : "Job Worker Workspace"}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-5 mt-2">
            {/* Quick Actions */}
            <div className="flex gap-3 p-4 bg-slate-50 rounded-lg border border-slate-200">
              <Button onClick={() => setIssueDialogOpen(true)} className="bg-indigo-600 hover:bg-indigo-700">
                <Plus className="mr-2 h-4 w-4" />
                Issue Material
              </Button>
              <Button onClick={() => setReturnDialogOpen(true)} variant="outline">
                <ArrowLeftRight className="mr-2 h-4 w-4" />
                Record Material Return
              </Button>
            </div>

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="border-b border-slate-200 w-full justify-start rounded-none bg-transparent h-auto p-0 gap-0">
                <TabsTrigger 
                  value="pending"
                  className="rounded-none border-b-2 border-transparent data-[state=active]:border-indigo-600 data-[state=active]:text-indigo-700 data-[state=active]:bg-transparent pb-2 px-4 font-medium text-slate-500 hover:text-slate-700 transition-colors"
                >
                  Pending Material
                </TabsTrigger>
                <TabsTrigger 
                  value="activity"
                  className="rounded-none border-b-2 border-transparent data-[state=active]:border-indigo-600 data-[state=active]:text-indigo-700 data-[state=active]:bg-transparent pb-2 px-4 font-medium text-slate-500 hover:text-slate-700 transition-colors"
                >
                  Recent Activity
                </TabsTrigger>
                <TabsTrigger 
                  value="ledger"
                  className="rounded-none border-b-2 border-transparent data-[state=active]:border-indigo-600 data-[state=active]:text-indigo-700 data-[state=active]:bg-transparent pb-2 px-4 font-medium text-slate-500 hover:text-slate-700 transition-colors flex items-center gap-1.5"
                >
                  <BookOpen className="h-3.5 w-3.5" />
                  Stock Custody Ledger
                </TabsTrigger>
              </TabsList>

              {/* ---- Tab: Pending Material ---- */}
              <TabsContent value="pending" className="mt-4">
                <div className="rounded-md border bg-white">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Material</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>UOM</TableHead>
                        <TableHead className="text-right">Issued</TableHead>
                        <TableHead className="text-right">Consumed</TableHead>
                        <TableHead className="text-right">Returned</TableHead>
                        <TableHead className="text-right font-bold text-slate-900">Pending</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {isLoadingStock ? (
                        <TableRow>
                          <TableCell colSpan={7} className="text-center h-24 text-slate-500">
                            Loading pending material…
                          </TableCell>
                        </TableRow>
                      ) : !pendingStock || pendingStock.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={7} className="text-center h-24 text-slate-500">
                            No pending materials found.
                          </TableCell>
                        </TableRow>
                      ) : (
                        pendingStock.map((stock) => {
                          const sku = skus?.find(s => s.id === stock.item_id)
                          return (
                            <TableRow key={stock.item_id}>
                              <TableCell className="font-medium">{sku?.product?.product_name || sku?.item_code || stock.item_id}</TableCell>
                              <TableCell>{sku?.product?.item_type || "—"}</TableCell>
                              <TableCell>{sku?.uom?.unit_code || "—"}</TableCell>
                              <TableCell className="text-right">{formatQuantityValue(stock.issued_quantity, sku?.uom?.unit_type)}</TableCell>
                              <TableCell className="text-right text-purple-600">{formatQuantityValue(stock.consumed_quantity, sku?.uom?.unit_type)}</TableCell>
                              <TableCell className="text-right text-orange-600">{formatQuantityValue(stock.returned_quantity, sku?.uom?.unit_type)}</TableCell>
                              <TableCell className="text-right font-bold text-indigo-700">{formatQuantityValue(stock.pending_quantity, sku?.uom?.unit_type)}</TableCell>
                            </TableRow>
                          )
                        })
                      )}
                    </TableBody>
                  </Table>
                </div>
              </TabsContent>

              {/* ---- Tab: Recent Activity ---- */}
              <TabsContent value="activity" className="mt-4">
                <div className="rounded-md border bg-white">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Date</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Item</TableHead>
                        <TableHead className="text-right">Quantity</TableHead>
                        <TableHead>Reference</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {isLoadingActivities ? (
                        <TableRow>
                          <TableCell colSpan={5} className="text-center h-24 text-slate-500">
                            Loading activities…
                          </TableCell>
                        </TableRow>
                      ) : !activities || activities.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={5} className="text-center h-24 text-slate-500">
                            No recent activity found.
                          </TableCell>
                        </TableRow>
                      ) : (
                        activities.map((act) => {
                          const sku = skus?.find(s => s.id === act.sku_id)
                          return (
                            <TableRow key={act.id}>
                              <TableCell>
                                {new Date(act.movement_date || act.created_on || new Date()).toLocaleDateString("en-GB", {
                                  day: "numeric", month: "short", year: "numeric"
                                })}
                              </TableCell>
                              <TableCell>{formatActivityType(act.movement_type)}</TableCell>
                              <TableCell>{sku?.product?.product_name || sku?.item_code || act.sku_id}</TableCell>
                              <TableCell className={`text-right font-medium ${act.quantity > 0 ? "text-green-600" : "text-red-600"}`}>
                                {formatQuantity(act.quantity, sku)}
                              </TableCell>
                              <TableCell className="text-slate-500">{act.reference_number}</TableCell>
                            </TableRow>
                          )
                        })
                      )}
                    </TableBody>
                  </Table>
                </div>
              </TabsContent>

              {/* ---- Tab: Stock Custody Ledger ---- */}
              <TabsContent value="ledger" className="mt-4">
                <CustodyLedgerTab supplierId={supplierId} />
              </TabsContent>
            </Tabs>
          </div>
        </DialogContent>
      </Dialog>

      <JobWorkIssueDialog 
        open={issueDialogOpen} 
        onOpenChange={setIssueDialogOpen} 
        supplierId={supplierId}
        supplierName={supplierName}
      />

      <JobWorkReturnDialog 
        open={returnDialogOpen} 
        onOpenChange={setReturnDialogOpen} 
        supplierId={supplierId}
        supplierName={supplierName}
      />
    </>
  )
}
