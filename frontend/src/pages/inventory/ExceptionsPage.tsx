import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { AlertTriangle } from "lucide-react"

export function ExceptionsPage() {
  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Exceptions Workbench</h1>
        <p className="text-slate-500">Triage and resolve mathematically impossible or suspect inventory states.</p>
      </div>

      <Card className="border-slate-200 shadow-sm h-[600px] flex flex-col">
        <CardHeader className="bg-slate-50/50 border-b flex-shrink-0">
          <CardTitle className="text-lg">Actionable Exceptions</CardTitle>
          <CardDescription>Review anomalies like negative stock and missing records</CardDescription>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center text-slate-400">
          <AlertTriangle className="h-12 w-12 text-slate-300 mb-4" />
          <h3 className="text-lg font-medium text-slate-900">Expanded Workbench Coming Soon</h3>
          <p className="text-sm text-center max-w-sm mt-2">
            This full-page workbench will provide detailed resolution workflows for each exception, rather than just the dashboard overview.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
