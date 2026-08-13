import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useRecordJobWorkerPayment } from "@/api/job-worker-accounting"
import { useToast } from "@/hooks/use-toast"
import { Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const formSchema = z.object({
  job_worker_id: z.string().uuid(),
  payment_date: z.string().min(10, "Date is required"),
  amount: z.coerce.number().positive("Amount must be greater than 0"),
  payment_account: z.string().optional(),
  payment_reference: z.string().optional(),
  notes: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
  jobWorkerId: string
  jobWorkerName: string
  currentOutstanding: number
}

export function RecordJobWorkerPaymentDialog({ open, onOpenChange, jobWorkerId, jobWorkerName, currentOutstanding }: Props) {
  const { toast } = useToast()
  const recordPayment = useRecordJobWorkerPayment()
  
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      job_worker_id: jobWorkerId,
      payment_date: new Date().toISOString().split('T')[0],
      amount: currentOutstanding > 0 ? currentOutstanding : 0, // default to full payment
      payment_account: "Bank",
      payment_reference: "",
      notes: "",
    },
  })

  // Track amount to show remaining dynamically
  const watchAmount = form.watch("amount", 0)
  const remaining = currentOutstanding - (watchAmount || 0)

  async function onSubmit(values: FormValues) {
    if (values.amount > currentOutstanding) {
      form.setError("amount", {
        type: "manual",
        message: "Payment cannot exceed the outstanding payable."
      })
      return
    }

    try {
      await recordPayment.mutateAsync(values)
      toast({
        title: "Payment Recorded",
        description: `Recorded payment of ₹${values.amount} for ${jobWorkerName}.`,
      })
      form.reset()
      onOpenChange(false)
    } catch (error: any) {
      toast({
        title: "Failed to record payment",
        description: error.response?.data?.detail || error.message || "An error occurred",
        variant: "destructive",
      })
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Record Payment</DialogTitle>
          <DialogDescription>
            Settle outstanding Job Work expenses for {jobWorkerName}.
          </DialogDescription>
        </DialogHeader>

        <div className="bg-slate-50 border border-slate-100 rounded-lg p-4 mb-2">
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm text-slate-500">Current Outstanding:</span>
            <span className="font-mono font-medium text-slate-900">{formatCurrency(currentOutstanding)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-500">Remaining after payment:</span>
            <span className={`font-mono font-bold ${remaining < 0 ? 'text-red-600' : 'text-indigo-600'}`}>
              {formatCurrency(remaining)}
            </span>
          </div>
        </div>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="payment_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Payment Date</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="amount"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Amount (₹)</FormLabel>
                    <FormControl>
                      <Input type="number" step="0.01" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="payment_account"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Payment Account</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select account" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="Bank">Bank</SelectItem>
                        <SelectItem value="Cash">Cash</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="payment_reference"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Reference (UTR)</FormLabel>
                    <FormControl>
                      <Input placeholder="e.g. UTR123456" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes (Optional)</FormLabel>
                  <FormControl>
                    <Textarea placeholder="Any remarks..." {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter className="pt-4">
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={recordPayment.isPending} className="bg-indigo-600 hover:bg-indigo-700">
                {recordPayment.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Record Payment
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
