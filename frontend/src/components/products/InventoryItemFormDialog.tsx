// @ts-nocheck
import { useEffect, useState, useMemo } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, SelectGroup, SelectLabel } from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useProducts, useCategories, useCreateInventoryItem, useUpdateSKU, useUpdateProduct, useUnitsOfMeasure, type SKUResponse } from "@/api/masters"

const formSchema = z.object({
  item_type: z.string().min(1, "Item type is required"),
  
  category_id: z.string().optional(),
  new_category_name: z.string().optional(),
  
  product_id: z.string().optional(),
  new_product_name: z.string().optional(),

  item_code: z.string().max(50).optional(),
  sku_code: z.string().max(50).optional(),
  
  color: z.string().max(255).optional(),
  size: z.string().max(50).optional(),
  barcode: z.string().max(100).optional(),
  base_uom_id: z.string().optional(),
  
  attribute_values: z.record(z.string()).optional(),

}).refine(data => data.category_id || data.new_category_name, {
  message: "Category is required",
  path: ["category_id"]
}).refine(data => data.product_id || data.new_product_name, {
  message: "Master Item is required",
  path: ["product_id"]
}).refine(data => {
  if (data.item_type !== "FINISHED_GOODS" && !data.base_uom_id) return false;
  return true;
}, {
  message: "Unit of Measure is required for components",
  path: ["base_uom_id"]
});

type FormValues = z.infer<typeof formSchema>

interface InventoryItemFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialData?: SKUResponse | null
  defaultCategoryId?: string
  defaultItemType?: string
  onSuccess?: () => void
}

export function InventoryItemFormDialog({ open, onOpenChange, initialData, defaultCategoryId, defaultItemType, onSuccess }: InventoryItemFormDialogProps) {
  const isEdit = !!initialData

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      item_type: initialData?.product?.item_type || defaultItemType || "FINISHED_GOODS",
      category_id: initialData?.product?.category_id || defaultCategoryId || "",
      product_id: initialData?.product_id || "",
      new_category_name: "",
      new_product_name: initialData?.product?.product_name || "",
      item_code: "",
      sku_code: "",
      color: "",
      size: "",
      barcode: "",
      base_uom_id: "",
      attribute_values: {},
    },
  })

  const itemType = form.watch("item_type")
  const categoryId = form.watch("category_id")
  const productId = form.watch("product_id")

  const { data: categories } = useCategories(itemType)
  const { data: products } = useProducts()
  const { data: uoms } = useUnitsOfMeasure()
  
  const filteredProducts = products?.filter(p => (p.item_type || "FINISHED_GOODS") === itemType) || []

  // Extract dynamic attributes from the selected category
  const dynamicAttributes = useMemo(() => {
    if (!categories || !categoryId || categoryId === "NEW") return [];
    const cat = categories.find(c => c.id === categoryId);
    return cat?.attributes || [];
  }, [categories, categoryId])

  const newCatName = form.watch("new_category_name")
  const newProdName = form.watch("new_product_name")

  const createMutation = useCreateInventoryItem()
  const updateMutation = useUpdateSKU()
  const updateProductMutation = useUpdateProduct()

  useEffect(() => {
    if (open) {
      if (initialData) {
        form.reset({
          item_type: initialData.product?.item_type || "FINISHED_GOODS",
          category_id: initialData.product?.category_id || "existing_but_unknown",
          product_id: initialData.product?.id || "",
          new_product_name: initialData.product?.product_name || "",
          item_code: initialData.item_code || "",
          sku_code: initialData.sku_code || "",
          color: initialData.color || "",
          size: initialData.size || "",
          barcode: initialData.barcode || "",
          base_uom_id: (initialData as any).uom_id || "",
          attribute_values: initialData.attribute_values || {},
        })
      } else {
        form.reset({
          item_type: defaultItemType || "FINISHED_GOODS",
          category_id: defaultCategoryId || "",
          new_category_name: "",
          product_id: "",
          new_product_name: "",
          item_code: "",
          sku_code: "",
          color: "",
          size: "",
          barcode: "",
          base_uom_id: "",
          attribute_values: {},
        })
      }
    }
  }, [open, initialData, form, defaultCategoryId, defaultItemType, products])

  const onSubmit = async (values: FormValues) => {
    try {
      const attribute_values = { ...values.attribute_values };
      Object.keys(attribute_values).forEach(key => {
        if (!attribute_values[key]) {
          delete attribute_values[key]
        }
      })

      if (isEdit) {
        // Update SKU
        await updateMutation.mutateAsync({
          id: initialData.id,
          data: {
            size: values.size || undefined,
            color: values.color || undefined,
            barcode: values.barcode || undefined,
            item_code: values.item_code || undefined,
            product_id: values.product_id !== "NEW" ? values.product_id : undefined,
            uom_id: values.base_uom_id || undefined,
            attribute_values,
          }
        })
        
        // Update Product Name if changed
        if (values.new_product_name && values.new_product_name !== initialData.product?.product_name) {
          await updateProductMutation.mutateAsync({
            id: initialData.product_id,
            data: { product_name: values.new_product_name }
          })
        }
      } else {
        // Auto-generate codes if missing
        const randomHex = () => Math.random().toString(16).substring(2, 8).toUpperCase();
        const finalItemCode = values.item_code || `ITM-${randomHex()}`;
        const finalSkuCode = values.sku_code || `SKU-${randomHex()}`;

        await createMutation.mutateAsync({
          item_type: values.item_type,
          category_id: values.category_id === "NEW" ? undefined : values.category_id,
          new_category_name: values.category_id === "NEW" ? values.new_category_name : undefined,
          product_id: values.product_id === "NEW" ? undefined : values.product_id,
          new_product_name: values.product_id === "NEW" ? values.new_product_name : undefined,
          item_code: finalItemCode,
          sku_code: finalSkuCode,
          color: values.color || undefined,
          size: values.size || undefined,
          barcode: values.barcode || undefined,
          base_uom_id: values.base_uom_id || undefined,
          attribute_values,
        } as any)
      }
      onSuccess?.()
      onOpenChange(false)
    } catch (error) {
      console.error("Failed to save Item:", error)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] h-[90vh] flex flex-col p-0">
        <DialogHeader className="p-6 pb-4 border-b shrink-0">
          <DialogTitle>{isEdit ? "Edit Inventory Item" : "Add Inventory Item"}</DialogTitle>
          <DialogDescription>
            {isEdit ? "Update the details of this item." : "Create a new inventory item and its master details."}
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
                      <FormLabel>Inventory Type</FormLabel>
                      <Select 
                        onValueChange={(val) => {
                          field.onChange(val)
                          form.setValue("category_id", "")
                          form.setValue("product_id", "")
                        }}
                        defaultValue={field.value || undefined}
                        value={field.value || undefined}
                      >
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

                <div className="grid grid-cols-2 gap-4 border p-3 rounded-md bg-slate-50">
                  <div className="col-span-2">
                    <FormField
                      control={form.control}
                      name="category_id"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Category</FormLabel>
                          <Select 
                            onValueChange={field.onChange} 
                            defaultValue={field.value || undefined}
                            value={field.value || undefined}
                          >
                            <FormControl>
                              <SelectTrigger className="bg-white">
                                <SelectValue placeholder="Select category" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectGroup>
                                <SelectItem value="NEW" className="text-primary font-semibold border-b mb-1">
                                  + Create Category
                                </SelectItem>
                              </SelectGroup>
                              <SelectGroup>
                                <SelectLabel>Existing Categories</SelectLabel>
                                {categories?.map(c => (
                                  <SelectItem key={c.id} value={c.id}>
                                    {c.category_name}
                                  </SelectItem>
                                ))}
                              </SelectGroup>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  {categoryId === "NEW" && (
                    <div className="col-span-2">
                      <FormField
                        control={form.control}
                        name="new_category_name"
                        render={({ field }) => (
                          <FormItem>
                            <FormControl>
                              <Input placeholder="Type new category name..." {...field} className="bg-white" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  )}

                  <div className="col-span-2 mt-2">
                    <FormField
                      control={form.control}
                      name="product_id"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Master Item</FormLabel>
                          <Select 
                            onValueChange={field.onChange} 
                            defaultValue={field.value || undefined}
                            value={field.value || undefined}
                          >
                            <FormControl>
                              <SelectTrigger className="bg-white">
                                <SelectValue placeholder="Select master item" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {!isEdit && (
                                <SelectGroup>
                                  <SelectItem value="NEW" className="text-primary font-semibold border-b mb-1">
                                    + Create Master Item
                                  </SelectItem>
                                </SelectGroup>
                              )}
                              <SelectGroup>
                                <SelectLabel>Existing Master Items</SelectLabel>
                                {filteredProducts.map(p => (
                                  <SelectItem key={p.id} value={p.id}>
                                    {p.product_name}
                                  </SelectItem>
                                ))}
                              </SelectGroup>
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  {(productId === "NEW" || isEdit) && (
                    <div className="col-span-2">
                      <FormField
                        control={form.control}
                        name="new_product_name"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>{isEdit ? "Master Item Name" : ""}</FormLabel>
                            <FormControl>
                              <Input placeholder={isEdit ? "Edit master item name..." : "Type new master item name..."} {...field} className="bg-white" />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                  <FormField
                    control={form.control}
                    name="item_code"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Item Code (Auto-generated if blank)</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g. RM-FAB-001" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {itemType !== "FINISHED_GOODS" && (
                    <FormField
                      control={form.control}
                      name="base_uom_id"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Base Unit of Measure</FormLabel>
                          <Select onValueChange={field.onChange} value={field.value || undefined} defaultValue={field.value || undefined}>
                            <FormControl>
                              <SelectTrigger className="bg-white">
                                <SelectValue placeholder="Select UOM" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {uoms?.filter(u => u.status?.toUpperCase() === 'ACTIVE').map(u => (
                                <SelectItem key={u.id} value={u.id}>{u.unit_name} ({u.short_name})</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  )}

                  {itemType === "FINISHED_GOODS" && (
                    <FormField
                      control={form.control}
                      name="sku_code"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>SKU Code (Auto-generated if blank)</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g. TSHIRT-RED-L" {...field} disabled={isEdit} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  )}
                </div>

                <div className="pt-2">
                  {itemType === "FINISHED_GOODS" && (
                    <>
                      <label className="text-sm font-medium leading-none text-slate-500 mb-3 block">Variant Details (Optional)</label>
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <FormField control={form.control} name="color" render={({ field }) => (<FormItem><FormLabel>Color</FormLabel><FormControl><Input placeholder="e.g. Red" {...field} /></FormControl></FormItem>)} />
                        <FormField control={form.control} name="size" render={({ field }) => (<FormItem><FormLabel>Size</FormLabel><FormControl><Input placeholder="e.g. L, 42" {...field} /></FormControl></FormItem>)} />
                      </div>
                    </>
                  )}

                  {dynamicAttributes.length > 0 && (
                    <div className="mt-4">
                      <label className="text-sm font-medium leading-none text-slate-500 mb-3 block">Dynamic Attributes</label>
                      <div className="grid grid-cols-2 gap-4">
                        {dynamicAttributes.map(attr => (
                          <FormField 
                            key={attr.attribute_name}
                            control={form.control} 
                            name={`attribute_values.${attr.attribute_name}`} 
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>{attr.attribute_name}</FormLabel>
                                <FormControl>
                                  <Input placeholder={`Enter ${attr.attribute_name}`} {...field} value={field.value || ""} />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )} 
                          />
                        ))}
                      </div>
                    </div>
                  )}

                </div>

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
                {createMutation.isPending || updateMutation.isPending ? "Saving..." : "Save Item"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
