import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { ShieldCheck } from "lucide-react"

export function ConfidencePage() {
  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Inventory Confidence</h1>
        <p className="text-slate-500">System-wide monitoring of data integrity and reliability.</p>
      </div>

      <Card className="border-slate-200 shadow-sm h-[600px] flex flex-col">
        <CardHeader className="bg-slate-50/50 border-b flex-shrink-0">
          <CardTitle className="text-lg">Trust Metrics</CardTitle>
          <CardDescription>Understand exactly why the engine trusts or distrusts certain stock levels</CardDescription>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center text-slate-400">
          <ShieldCheck className="h-12 w-12 text-slate-300 mb-4" />
          <h3 className="text-lg font-medium text-slate-900">Confidence Command Center Coming Soon</h3>
          <p className="text-sm text-center max-w-sm mt-2">
            This dashboard will aggregate positive and negative signals across the entire warehouse to give you a clear picture of systemic health.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
