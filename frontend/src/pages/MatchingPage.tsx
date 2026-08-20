// @ts-nocheck
import { useMatchExceptions, useRunMatchingPipeline } from "@/api/matching"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { PlayCircle, AlertTriangle, AlertCircle, CheckCircle2 } from "lucide-react"

export function MatchingPage() {
  const { data: exceptions, isLoading, refetch } = useMatchExceptions()
  const runPipeline = useRunMatchingPipeline()

  const handleRunPipeline = async () => {
    await runPipeline.mutateAsync()
    refetch()
  }

  // Aggregate exceptions
  const highSeverity = exceptions?.filter(e => e.severity === 'HIGH') || []
  const mediumSeverity = exceptions?.filter(e => e.severity === 'MEDIUM') || []

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Reconciliation</h1>
          <p className="text-slate-500">Automatically match and clear orders, invoices, and payments.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button 
            className="gap-2 bg-indigo-600 hover:bg-indigo-700" 
            onClick={handleRunPipeline}
            disabled={runPipeline.isPending}
          >
            {runPipeline.isPending ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
            ) : (
              <PlayCircle className="h-4 w-4" />
            )}
            Run Auto-Match
          </Button>
        </div>
      </div>

      {isLoading ? (
        <Card className="border-slate-200 h-48 animate-pulse bg-slate-50/50" />
      ) : exceptions?.length === 0 ? (
        <Card className="border-emerald-200 shadow-sm bg-emerald-50/50">
          <CardContent className="pt-6 flex flex-col items-center justify-center py-12 text-center">
            <div className="h-16 w-16 bg-emerald-100 rounded-full flex items-center justify-center mb-4">
              <CheckCircle2 className="h-8 w-8 text-emerald-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900">All Reconciled</h3>
            <p className="text-slate-500 mt-2 max-w-sm">
              All sales orders have been successfully matched with their corresponding payments and invoices. No outstanding exceptions.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {highSeverity.length > 0 && (
            <Card className="border-red-200 shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-red-500" />
              <CardHeader className="bg-red-50/50 border-b border-red-100 pb-4">
                <CardTitle className="flex items-center gap-2 text-red-900">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  High Priority Issues
                </CardTitle>
                <CardDescription className="text-red-700/80">
                  {highSeverity.length} orders require immediate attention
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div className="divide-y divide-red-100">
                  {highSeverity.slice(0, 5).map(exc => (
                    <div key={exc.id} className="p-4 flex items-start justify-between hover:bg-red-50/30">
                      <div>
                        <p className="text-sm font-medium text-slate-900">{exc.description}</p>
                        <p className="text-xs text-slate-500 mt-1 flex items-center gap-2">
                          <span className="capitalize">{exc.exception_type.replace(/_/g, ' ').toLowerCase()}</span>
                        </p>
                      </div>
                      <Button variant="outline" size="sm" className="text-xs shrink-0">Review</Button>
                    </div>
                  ))}
                  {highSeverity.length > 5 && (
                    <div className="p-4 text-center text-sm text-slate-500 bg-slate-50/50">
                      + {highSeverity.length - 5} more issues
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {mediumSeverity.length > 0 && (
            <Card className="border-amber-200 shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-amber-500" />
              <CardHeader className="bg-amber-50/50 border-b border-amber-100 pb-4">
                <CardTitle className="flex items-center gap-2 text-amber-900">
                  <AlertCircle className="h-5 w-5 text-amber-600" />
                  Review Needed
                </CardTitle>
                <CardDescription className="text-amber-700/80">
                  {mediumSeverity.length} partial matches found
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div className="divide-y divide-amber-100">
                  {mediumSeverity.slice(0, 5).map(exc => (
                    <div key={exc.id} className="p-4 flex items-start justify-between hover:bg-amber-50/30">
                      <div>
                        <p className="text-sm font-medium text-slate-900">{exc.description}</p>
                        <p className="text-xs text-slate-500 mt-1 flex items-center gap-2">
                          <span className="capitalize">{exc.exception_type.replace(/_/g, ' ').toLowerCase()}</span>
                        </p>
                      </div>
                      <Button variant="outline" size="sm" className="text-xs shrink-0">Review</Button>
                    </div>
                  ))}
                  {mediumSeverity.length > 5 && (
                    <div className="p-4 text-center text-sm text-slate-500 bg-slate-50/50">
                      + {mediumSeverity.length - 5} more issues
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
