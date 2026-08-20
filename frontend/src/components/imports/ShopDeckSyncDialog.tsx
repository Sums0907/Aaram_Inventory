// @ts-nocheck
import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { useSyncShopDeck } from "@/api/imports"
import { Loader2, Download, CheckCircle2, AlertCircle } from "lucide-react"

interface ShopDeckSyncDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const syncSchema = z.object({
  report_type: z.string().optional(),
  period_start: z.string().min(1, "Start date is required"),
  period_end: z.string().min(1, "End date is required")
})

type SyncFormValues = z.infer<typeof syncSchema>

export function ShopDeckSyncDialog({ open, onOpenChange }: ShopDeckSyncDialogProps) {
  const syncMutation = useSyncShopDeck()
  const [syncResponse, setSyncResponse] = useState<any | null>(null)

  const form = useForm<SyncFormValues>({
    resolver: zodResolver(syncSchema),
    defaultValues: {
      report_type: "",
      period_start: new Date(new Date().setDate(new Date().getDate() - 7)).toISOString().split("T")[0],
      period_end: new Date().toISOString().split("T")[0]
    }
  })

  // Reset state when dialog closes
  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setTimeout(() => {
        setSyncResponse(null)
        form.reset()
      }, 200)
    }
    onOpenChange(newOpen)
  }

  const onSubmit = async (data: SyncFormValues) => {
    try {
      const payload: any = {
        integration_id: "SHOPDECK",
        period_start: data.period_start,
        period_end: data.period_end
      }
      if (data.report_type) {
        payload.report_type = data.report_type
      }

      const response = await syncMutation.mutateAsync(payload)
      setSyncResponse(response || { status: "FAILED", reason: "Unknown error occurred" })
    } catch (err) {
      console.error("Failed to sync shopdeck:", err)
    }
  }

  const handleDownload = async (filename: string) => {
    try {
      // Import the token directly from client (assuming it is exported)
      // Since it's not exported, we can just use apiClient to fetch the blob.
      const { apiClient } = await import('@/api/client');
      const response = await apiClient.get(`/shopdeck/reports/${filename}/download`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response as any]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to download file:", err);
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        {syncResponse ? (
          syncResponse.status === "FAILED" ? (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2 text-rose-600">
                  <AlertCircle className="h-5 w-5" /> Sync Failed
                </DialogTitle>
                <DialogDescription className="text-rose-600">
                  {syncResponse.reason || "An unknown error occurred during sync."}
                </DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <p className="text-sm text-slate-500">
                  Please ensure your ShopDeck credentials (like session cookies) are correctly configured in your environment.
                </p>
              </div>
              <DialogFooter>
                <Button onClick={() => handleOpenChange(false)}>Close</Button>
              </DialogFooter>
            </>
          ) : (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2 text-emerald-600">
                  <CheckCircle2 className="h-5 w-5" /> Sync Completed
                </DialogTitle>
                <DialogDescription>
                  The ShopDeck connector has successfully downloaded the requested reports.
                </DialogDescription>
              </DialogHeader>
              <div className="py-4 space-y-4">
                {!syncResponse.files_processed || syncResponse.files_processed.length === 0 ? (
                  <p className="text-sm text-slate-500">No new files were downloaded.</p>
                ) : (
                  syncResponse.files_processed.map((file: any, idx: number) => (
                    <div key={idx} className="flex flex-col gap-2 p-3 bg-slate-50 rounded-lg border border-slate-200">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-700 truncate max-w-[250px]" title={file.filename}>
                        {file.filename}
                      </span>
                      <span className="text-xs px-2 py-1 bg-slate-200 text-slate-600 rounded-full font-medium">
                        {file.status}
                      </span>
                    </div>
                    {file.status === "IMPORTED" || file.status === "DUPLICATE" ? (
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full mt-2 gap-2 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 border-indigo-200"
                        onClick={() => handleDownload(file.filename)}
                      >
                        <Download className="h-4 w-4" /> Download CSV
                      </Button>
                    ) : null}
                  </div>
                  ))
                )}
              </div>
              <DialogFooter>
                <Button onClick={() => handleOpenChange(false)}>Close</Button>
              </DialogFooter>
            </>
          )
        ) : (
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <DialogHeader>
              <DialogTitle>Sync ShopDeck Reports</DialogTitle>
              <DialogDescription>
                Download custom reports directly from ShopDeck for processing.
              </DialogDescription>
            </DialogHeader>
            
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <label htmlFor="report_type" className="text-sm font-medium">Report Type</label>
                <select
                  id="report_type"
                  className="flex h-10 w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  {...form.register("report_type")}
                >
                  <option value="">All Reports</option>
                  <option value="ORDER_RECONCILIATION">Order Reconciliation Report</option>
                  <option value="TAX_READY">Tax Ready Report</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <label htmlFor="period_start" className="text-sm font-medium">Start Date</label>
                  <input
                    id="period_start"
                    type="date"
                    className="flex h-10 w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    {...form.register("period_start")}
                  />
                  {form.formState.errors.period_start && (
                    <span className="text-xs text-rose-500">{form.formState.errors.period_start.message}</span>
                  )}
                </div>

                <div className="grid gap-2">
                  <label htmlFor="period_end" className="text-sm font-medium">End Date</label>
                  <input
                    id="period_end"
                    type="date"
                    className="flex h-10 w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    {...form.register("period_end")}
                  />
                  {form.formState.errors.period_end && (
                    <span className="text-xs text-rose-500">{form.formState.errors.period_end.message}</span>
                  )}
                </div>
              </div>
            </div>
            
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => handleOpenChange(false)} disabled={syncMutation.isPending}>
                Cancel
              </Button>
              <Button type="submit" disabled={syncMutation.isPending} className="bg-indigo-600 hover:bg-indigo-700">
                {syncMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Sync Reports
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}
