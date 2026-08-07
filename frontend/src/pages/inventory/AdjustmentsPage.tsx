import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Settings2 } from "lucide-react"

export function AdjustmentsPage() {
  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Manual Adjustments</h1>
        <p className="text-slate-500">Audit log of all manual corrections and their underlying justifications.</p>
      </div>

      <Card className="border-slate-200 shadow-sm h-[600px] flex flex-col">
        <CardHeader className="bg-slate-50/50 border-b flex-shrink-0">
          <CardTitle className="text-lg">Adjustment History</CardTitle>
          <CardDescription>Track who adjusted what, when, and why</CardDescription>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center text-slate-400">
          <Settings2 className="h-12 w-12 text-slate-300 mb-4" />
          <h3 className="text-lg font-medium text-slate-900">Adjustments Ledger Coming Soon</h3>
          <p className="text-sm text-center max-w-sm mt-2">
            This page provides strict accountability for any inventory change that occurred outside of standard operational events (like purchases or sales).
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
