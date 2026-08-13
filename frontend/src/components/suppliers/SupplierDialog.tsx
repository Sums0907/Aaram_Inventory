import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import {
  Dialog,
  DialogContent,
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
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { useSupplier, useCreateSupplier, useUpdateSupplier } from "@/api/suppliers"

const supplierSchema = z.object({
  name: z.string().min(1, "Name is required"),
  gstin: z.string().optional(),
  contact_number: z.string().optional(),
  email: z.string().email("Invalid email address").optional().or(z.literal("")),
  address: z.string().optional(),
  is_job_worker: z.boolean().default(false),
})

type SupplierFormValues = z.infer<typeof supplierSchema>

interface SupplierDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  supplierId: string | null
}

export function SupplierDialog({ open, onOpenChange, supplierId }: SupplierDialogProps) {
  const { data: supplier, isLoading } = useSupplier(supplierId || "")
  const createMutation = useCreateSupplier()
  const updateMutation = useUpdateSupplier()

  const form = useForm<SupplierFormValues>({
    resolver: zodResolver(supplierSchema),
    defaultValues: {
      name: "",
      gstin: "",
      contact_number: "",
      email: "",
      address: "",
      is_job_worker: false,
    },
  })

  useEffect(() => {
    if (supplier && supplierId) {
      form.reset({
        name: supplier.name,
        gstin: supplier.gstin || "",
        contact_number: supplier.contact_number || "",
        email: supplier.email || "",
        address: supplier.address || "",
        is_job_worker: supplier.is_job_worker || false,
      })
    } else if (!supplierId) {
      form.reset({
        name: "",
        gstin: "",
        contact_number: "",
        email: "",
        address: "",
        is_job_worker: false,
      })
    }
  }, [supplier, supplierId, form])

  const onSubmit = async (data: SupplierFormValues) => {
    try {
      if (supplierId) {
        await updateMutation.mutateAsync({ id: supplierId, ...data })
      } else {
        await createMutation.mutateAsync(data)
      }
      onOpenChange(false)
    } catch (error) {
      console.error("Failed to save supplier", error)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{supplierId ? "Edit Supplier" : "Add Supplier"}</DialogTitle>
        </DialogHeader>
        
        {isLoading && supplierId ? (
          <div className="py-6 text-center text-slate-500">Loading...</div>
        ) : (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Supplier Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter supplier name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="gstin"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>GSTIN</FormLabel>
                    <FormControl>
                      <Input placeholder="GSTIN (Optional)" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="contact_number"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Contact Number</FormLabel>
                      <FormControl>
                        <Input placeholder="Phone number" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input placeholder="Email address" type="email" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="address"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Address</FormLabel>
                    <FormControl>
                      <Input placeholder="Full address" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="is_job_worker"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">
                        Job Worker
                      </FormLabel>
                      <div className="text-sm text-muted-foreground">
                        Allow issuing and receiving materials for job work.
                      </div>
                    </div>
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              <div className="flex justify-end pt-4 space-x-2">
                <Button variant="outline" type="button" onClick={() => onOpenChange(false)}>
                  Cancel
                </Button>
                <Button 
                  type="submit" 
                  disabled={createMutation.isPending || updateMutation.isPending}
                  className="bg-indigo-600 hover:bg-indigo-700"
                >
                  {createMutation.isPending || updateMutation.isPending ? "Saving..." : "Save Supplier"}
                </Button>
              </div>
            </form>
          </Form>
        )}
      </DialogContent>
    </Dialog>
  )
}
