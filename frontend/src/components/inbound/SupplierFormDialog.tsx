// @ts-nocheck
import { useState } from "react"
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
import { useToast } from "@/hooks/use-toast"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/api/client"

const supplierSchema = z.object({
  name: z.string().min(1, "Name is required"),
  code: z.string().optional(),
  contact_person: z.string().optional(),
  email: z.string().email("Invalid email").optional().or(z.literal("")),
  phone: z.string().optional(),
  gst_number: z.string().optional(),
})

type SupplierFormValues = z.infer<typeof supplierSchema>

interface SupplierFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: (supplierId: string) => void
}

export function SupplierFormDialog({ open, onOpenChange, onSuccess }: SupplierFormDialogProps) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  
  const form = useForm<SupplierFormValues>({
    resolver: zodResolver(supplierSchema),
    defaultValues: {
      name: "",
      code: "",
      contact_person: "",
      email: "",
      phone: "",
      gst_number: "",
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data: SupplierFormValues) => {
      const response = await apiClient.post("/masters/suppliers", data)
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["suppliers"] })
      toast({ title: "Supplier created successfully" })
      onOpenChange(false)
      form.reset()
      if (onSuccess && data?.id) {
        onSuccess(data.id)
      }
    },
    onError: (error: any) => {
      toast({
        title: "Failed to create supplier",
        description: error.response?.data?.message || "An unexpected error occurred",
        variant: "destructive",
      })
    }
  })

  const onSubmit = (data: SupplierFormValues) => {
    createMutation.mutate(data)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add New Supplier</DialogTitle>
        </DialogHeader>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 pt-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Supplier Name *</FormLabel>
                  <FormControl>
                    <Input placeholder="E.g. ABC Trading Co." {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="gst_number"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>GST Number</FormLabel>
                  <FormControl>
                    <Input placeholder="29ABCDE1234F1Z5" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="flex justify-end pt-4 space-x-2 border-t border-slate-100">
              <Button variant="outline" type="button" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={createMutation.isPending}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                {createMutation.isPending ? "Saving..." : "Save Supplier"}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
