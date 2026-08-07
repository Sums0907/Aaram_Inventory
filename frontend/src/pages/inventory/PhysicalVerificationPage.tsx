import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { ClipboardCheck } from "lucide-react"

export function PhysicalVerificationPage() {
  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Physical Verification</h1>
        <p className="text-slate-500">Manage cycle counts and full warehouse stock takes.</p>
      </div>

      <Card className="border-slate-200 shadow-sm h-[600px] flex flex-col">
        <CardHeader className="bg-slate-50/50 border-b flex-shrink-0">
          <CardTitle className="text-lg">Stock Counts</CardTitle>
          <CardDescription>Reconcile physical inventory against systemic truth</CardDescription>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center text-slate-400">
          <ClipboardCheck className="h-12 w-12 text-slate-300 mb-4" />
          <h3 className="text-lg font-medium text-slate-900">Verification Workspace Coming Soon</h3>
          <p className="text-sm text-center max-w-sm mt-2">
            This module will allow you to generate count sheets, enter physical quantities, and automatically generate discrepancy adjustments.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
