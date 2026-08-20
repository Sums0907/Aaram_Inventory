// @ts-nocheck
import { formatQuantityValue } from "@/lib/utils"
import { useState, useEffect } from "react"
import { useForm, useFieldArray } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, SelectGroup, SelectLabel } from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { useSKUs, useUnitsOfMeasure } from "@/api/masters"
import { useCreateBOM, useArchiveBOM, useRestoreBOM } from "@/api/boms"
import { Plus, Trash2, MoreHorizontal, Archive, RotateCcw, Pencil } from "lucide-react"

const bomItemSchema = z.object({
  component_item_id: z.string().min(1, "Component is required"),
  quantity: z.coerce.number().min(0.0001, "Quantity must be > 0"),
  wastage_percentage: z.coerce.number().min(0).max(100).default(0),
})

const formSchema = z.object({
  bom_number: z.string().min(1, "BOM Number is required"),
  bom_name: z.string().optional(),
  target_item_id: z.string().min(1, "Target item is required"),
  target_quantity: z.coerce.number().min(1, "Target quantity must be at least 1"),
  status: z.string().default("ACTIVE"),
  items: z.array(bomItemSchema).min(1, "At least one component is required"),
})

import type { BOMResponse } from "@/api/boms"

interface BOMFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  bom?: BOMResponse | null
}

export function BOMFormDialog({ open, onOpenChange, bom }: BOMFormDialogProps) {
  const { data: skus } = useSKUs()
  const { data: uoms } = useUnitsOfMeasure()
  const createMutation = useCreateBOM()
  const archiveMutation = useArchiveBOM()
  const restoreMutation = useRestoreBOM()
  
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      bom_number: bom?.bom_number || `BOM-${Date.now().toString().slice(-6)}`,
      bom_name: bom?.bom_name || "",
      target_item_id: bom?.target_item_id || "",
      target_quantity: bom?.target_quantity || 1,
      status: bom?.status || "ACTIVE",
      items: bom?.items || [],
    },
  })

  useEffect(() => {
    if (bom) {
      form.reset({
        bom_number: bom.bom_number,
        bom_name: bom.bom_name || "",
        target_item_id: bom.target_item_id,
        target_quantity: bom.target_quantity,
        status: bom.status,
        items: bom.items,
      })
    } else {
      form.reset({
        bom_number: `BOM-${Date.now().toString().slice(-6)}`,
        bom_name: "",
        target_item_id: "",
        target_quantity: 1,
        status: "ACTIVE",
        items: [],
      })
    }
  }, [bom, form])

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "items",
  })

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    try {
      await createMutation.mutateAsync(values)
      onOpenChange(false)
      form.reset()
    } catch (error) {
      console.error("Failed to create BOM:", error)
      alert("Failed to create BOM. Please check inputs.")
    }
  }

  const finishedGoods = skus?.filter(s => s.product?.item_type === 'FINISHED_GOODS' || !s.product?.item_type) || []
  const availableComponents = skus?.filter(s => s.status?.toUpperCase() === 'ACTIVE' && s.product?.item_type !== 'FINISHED_GOODS') || []

  const getSkuName = (sku: any) => {
    return `${sku.product?.product_name || "Unknown"} ${sku.item_code ? `(${sku.item_code})` : ""}`
  }

  const getSkuUOM = (skuId: string) => {
    const sku = skus?.find(s => s.id === skuId);
    if (!sku) return "Unknown";
    const uomId = (sku as any).uom_id;
    if (uomId) {
      const uom = uoms?.find(u => u.id === uomId);
      if (uom) return `${uom.unit_name} (${uom.short_name})`;
    }
    return "-";
  }

  return (
    <Dialog open={open} onOpenChange={(val) => {
      onOpenChange(val)
      if (!val) form.reset()
    }}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <div className="flex items-center justify-between pr-8">
            <div>
              <DialogTitle className="flex items-center gap-3">
                {bom ? "View Bill of Materials" : "Create Bill of Materials"}
                {bom?.status === 'ARCHIVED' && (
                  <Badge variant="secondary" className="bg-slate-200 text-slate-700">ARCHIVED</Badge>
                )}
              </DialogTitle>
              <DialogDescription className="mt-1">
                {bom ? "Viewing recipe and conversion ratio details." : "Define the recipe and conversion ratio for a finished good."}
              </DialogDescription>
            </div>
            
            {bom && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem disabled>
                    <Pencil className="h-4 w-4 mr-2 text-slate-500" />
                    Edit BOM
                  </DropdownMenuItem>
                  {bom.status === 'ARCHIVED' ? (
                    <DropdownMenuItem 
                      className="text-green-600 focus:text-green-700 cursor-pointer"
                      onClick={() => {
                        if (confirm('Are you sure you want to restore this BOM? It will become ACTIVE and available for Job Work Receipts.')) {
                          restoreMutation.mutate(bom.id)
                          onOpenChange(false)
                        }
                      }}
                    >
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Restore BOM
                    </DropdownMenuItem>
                  ) : (
                    <DropdownMenuItem 
                      className="text-rose-600 focus:text-rose-700 cursor-pointer"
                      onClick={() => {
                        if (confirm('Are you sure you want to archive this BOM? It will no longer be available for new Job Work Receipts.')) {
                          archiveMutation.mutate(bom.id)
                          onOpenChange(false)
                        }
                      }}
                    >
                      <Archive className="h-4 w-4 mr-2" />
                      Archive BOM
                    </DropdownMenuItem>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </DialogHeader>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="bom_number"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>BOM Number</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="status"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Status</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value} value={field.value} disabled={!!bom}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select Status" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="DRAFT">Draft</SelectItem>
                        <SelectItem value="ACTIVE">Active</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="target_item_id"
                render={({ field }) => (
                  <FormItem className="col-span-1">
                    <FormLabel>Target Item (Output)</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value} value={field.value} disabled={!!bom}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select Target SKU" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {finishedGoods.map(sku => (
                          <SelectItem key={sku.id} value={sku.id}>
                            {getSkuName(sku)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="target_quantity"
                render={({ field }) => (
                  <FormItem className="col-span-1">
                    <FormLabel>Base Quantity</FormLabel>
                    <FormControl>
                    <Input placeholder="e.g. BOM-001" {...field} disabled={!!bom} />
                  </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="bom_name"
                render={({ field }) => (
                  <FormItem className="col-span-2">
                    <FormLabel>BOM Name</FormLabel>
                    <FormControl>
                      <Input placeholder="e.g. Standard Recipe" {...field} disabled={!!bom} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium">Components & Ingredients</h4>
                    {!bom && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => append({ component_item_id: "", quantity: 1, wastage_percentage: 0 })}
                      >
                        <Plus className="h-4 w-4 mr-2" /> Add Component
                      </Button>
                    )}
                  </div>

              {fields.length === 0 ? (
                <div className="p-8 text-center text-sm text-slate-500 bg-slate-50 border rounded-md border-dashed">
                  No components added yet. Click "Add Component" to build the recipe.
                </div>
              ) : (
                <ScrollArea className="h-[250px] pr-4">
                  <div className="space-y-3">
                    {fields.map((field, index) => (
                      <div key={field.id} className="flex items-start gap-3 p-3 bg-slate-50 rounded-md border">
                        <div className="flex-1 space-y-3">
                          <FormField
                            control={form.control}
                            name={`items.${index}.component_item_id`}
                            render={({ field }) => (
                              <FormItem>
                                <Select onValueChange={field.onChange} defaultValue={field.value} value={field.value} disabled={!!bom}>
                                  <FormControl>
                                    <SelectTrigger>
                                      <SelectValue placeholder="Select raw material or consumable..." />
                                    </SelectTrigger>
                                  </FormControl>
                                  <SelectContent>
                                    <SelectGroup>
                                      <SelectLabel>Available Components</SelectLabel>
                                      {availableComponents.map(sku => (
                                        <SelectItem key={sku.id} value={sku.id}>
                                          {getSkuName(sku)} - {sku.product?.item_type}
                                        </SelectItem>
                                      ))}
                                    </SelectGroup>
                                  </SelectContent>
                                </Select>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                          
                          <div className="flex gap-3">
                            <FormField
                              control={form.control}
                              name={`items.${index}.quantity`}
                              render={({ field }) => (
                                <FormItem className="flex-1">
                                  <FormLabel className="text-xs text-slate-500 font-normal">Quantity</FormLabel>
                                  <FormControl>
                                    <Input type="number" step="0.01" placeholder="Qty" {...field} disabled={!!bom} />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            
                            <div className="flex-1 space-y-2">
                              <label className="text-xs text-slate-500 font-normal leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Unit of Measure</label>
                              <div className="h-10 px-3 py-2 border rounded-md bg-slate-100 text-sm text-slate-600 flex items-center">
                                {getSkuUOM(form.watch(`items.${index}.component_item_id`))}
                              </div>
                            </div>
                            
                            <FormField
                              control={form.control}
                              name={`items.${index}.wastage_percentage`}
                              render={({ field }) => (
                                <FormItem className="flex-1">
                                  <FormLabel className="text-xs text-slate-500 font-normal">Wastage %</FormLabel>
                                  <FormControl>
                                  <Input type="number" min="0" step="0.0001" {...field} disabled={!!bom} />
                                </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                          </div>
                        </div>
                                                {!bom && (
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="icon"
                                  className="h-10 w-10 text-rose-500 hover:text-rose-600 hover:bg-rose-50 mt-[32px]"
                                  onClick={() => remove(index)}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              )}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              )}
              {form.formState.errors.items?.root && (
                <p className="text-sm font-medium text-destructive">{form.formState.errors.items.root.message}</p>
              )}
            </div>

            <DialogFooter className="bg-slate-50 px-6 py-4 border-t rounded-b-lg">
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            {bom ? "Close" : "Cancel"}
          </Button>
          {!bom && (
            <Button type="button" className="bg-indigo-600 hover:bg-indigo-700" onClick={form.handleSubmit(onSubmit)} disabled={createMutation.isPending}>
              {createMutation.isPending ? "Saving..." : "Save BOM"}
            </Button>
          )}
        </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
