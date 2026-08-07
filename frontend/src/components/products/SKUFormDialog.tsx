import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useProducts, useCreateSKU, useUpdateSKU, type SKUResponse } from "@/api/masters"

const formSchema = z.object({
  sku_code: z.string().min(1, "SKU Code/Item Code is required").max(50),
  item_type: z.string().min(1, "Item type is required"),
  product_id: z.string().min(1, "Product is required"),
  color: z.string().max(255).optional(),
  size: z.string().max(50).optional(),
  barcode: z.string().max(100).optional(),
  pattern: z.string().max(255).optional(),
  material: z.string().max(255).optional(),
  thread_count: z.string().max(50).optional(),
  gsm: z.string().max(50).optional(),
  width: z.string().max(50).optional(),
  package_size: z.string().max(50).optional(),
  box_size: z.string().max(50).optional(),
  brand: z.string().max(100).optional(),
  model_number: z.string().max(100).optional(),
  manufacturer: z.string().max(100).optional(),
})

type FormValues = z.infer<typeof formSchema>

interface SKUFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialData?: SKUResponse | null
  onSuccess?: () => void
}

export function SKUFormDialog({ open, onOpenChange, initialData, onSuccess }: SKUFormDialogProps) {
  const { data: products } = useProducts()
  const createMutation = useCreateSKU()
  const updateMutation = useUpdateSKU()

  const isEdit = !!initialData

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      sku_code: "",
      item_type: "FINISHED_GOODS",
      product_id: "",
      color: "",
      size: "",
      barcode: "",
      pattern: "",
      material: "",
      thread_count: "",
      gsm: "",
      width: "",
      package_size: "",
      box_size: "",
      brand: "",
      model_number: "",
      manufacturer: "",
    },
  })

  const itemType = form.watch("item_type")
  const filteredProducts = products?.filter(p => (p.item_type || "FINISHED_GOODS") === itemType) || []

  useEffect(() => {
    if (open) {
      if (initialData) {
        form.reset({
          sku_code: initialData.sku_code || "",
          item_type: initialData.product?.item_type || "FINISHED_GOODS",
          product_id: initialData.product?.id || "",
          color: initialData.color || "",
          size: initialData.size || "",
          barcode: initialData.barcode || "",
          pattern: initialData.pattern || "",
          material: initialData.material || "",
          thread_count: initialData.thread_count || "",
          gsm: initialData.attribute_values?.gsm || "",
          width: initialData.attribute_values?.width || "",
          package_size: initialData.attribute_values?.package_size || "",
          box_size: initialData.attribute_values?.box_size || "",
          brand: initialData.attribute_values?.brand || "",
          model_number: initialData.attribute_values?.model_number || "",
          manufacturer: initialData.attribute_values?.manufacturer || "",
        })
      } else {
        form.reset({
          sku_code: "",
          item_type: "FINISHED_GOODS",
          product_id: "",
          color: "",
          size: "",
          barcode: "",
          pattern: "",
          material: "",
          thread_count: "",
          gsm: "",
          width: "",
          package_size: "",
          box_size: "",
          brand: "",
          model_number: "",
          manufacturer: "",
        })
      }
    }
  }, [open, initialData, form])

  const onSubmit = async (values: FormValues) => {
    try {
      const attribute_values = {
        gsm: values.gsm,
        width: values.width,
        package_size: values.package_size,
        box_size: values.box_size,
        brand: values.brand,
        model_number: values.model_number,
        manufacturer: values.manufacturer,
      }

      // Cleanup empty attributes
      Object.keys(attribute_values).forEach(key => {
        if (!attribute_values[key as keyof typeof attribute_values]) {
          delete attribute_values[key as keyof typeof attribute_values]
        }
      })

      if (isEdit) {
        await updateMutation.mutateAsync({
          id: initialData.id,
          data: {
            color: values.color,
            size: values.size,
            barcode: values.barcode,
            pattern: values.pattern,
            material: values.material,
            thread_count: values.thread_count,
            attribute_values,
          }
        })
      } else {
        await createMutation.mutateAsync({
          sku_code: values.sku_code,
          product_id: values.product_id,
          color: values.color,
          size: values.size,
          barcode: values.barcode,
          pattern: values.pattern,
          material: values.material,
          thread_count: values.thread_count,
          attribute_values,
        })
      }
      onSuccess?.()
      onOpenChange(false)
    } catch (error) {
      console.error("Failed to save SKU:", error)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] h-[90vh] flex flex-col p-0">
        <DialogHeader className="p-6 pb-4 border-b shrink-0">
          <DialogTitle>{isEdit ? "Edit SKU" : "Add New SKU"}</DialogTitle>
          <DialogDescription>
            {isEdit ? "Update the details of this SKU." : "Create a new Stock Keeping Unit."}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col overflow-hidden">
            
            <ScrollArea className="flex-1 p-6 space-y-4">
              
              <div className="space-y-4 pb-4">
                <FormField
                  control={form.control}
                  name="item_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Item Type</FormLabel>
                      <Select 
                        disabled={isEdit} 
                        onValueChange={(val) => {
                          field.onChange(val)
                          form.setValue("product_id", "") // reset product when type changes
                        }}
                        defaultValue={field.value}
                        value={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select item type" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="FINISHED_GOODS">Finished Goods (SKU)</SelectItem>
                          <SelectItem value="RAW_MATERIAL">Raw Material (Fabric/etc)</SelectItem>
                          <SelectItem value="CONSUMABLE">Consumable (Thread/etc)</SelectItem>
                          <SelectItem value="PACKAGING_MATERIAL">Packaging Material</SelectItem>
                          <SelectItem value="ASSET">Asset (Machinery)</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="sku_code"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>SKU Code</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. TSHIRT-RED-L" {...field} disabled={isEdit} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="product_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Product</FormLabel>
                      <Select 
                        disabled={isEdit || !products} 
                        onValueChange={field.onChange} 
                        defaultValue={field.value}
                        value={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a product" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {filteredProducts.map(p => (
                            <SelectItem key={p.id} value={p.id}>
                              {p.product_name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {itemType === "FINISHED_GOODS" && (
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="color"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Color</FormLabel>
                            <FormControl>
                              <Input placeholder="e.g. Red" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="size"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Size</FormLabel>
                            <FormControl>
                              <Input placeholder="e.g. L, 42" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="pattern"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Pattern</FormLabel>
                            <FormControl>
                              <Input placeholder="e.g. Striped" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <FormField
                        control={form.control}
                        name="thread_count"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Thread Count</FormLabel>
                            <FormControl>
                              <Input placeholder="e.g. 200 TC" {...field} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </>
                )}

                {itemType === "RAW_MATERIAL" && (
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="material"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Fabric Type</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. Cotton" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="gsm"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>GSM</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. 200" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="width"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Width</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. 54 inch" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="color"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Color</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. White" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                )}

                {itemType === "CONSUMABLE" && (
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="package_size"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Package Size</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. 100m, 5kg" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="brand"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Brand (Optional)</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. 3M" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                )}

                {itemType === "PACKAGING_MATERIAL" && (
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="box_size"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Box Size</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. 12x10x4" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="material"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Material</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. Corrugated Cardboard" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                )}

                {itemType === "ASSET" && (
                  <div className="grid grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="model_number"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Model Number</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. MX-2000" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="manufacturer"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Manufacturer</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. Brother, Juki" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                )}

                <div className="pt-2 border-t">
                  <FormField
                    control={form.control}
                    name="barcode"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Barcode (Optional)</FormLabel>
                        <FormControl>
                          <Input placeholder="Scan or enter barcode" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>

            </ScrollArea>

            <DialogFooter className="p-6 pt-4 border-t shrink-0 bg-slate-50">
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
                {createMutation.isPending || updateMutation.isPending ? "Saving..." : "Save SKU"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
