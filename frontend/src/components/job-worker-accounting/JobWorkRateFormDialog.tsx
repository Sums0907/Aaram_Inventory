// @ts-nocheck
import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useCreateJobWorkRate } from "@/api/job-worker-accounting"
import type { Supplier } from "@/api/suppliers"
import type { SKUResponse } from "@/api/masters"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

const formSchema = z.object({
  job_worker_id: z.string().uuid("Please select a Job Worker"),
  sku_id: z.string().uuid("Please select a Product"),
  rate: z.coerce.number().positive("Rate must be greater than 0"),
  rate_basis: z.string().default("PER_PIECE"),
  effective_from: z.string().min(10, "Date is required"),
  notes: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
  suppliers: Supplier[]
  skus: SKUResponse[]
}

export function JobWorkRateFormDialog({ open, onOpenChange, suppliers, skus }: Props) {
  const { toast } = useToast()
  const createRate = useCreateJobWorkRate()
  
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      rate_basis: "PER_PIECE",
      effective_from: new Date().toISOString().split('T')[0],
      notes: "",
    },
  })

  // Filter job workers only
  const jobWorkers = suppliers.filter(s => s.is_job_worker)

  // Filter only finished goods (or all SKUs if item_type isn't available on SKU easily, but ideally we should let them select valid products)
  // Assuming all SKUs are available for now, but we label it 'Job Worked Product'
  
  async function onSubmit(values: FormValues) {
    try {
      await createRate.mutateAsync(values)
      toast({
        title: "Rate Created",
        description: "The new Job Work Rate has been configured.",
      })
      form.reset()
      onOpenChange(false)
    } catch (error: any) {
      toast({
        title: "Failed to create rate",
        description: error.response?.data?.detail || error.message || "An error occurred",
        variant: "destructive",
      })
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add Job Work Rate</DialogTitle>
          <DialogDescription>
            Configure the rate per piece for a specific Job Worker and Product. 
            <br/><br/>
            <strong>Note:</strong> If an active rate already exists for this combination, it will be automatically archived, and this new rate will become the only active rate.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 py-4">
            
            <FormField
              control={form.control}
              name="job_worker_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Job Worker</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="[ Select Job Worker ▼ ]" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {jobWorkers.map(jw => (
                        <SelectItem key={jw.id} value={jw.id}>{jw.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="sku_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Job Worked Product</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="[ Select Product ▼ ]" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {skus.map(sku => (
                        <SelectItem key={sku.id} value={sku.id}>
                          {sku.product?.product_name} <span className="text-slate-400">({sku.item_code})</span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="rate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Rate (₹)</FormLabel>
                    <FormControl>
                      <Input type="number" step="0.01" placeholder="e.g. 150.00" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="rate_basis"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Basis</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="PER_PIECE">Per Piece</SelectItem>
                        <SelectItem value="FIXED">Fixed Amount</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="effective_from"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Effective From</FormLabel>
                  <FormControl>
                    <Input type="date" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
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
              <Button type="submit" disabled={createRate.isPending} className="bg-indigo-600 hover:bg-indigo-700">
                {createRate.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Revise / Create Rate
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
