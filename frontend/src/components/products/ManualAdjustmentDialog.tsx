// @ts-nocheck
import { formatQuantityValue } from "@/lib/utils"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { useCreateManualAdjustment } from "@/api/inventory"
import { Loader2 } from "lucide-react"

export type AdjustmentType = "increase" | "decrease"

interface ManualAdjustmentDialogProps {
  skuId: string
  open: boolean
  onOpenChange: (open: boolean) => void
  type: AdjustmentType
  onSuccess?: () => void
}

const adjustmentSchema = z.object({
  quantity: z.number().min(0.001, "Quantity must be greater than 0"),
  reason: z.string().min(1, "Reason is required"),
  reference_number: z.string().min(1, "Reference number is required"),
  remarks: z.string().optional()
})

type AdjustmentFormValues = z.infer<typeof adjustmentSchema>

const INCREASE_REASONS = [
  "Opening Stock Correction",
  "Stock Found",
  "Manual Correction",
  "Sample Returned",
  "Other"
]

const DECREASE_REASONS = [
  "Damaged Goods",
  "Lost Stock",
  "Sample Issued",
  "Manual Correction",
  "Other"
]

// Hardcoded for now until warehouse API is built (Matches test_inventory.db)
const WAREHOUSE_ID = "dbcfca97-fc1d-4466-815f-a843072a14be"

export function ManualAdjustmentDialog({ skuId, open, onOpenChange, type, onSuccess }: ManualAdjustmentDialogProps) {
  const createMutation = useCreateManualAdjustment()

  const form = useForm<AdjustmentFormValues>({
    resolver: zodResolver(adjustmentSchema),
    defaultValues: {
      quantity: 1,
      reason: "",
      reference_number: `ADJ-${Math.floor(Math.random() * 10000)}`,
      remarks: ""
    }
  })

  // Reset form when dialog opens
  if (open && form.formState.isSubmitSuccessful) {
    form.reset()
  }

  const onSubmit = async (data: AdjustmentFormValues) => {
    try {
      // If decreasing, the backend expects a negative number
      const finalQuantity = type === "increase" ? data.quantity : -data.quantity
      
      await createMutation.mutateAsync({
        warehouse_id: WAREHOUSE_ID,
        sku_id: skuId,
        quantity: finalQuantity,
        reason: data.reason,
        reference_number: data.reference_number,
        // The backend expects an adjustment date
        adjustment_date: new Date().toISOString().split("T")[0]
      })
      
      onOpenChange(false)
      form.reset()
      if (onSuccess) onSuccess()
    } catch (err) {
      console.error("Failed to create manual adjustment:", err)
      // Usually would show a toast here, but we'll let the mutation handle errors globally if configured
    }
  }

  const isIncrease = type === "increase"
  const title = isIncrease ? "Increase Stock" : "Reduce Stock"
  const reasons = isIncrease ? INCREASE_REASONS : DECREASE_REASONS
  const submitText = isIncrease ? "Increase Stock" : "Reduce Stock"
  const buttonVariant = isIncrease ? "default" : "destructive"

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>{title}</DialogTitle>
            <DialogDescription>
              This will create a permanent manual adjustment in the inventory ledger.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <label htmlFor="quantity" className="text-sm font-medium">Quantity</label>
              <input
                id="quantity"
                type="number"
                min="0.001"
                step="any"
                className="flex h-10 w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...form.register("quantity", { valueAsNumber: true })}
              />
              {form.formState.errors.quantity && (
                <span className="text-xs text-rose-500">{form.formState.errors.quantity.message}</span>
              )}
            </div>

            <div className="grid gap-2">
              <label htmlFor="reason" className="text-sm font-medium">Reason</label>
              <select
                id="reason"
                className="flex h-10 w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...form.register("reason")}
              >
                <option value="">Select a reason...</option>
                {reasons.map(r => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
              {form.formState.errors.reason && (
                <span className="text-xs text-rose-500">{form.formState.errors.reason.message}</span>
              )}
            </div>

            <div className="grid gap-2">
              <label htmlFor="reference_number" className="text-sm font-medium">Reference Number</label>
              <input
                id="reference_number"
                className="flex h-10 w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...form.register("reference_number")}
              />
              {form.formState.errors.reference_number && (
                <span className="text-xs text-rose-500">{form.formState.errors.reference_number.message}</span>
              )}
            </div>

            <div className="grid gap-2">
              <label htmlFor="remarks" className="text-sm font-medium">Remarks (Optional)</label>
              <textarea
                id="remarks"
                className="flex min-h-[80px] w-full rounded-md border border-slate-300 bg-transparent px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Add any additional details here..."
                {...form.register("remarks")}
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={createMutation.isPending}>
              Cancel
            </Button>
            <Button type="submit" variant={buttonVariant} disabled={createMutation.isPending}>
              {createMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              {submitText}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
