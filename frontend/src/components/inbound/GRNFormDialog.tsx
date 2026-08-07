import { useState } from "react"
import { useForm, useFieldArray } from "react-hook-form"
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Plus, Trash2 } from "lucide-react"

import { useCreateGoodsReceipt } from "@/api/goods-receipts"
import { useSuppliers } from "@/api/suppliers"
import { useSKUs } from "@/api/masters"
import { useToast } from "@/hooks/use-toast"
import { SupplierFormDialog } from "@/components/inbound/SupplierFormDialog"

const itemSchema = z.object({
  item_type: z.string().optional(),
  sku_id: z.string().min(1, "Item is required"),
  quantity: z.coerce.number().int().positive("Quantity must be positive"),
  unit_of_measure: z.string().optional(),
})

const grnSchema = z.object({
  grn_number: z.string().min(1, "GRN number is required"),
  supplier_id: z.string().min(1, "Supplier is required"),
  warehouse_id: z.string().min(1, "Warehouse is required"),
  receipt_date: z.string().min(1, "Date is required"),
  invoice_number: z.string().optional(),
  challan_number: z.string().optional(),
  remarks: z.string().optional(),
  items: z.array(itemSchema).min(1, "At least one item is required"),
})

type GRNFormValues = z.infer<typeof grnSchema>

interface GRNFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  defaultSkuId?: string
}

export function GRNFormDialog({ open, onOpenChange, defaultSkuId }: GRNFormDialogProps) {
  const { toast } = useToast()
  const createMutation = useCreateGoodsReceipt()
  const [isSupplierDialogOpen, setIsSupplierDialogOpen] = useState(false)
  
  const { data: suppliersData } = useSuppliers(0, 100)
  const { data: skus } = useSKUs()
  const suppliers = suppliersData?.data || []

  // Hardcoded to "Main Warehouse" ID from the database for now until warehouse API is available
  const warehouseId = "96c6b20c-d119-4f97-b635-c8e5ef87fd52" 

  const generateGrnNumber = () => {
    const year = new Date().getFullYear();
    const randomSeq = Math.floor(Math.random() * 90000) + 10000;
    return `GRN-${year}-${randomSeq}`;
  }

  const form = useForm<GRNFormValues>({
    resolver: zodResolver(grnSchema),
    defaultValues: {
      grn_number: generateGrnNumber(),
      supplier_id: "",
      warehouse_id: warehouseId,
      receipt_date: new Date().toISOString().split("T")[0],
      invoice_number: "",
      challan_number: "",
      remarks: "",
      items: [{ item_type: "FINISHED_GOODS", sku_id: defaultSkuId || "", quantity: 1, unit_of_measure: "PCS" }],
    },
  })

  const { fields, append, remove } = useFieldArray({
    name: "items",
    control: form.control,
  })

  const onSubmit = async (data: GRNFormValues) => {
    try {
      await createMutation.mutateAsync(data)
      toast({
        title: "Goods Receipt Note (GRN) created",
        description: "Inventory stock balances have been updated successfully.",
      })
      onOpenChange(false)
      form.reset({
        ...form.getValues(),
        grn_number: generateGrnNumber(),
        items: [{ item_type: "FINISHED_GOODS", sku_id: defaultSkuId || "", quantity: 1, unit_of_measure: "PCS" }]
      })
    } catch (error: any) {
      toast({
        title: "Failed to create GRN",
        description: error.response?.data?.message || "An unexpected error occurred",
        variant: "destructive",
      })
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>New Goods Receipt Note (GRN)</DialogTitle>
        </DialogHeader>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 pt-4">
            
            {/* Header Details */}
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="grn_number"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>GRN Number</FormLabel>
                    <FormControl>
                      <Input placeholder="GRN-1234" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="receipt_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Receipt Date</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="supplier_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Supplier</FormLabel>
                    <div className="flex gap-2">
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger className="flex-1">
                            <SelectValue placeholder="Select supplier" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {suppliers.map((s: any) => (
                            <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <Button type="button" variant="outline" onClick={() => setIsSupplierDialogOpen(true)}>
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="invoice_number"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Invoice Number (Optional)</FormLabel>
                    <FormControl>
                      <Input placeholder="INV-..." {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="col-span-2">
                <FormField
                  control={form.control}
                  name="remarks"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Remarks (Optional)</FormLabel>
                      <FormControl>
                        <Input placeholder="E.g. Boxes damaged, replacement stock, urgent..." {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Line Items */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium">Line Items</h3>
                <Button 
                  type="button" 
                  variant="outline" 
                  size="sm"
                  onClick={() => append({ item_type: "FINISHED_GOODS", sku_id: "", quantity: 1, unit_of_measure: "PCS" })}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Row
                </Button>
              </div>

              {fields.map((field, index) => (
                <div key={field.id} className="flex gap-4 items-start bg-slate-50 p-4 rounded-lg border border-slate-100">
                  <FormField
                    control={form.control}
                    name={`items.${index}.item_type`}
                    render={({ field }) => (
                      <FormItem className="w-[180px]">
                        <FormLabel className={index !== 0 ? "sr-only" : ""}>Inventory Type</FormLabel>
                        <Select onValueChange={(val) => {
                          field.onChange(val)
                          form.setValue(`items.${index}.sku_id`, "")
                        }} defaultValue={field.value} value={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select type" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="FINISHED_GOODS">Finished Goods</SelectItem>
                            <SelectItem value="RAW_MATERIAL">Raw Material</SelectItem>
                            <SelectItem value="CONSUMABLE">Consumable</SelectItem>
                            <SelectItem value="PACKAGING_MATERIAL">Packaging Material</SelectItem>
                            <SelectItem value="ASSET">Asset</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name={`items.${index}.sku_id`}
                    render={({ field }) => {
                      const itemType = form.watch(`items.${index}.item_type`);
                      const filteredSkus = skus?.filter((s: any) => (s.product?.item_type || "FINISHED_GOODS") === itemType) || [];
                      
                      return (
                      <FormItem className="flex-1">
                        <FormLabel className={index !== 0 ? "sr-only" : ""}>Inventory Item</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value} value={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select Item" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {filteredSkus.map((sku: any) => (
                              <SelectItem key={sku.id} value={sku.id}>
                                {sku.item_code} - {sku.product?.product_name || "Unknown"} {sku.sku_code ? `(${sku.sku_code})` : ""}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}}
                  />
                  
                  <FormField
                    control={form.control}
                    name={`items.${index}.quantity`}
                    render={({ field }) => (
                      <FormItem className="w-24">
                        <FormLabel className={index !== 0 ? "sr-only" : ""}>Qty</FormLabel>
                        <FormControl>
                          <Input type="number" min="1" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <Button 
                    type="button" 
                    variant="ghost" 
                    size="icon"
                    className={`text-red-500 hover:text-red-700 hover:bg-red-50 ${index === 0 ? "mt-8" : "mt-2"}`}
                    onClick={() => remove(index)}
                    disabled={fields.length === 1}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-4 space-x-2 border-t border-slate-100">
              <Button variant="outline" type="button" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={createMutation.isPending}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                {createMutation.isPending ? "Processing..." : "Complete Goods Receipt"}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>

      <SupplierFormDialog 
        open={isSupplierDialogOpen} 
        onOpenChange={setIsSupplierDialogOpen}
        onSuccess={(supplierId) => {
          form.setValue("supplier_id", supplierId)
        }}
      />
    </Dialog>
  )
}
