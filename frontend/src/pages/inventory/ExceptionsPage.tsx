// @ts-nocheck
import { formatQuantityValue } from "@/lib/utils"
import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { exceptionsApi } from "@/api/exceptions"
import { AlertTriangle, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { format } from "date-fns"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet"
import { Textarea } from "@/components/ui/textarea"
import { useAuth } from "@/hooks/use-auth"

export function ExceptionsPage() {
  const { hasPermission } = useAuth()
  const queryClient = useQueryClient()
  const [selectedException, setSelectedException] = useState<any>(null)
  const [resolutionNotes, setResolutionNotes] = useState("")

  const { data, isLoading } = useQuery({
    queryKey: ['inventory-exceptions'],
    queryFn: () => exceptionsApi.getExceptions()
  })

  const resolveMutation = useMutation({
    mutationFn: (id: string) => exceptionsApi.resolveException(id, { resolution_notes: resolutionNotes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory-exceptions'] })
      setSelectedException(null)
      setResolutionNotes("")
    }
  })

  const handleResolve = () => {
    if (selectedException) {
      resolveMutation.mutate(selectedException.id)
    }
  }

  const exceptions = data?.items || []

  return (
    <div className="h-full flex flex-col space-y-6 max-w-7xl mx-auto w-full pb-8 px-4 md:px-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Inventory Exceptions</h1>
        <p className="text-sm text-slate-500">Manage anomalies and discrepancies across the system.</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex-1 flex flex-col">
        {isLoading ? (
          <div className="p-8 text-center text-slate-500">Loading exceptions...</div>
        ) : exceptions.length === 0 ? (
          <div className="p-8 text-center text-slate-500">
            <CheckCircle2 className="h-12 w-12 text-emerald-500 mx-auto mb-3" />
            <div className="text-lg font-medium text-slate-900">All Clear!</div>
            <p>No open exceptions to review.</p>
          </div>
        ) : (
          <div className="overflow-auto flex-1">
            <table className="w-full text-sm text-left whitespace-nowrap">
              <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 sticky top-0 z-10">
                <tr>
                  <th className="px-6 py-3 font-medium">Issue</th>
                  <th className="px-6 py-3 font-medium">Date</th>
                  <th className="px-6 py-3 font-medium">Item</th>
                  <th className="px-6 py-3 font-medium">Source</th>
                  <th className="px-6 py-3 font-medium text-right">Variance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {exceptions.map(exc => (
                  <tr 
                    key={exc.id} 
                    className="hover:bg-slate-50 cursor-pointer"
                    onClick={() => setSelectedException(exc)}
                  >
                    <td className="px-6 py-4 font-medium text-slate-900">{exc.resolution_notes || 'Discrepancy reported'}</td>
                    <td className="px-6 py-4 text-slate-600">{format(new Date(exc.exception_date), "MMM d, yyyy")}</td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-900">{exc.inventory_item.name}</div>
                      <div className="text-xs text-slate-500">{exc.inventory_item.inventory_code}</div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200">
                        {exc.source_system}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="text-rose-600 font-mono font-medium">{exc.difference > 0 ? '+' : ''}{exc.difference}</div>
                      <div className="text-xs text-slate-400">Sys: {formatQuantityValue(exc.expected_quantity)} → Act: {formatQuantityValue(exc.actual_quantity)}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Sheet open={!!selectedException} onOpenChange={(o) => !o && setSelectedException(null)}>
        <SheetContent className="sm:max-w-md">
          <SheetHeader>
            <SheetTitle>Resolve Exception</SheetTitle>
            <SheetDescription>
              Review the variance and log your resolution.
            </SheetDescription>
          </SheetHeader>
          
          {selectedException && (
            <div className="mt-6 space-y-6">
              <div className="bg-rose-50 border border-rose-200 p-4 rounded-lg flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-rose-600 mt-0.5" />
                <div>
                  <div className="font-medium text-rose-900">Quantity Variance</div>
                  <div className="text-sm text-rose-700 mt-1">
                    System expected {formatQuantityValue(selectedException.expected_quantity)} but found {formatQuantityValue(selectedException.actual_quantity)} (Difference: {formatQuantityValue(selectedException.difference)}).
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-slate-500 mb-1">Item</h3>
                <div className="text-lg font-semibold text-slate-900">{selectedException.inventory_item.name}</div>
                <div className="text-sm text-slate-500 font-mono">{selectedException.inventory_item.inventory_code}</div>
              </div>
              
              {hasPermission("INVENTORY_EXCEPTION_RESOLVE") ? (
                <>
                  <div>
                    <h3 className="text-sm font-medium text-slate-500 mb-1">Resolution Notes</h3>
                    <Textarea 
                      placeholder="Explain how this variance was investigated and resolved..."
                      value={resolutionNotes}
                      onChange={(e) => setResolutionNotes(e.target.value)}
                      className="min-h-[120px]"
                    />
                  </div>

                  <div className="pt-4 flex gap-3">
                    <Button 
                      onClick={handleResolve} 
                      disabled={resolveMutation.isPending || !resolutionNotes.trim()}
                      className="w-full bg-indigo-600 hover:bg-indigo-700"
                    >
                      {resolveMutation.isPending ? "Resolving..." : "Mark as Resolved"}
                    </Button>
                  </div>
                </>
              ) : (
                <div className="pt-4 text-sm text-slate-500 italic">
                  You do not have permission to resolve exceptions.
                </div>
              )}
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  )
}
