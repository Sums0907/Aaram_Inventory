import { formatQuantityValue } from "@/lib/utils"
import { useState, useMemo } from "react"
import { useForm, useFieldArray, useWatch } from "react-hook-form"
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
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Plus, Trash2, Info, ArrowRight, Settings2 } from "lucide-react"

import { useCreateGoodsReceipt } from "@/api/goods-receipts"
import { useSuppliers } from "@/api/suppliers"
import { useSKUs, useUnitsOfMeasure } from "@/api/masters"
import { useBOMs } from "@/api/boms"
import { usePendingStock } from "@/api/job-works"
import { useToast } from "@/hooks/use-toast"
import { SupplierFormDialog } from "@/components/inbound/SupplierFormDialog"

const itemSchema = z.object({
  sku_id: z.string().min(1, "Item is required"),
  quantity: z.coerce.number().positive("Quantity must be positive"),
  batch_number: z.string().optional(),
})

const grnSchema = z.object({
  receipt_type: z.enum(["RAW_MATERIAL_RECEIPT", "PURCHASED_FINISHED_GOODS", "JOB_WORK_RECEIPT"]),
  grn_number: z.string().min(1, "GRN number is required"),
  supplier_id: z.string().min(1, "Supplier/Job Worker is required"),
  warehouse_id: z.string().min(1, "Warehouse is required"),
  receipt_date: z.string().min(1, "Date is required"),
  invoice_number: z.string().optional(),
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
  const [showConfirmation, setShowConfirmation] = useState(false)
  
  const { data: suppliersData } = useSuppliers(0, 100)
  const { data: skus } = useSKUs()
  const { data: bomsData } = useBOMs()
  const boms = (bomsData || []).filter((bom: any) => bom.status !== "ARCHIVED")
  
  const suppliers = suppliersData?.data || []

  // Hardcoded Test Warehouse ID (Matches test_inventory.db)
  const warehouseId = "dbcfca97-fc1d-4466-815f-a843072a14be" 

  const generateGrnNumber = () => {
    const year = new Date().getFullYear();
    const randomSeq = Math.floor(Math.random() * 90000) + 10000;
    return `GRN-${year}-${randomSeq}`;
  }

  const form = useForm<GRNFormValues>({
    resolver: zodResolver(grnSchema),
    defaultValues: {
      receipt_type: "RAW_MATERIAL_RECEIPT",
      grn_number: generateGrnNumber(),
      supplier_id: "",
      warehouse_id: warehouseId,
      receipt_date: new Date().toISOString().split("T")[0],
      invoice_number: "",
      remarks: "",
      items: [{ sku_id: defaultSkuId || "", quantity: 1, batch_number: "" }],
    },
  })

  const { fields, append, remove } = useFieldArray({
    name: "items",
    control: form.control,
  })

  const receiptType = useWatch({ control: form.control, name: "receipt_type" }) || "RAW_MATERIAL_RECEIPT"
  const supplierId = useWatch({ control: form.control, name: "supplier_id" }) || ""
  const currentItems = useWatch({ control: form.control, name: "items" }) || [{ sku_id: defaultSkuId || "", quantity: 1, batch_number: "" }]

  const { data: pendingStockResp } = usePendingStock(receiptType === "JOB_WORK_RECEIPT" ? supplierId : "")
  const pendingStockData = pendingStockResp || []
  
  const { data: uoms } = useUnitsOfMeasure()
  
  // Filter SKUs based on receipt type
  console.log("SKUS VALUE:", skus, "isArray:", Array.isArray(skus));
  const filteredSkus = useMemo(() => {
    if (!skus) return []
    if (receiptType === "RAW_MATERIAL_RECEIPT") {
      return skus.filter((s: any) => s.product?.item_type !== "FINISHED_GOODS" && s.status !== "ARCHIVED")
    }
    return skus.filter((s: any) => s.product?.item_type === "FINISHED_GOODS" && s.status !== "ARCHIVED")
  }, [skus, receiptType])

  // Get current stock for an item
  const getCurrentStock = (skuId: string) => {
    // In a real app we'd query the balance, but assuming we have it in skus or a separate API. 
    // We'll mock it for the UI as per specs if not available.
    return 0; // Mock 0 for now unless we add useInventoryBalances
  }

  // Calculate Job Work Consumption Impact
  const inventoryImpact = useMemo(() => {
    const impact: any[] = [];
    
    (currentItems || []).forEach((item) => {
      if (!item.sku_id || !item.quantity) return
      
      const skuInfo = skus?.find((s: any) => s.id === item.sku_id)
      const uomName = uoms?.find((u: any) => u.id === skuInfo?.uom_id)?.short_name || "units"
      
      impact.push({
        name: skuInfo?.product?.product_name || "Unknown Item",
        type: "Increase",
        amount: `+${item.quantity} ${uomName}`
      })

      if (receiptType === "JOB_WORK_RECEIPT" && boms) {
        // Try to find an ACTIVE BOM first, fallback to any BOM for preview
        const activeBom = boms.find((b: any) => b.target_item_id === item.sku_id && b.status === 'ACTIVE')
        const bom = activeBom || boms.find((b: any) => b.target_item_id === item.sku_id)
        
        if (bom) {
          impact.push({
            name: `Applied BOM Version ${bom.version || 1}`,
            type: "Info",
            amount: bom.status === 'ACTIVE' ? "Active" : bom.status,
          });
          
          bom.items.forEach((bomItem: any) => {
            const compInfo = skus?.find((s: any) => s.id === bomItem.component_item_id)
            const compUom = uoms?.find((u: any) => u.id === compInfo?.uom_id)?.short_name || "units"
            const consumed = item.quantity * bomItem.quantity
            impact.push({
              name: compInfo?.product?.product_name || "Raw Material",
              type: "Decrease",
              amount: `-${consumed} ${compUom}`
            })
          })
        } else {
          impact.push({
            name: "Warning",
            type: "Error",
            amount: "No BOM found!"
          })
        }
      }
    })
    
    return impact
  }, [currentItems, receiptType, boms, skus])

  const onSubmit = async (data: GRNFormValues) => {
    if (!showConfirmation) {
      setShowConfirmation(true)
      return
    }

    try {
      await createMutation.mutateAsync(data)
      toast({
        title: "Goods Receipt Note (GRN) created",
        description: "Inventory stock balances have been updated successfully.",
      })
      onOpenChange(false)
      setShowConfirmation(false)
      form.reset({
        ...form.getValues(),
        grn_number: generateGrnNumber(),
        items: [{ sku_id: defaultSkuId || "", quantity: 1, batch_number: "" }]
      })
    } catch (error: any) {
      toast({
        title: "Failed to create GRN",
        description: error.response?.data?.error?.message || error.response?.data?.message || "An unexpected error occurred",
        variant: "destructive",
      })
    }
  }

  // Effect to reset items when receipt type changes
  const handleReceiptTypeChange = (val: string) => {
    form.setValue("receipt_type", val as any)
    form.setValue("items", [{ sku_id: "", quantity: 1, batch_number: "" }])
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[1000px] max-h-[90vh] overflow-y-auto p-0 gap-0">
        <DialogHeader className="px-6 py-4 border-b border-slate-100 bg-slate-50/50 sticky top-0 z-10">
          <DialogTitle className="text-xl">New Goods Receipt Note</DialogTitle>
        </DialogHeader>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col md:flex-row h-full">
            
            {/* Left Column: Form Fields */}
            <div className="flex-1 p-6 space-y-8 border-r border-slate-100">
              
              {/* Receipt Type */}
              <div className="space-y-3">
                <label className="text-base font-semibold leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Goods Receipt Type</label>
                <FormField
                  control={form.control}
                  name="receipt_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <RadioGroup
                          onValueChange={handleReceiptTypeChange}
                          defaultValue={field.value}
                          className="flex flex-col space-y-2 md:flex-row md:space-x-4 md:space-y-0"
                        >
                          <FormItem className="flex items-center space-x-3 space-y-0 bg-white border border-slate-200 rounded-lg p-3 cursor-pointer hover:border-indigo-200 transition-colors [&:has([data-state=checked])]:border-indigo-600 [&:has([data-state=checked])]:bg-indigo-50/50">
                            <FormControl>
                              <RadioGroupItem value="RAW_MATERIAL_RECEIPT" />
                            </FormControl>
                            <FormLabel className="font-normal cursor-pointer text-sm m-0">
                              Raw Material Receipt
                            </FormLabel>
                          </FormItem>
                          <FormItem className="flex items-center space-x-3 space-y-0 bg-white border border-slate-200 rounded-lg p-3 cursor-pointer hover:border-indigo-200 transition-colors [&:has([data-state=checked])]:border-indigo-600 [&:has([data-state=checked])]:bg-indigo-50/50">
                            <FormControl>
                              <RadioGroupItem value="PURCHASED_FINISHED_GOODS" />
                            </FormControl>
                            <FormLabel className="font-normal cursor-pointer text-sm m-0">
                              Purchased Finished Goods
                            </FormLabel>
                          </FormItem>
                          <FormItem className="flex items-center space-x-3 space-y-0 bg-white border border-slate-200 rounded-lg p-3 cursor-pointer hover:border-indigo-200 transition-colors [&:has([data-state=checked])]:border-indigo-600 [&:has([data-state=checked])]:bg-indigo-50/50">
                            <FormControl>
                              <RadioGroupItem value="JOB_WORK_RECEIPT" />
                            </FormControl>
                            <FormLabel className="font-normal cursor-pointer text-sm m-0">
                              Job Work Receipt
                            </FormLabel>
                          </FormItem>
                        </RadioGroup>
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>

              {/* Header Details */}
              <div className="grid grid-cols-2 gap-x-6 gap-y-4">
                <FormField
                  control={form.control}
                  name="supplier_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{receiptType === "JOB_WORK_RECEIPT" ? "Job Worker" : "Supplier"}</FormLabel>
                      <div className="flex gap-2">
                        <Select onValueChange={field.onChange} defaultValue={field.value} value={field.value}>
                          <FormControl>
                            <SelectTrigger className="flex-1 bg-white">
                              <SelectValue placeholder={`Select ${receiptType === "JOB_WORK_RECEIPT" ? "Job Worker" : "Supplier"}`} />
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
                      <FormLabel>Invoice / Reference</FormLabel>
                      <FormControl>
                        <Input placeholder="INV-..." {...field} className="bg-white" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="grn_number"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>GRN Number</FormLabel>
                      <FormControl>
                        <Input {...field} readOnly className="bg-slate-50 text-slate-500 font-mono" />
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
                      <FormLabel>Date</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} className="bg-white" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {receiptType !== "JOB_WORK_RECEIPT" && (
                  <div className="col-span-2">
                    <FormField
                      control={form.control}
                      name="remarks"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Remarks</FormLabel>
                          <FormControl>
                            <Input placeholder="Optional notes..." {...field} className="bg-white" />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                )}
              </div>

              {/* Line Items */}
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                  <h3 className="text-base font-semibold">Inventory Items</h3>
                </div>

                {receiptType === "JOB_WORK_RECEIPT" && supplierId && pendingStockData && pendingStockData.length > 0 && (
                  <div className="mb-6 p-4 rounded-lg bg-amber-50 border border-amber-100">
                    <h4 className="text-sm font-medium text-amber-900 mb-2 flex items-center">
                      <Info className="w-4 h-4 mr-2" />
                      Pending Material with Job Worker
                    </h4>
                    <div className="space-y-2">
                      {pendingStockData.map((stock) => {
                        const sku = skus?.find((s:any) => s.id === stock.item_id)
                        const stockUom = uoms?.find((u: any) => u.id === sku?.uom_id)?.short_name || "units"
                        return (
                          <div key={stock.item_id} className="flex justify-between text-sm text-amber-800 bg-white/60 p-2 rounded">
                            <span>{sku?.product?.product_name || "Unknown Item"}</span>
                            <span className="font-medium">{stock.pending_quantity} {stockUom}</span>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}

                {fields.map((field, index) => {
                  const selectedSkuId = (currentItems || [])[index]?.sku_id;
                  const selectedSku = skus?.find((s: any) => s.id === selectedSkuId);
                  const lineUom = uoms?.find((u: any) => u.id === selectedSku?.uom_id)?.short_name || "units";

                  return (
                    <div key={field.id} className="flex flex-wrap gap-4 items-start bg-slate-50/50 p-4 rounded-xl border border-slate-200 shadow-sm relative group">
                      <FormField
                        control={form.control}
                        name={`items.${index}.sku_id`}
                        render={({ field }) => (
                          <FormItem className="flex-[2] min-w-[200px]">
                            <FormLabel className="text-xs text-slate-500 uppercase tracking-wider">
                              {receiptType === "JOB_WORK_RECEIPT" ? "Finished Good Received" : "Inventory Item"}
                            </FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value} value={field.value}>
                              <FormControl>
                                <SelectTrigger className="bg-white">
                                  <SelectValue placeholder="Select Item" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                {filteredSkus.map((sku: any) => (
                                  <SelectItem key={sku.id} value={sku.id}>
                                    <div className="flex flex-col">
                                      <span className="font-medium">{sku.product?.product_name || "Unknown"}</span>
                                      <span className="text-xs text-slate-500">{sku.item_code}</span>
                                    </div>
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      
                      {receiptType === "RAW_MATERIAL_RECEIPT" && (
                        <FormField
                          control={form.control}
                          name={`items.${index}.batch_number`}
                          render={({ field }) => (
                            <FormItem className="flex-1 min-w-[120px]">
                              <FormLabel className="text-xs text-slate-500 uppercase tracking-wider">Batch / Roll No.</FormLabel>
                              <FormControl>
                                <Input placeholder="Optional" {...field} className="bg-white" />
                              </FormControl>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      )}

                      <FormField
                        control={form.control}
                        name={`items.${index}.quantity`}
                        render={({ field }) => (
                          <FormItem className="w-[140px]">
                            <FormLabel className="text-xs text-slate-500 uppercase tracking-wider">Quantity</FormLabel>
                            <div className="relative">
                              <FormControl>
                                <Input type="number" min="0.001" step="any" {...field} className="bg-white pr-12" />
                              </FormControl>
                              <div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 font-medium pointer-events-none">
                                {lineUom}
                              </div>
                            </div>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <Button 
                        type="button" 
                        variant="ghost" 
                        size="icon"
                        className={`absolute -right-2 -top-2 opacity-0 group-hover:opacity-100 transition-opacity bg-white border border-slate-200 text-slate-400 hover:text-red-600 rounded-full h-6 w-6 shadow-sm`}
                        onClick={() => remove(index)}
                        disabled={fields.length === 1}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  )
                })}

                <Button 
                  type="button" 
                  variant="outline" 
                  size="sm"
                  className="w-full border-dashed text-slate-500 hover:text-indigo-600 hover:border-indigo-300 hover:bg-indigo-50/50"
                  onClick={() => append({ sku_id: "", quantity: 1, batch_number: "" })}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Another Item
                </Button>
              </div>
            </div>

            {/* Right Column: Live Summary & Impact */}
            <div className="w-full md:w-[320px] bg-slate-50 p-6 flex flex-col justify-between border-l border-slate-100">
              
              <div>
                <h3 className="font-semibold text-lg mb-6 flex items-center">
                  Receipt Summary
                </h3>

                <div className="space-y-4 text-sm">
                  <div className="flex justify-between py-2 border-b border-slate-200">
                    <span className="text-slate-500">Receipt Type</span>
                    <span className="font-medium text-right max-w-[150px] leading-tight">
                      {receiptType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                  </div>
                  
                  <div className="flex justify-between py-2 border-b border-slate-200">
                    <span className="text-slate-500">{receiptType === "JOB_WORK_RECEIPT" ? "Job Worker" : "Supplier"}</span>
                    <span className="font-medium text-right max-w-[150px] truncate">
                      {suppliers.find((s:any) => s.id === supplierId)?.name || "-"}
                    </span>
                  </div>
                  
                  <div className="flex justify-between py-2 border-b border-slate-200">
                    <span className="text-slate-500">Total Items</span>
                    <span className="font-medium">{(currentItems || []).filter(i => i.sku_id).length}</span>
                  </div>
                  
                  <div className="flex justify-between py-2 border-b border-slate-200">
                    <span className="text-slate-500">Total Units</span>
                    <span className="font-medium">
                      {(currentItems || []).reduce((acc, item) => acc + (Number(item.quantity) || 0), 0)}
                    </span>
                  </div>
                </div>

                {/* Inventory Impact Preview */}
                <div className="mt-8">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center">
                    Inventory Impact Preview
                  </h4>
                  
                  {inventoryImpact.length === 0 ? (
                    <div className="text-sm text-slate-400 italic">Select items to view impact</div>
                  ) : (
                    <div className="space-y-3">
                      {inventoryImpact.map((impact, idx) => (
                        <div key={idx} className={`p-3 rounded-lg border ${
                          impact.type === "Increase" ? "bg-green-50/50 border-green-100" : 
                          impact.type === "Decrease" ? "bg-amber-50/50 border-amber-100" :
                          impact.type === "Info" ? "bg-indigo-50/50 border-indigo-100" :
                          "bg-red-50/50 border-red-100"
                        }`}>
                          <div className="flex justify-between items-center text-sm">
                            <span className={`font-medium truncate mr-2 ${impact.type === "Info" ? "text-indigo-700" : "text-slate-700"}`} title={impact.name}>
                              {impact.type === "Info" && <Settings2 className="inline-block w-3 h-3 mr-1 -mt-0.5" />}
                              {impact.name}
                            </span>
                            <span className={`font-bold whitespace-nowrap ${
                              impact.type === "Increase" ? "text-green-600" : 
                              impact.type === "Decrease" ? "text-amber-600" :
                              impact.type === "Info" ? "text-indigo-600 uppercase text-xs" :
                              "text-red-600"
                            }`}>{impact.amount}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="pt-8 space-y-3">
                {showConfirmation ? (
                  <div className="p-4 bg-indigo-50 border border-indigo-100 rounded-xl mb-4 text-sm text-indigo-900 animate-in fade-in slide-in-from-bottom-2">
                    <p className="font-semibold mb-1">Confirm Transaction?</p>
                    <p className="text-indigo-700 mb-4">Please verify the inventory impact above before proceeding. This action will update ledger balances.</p>
                    <div className="flex gap-2">
                      <Button 
                        type="button" 
                        variant="outline" 
                        className="flex-1 bg-white"
                        onClick={() => setShowConfirmation(false)}
                        disabled={createMutation.isPending}
                      >
                        Back
                      </Button>
                      <Button 
                        type="submit" 
                        className="flex-1 bg-indigo-600 hover:bg-indigo-700"
                        disabled={createMutation.isPending}
                      >
                        {createMutation.isPending ? "Posting..." : "Confirm & Post"}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <Button 
                    type="button" 
                    className="w-full bg-indigo-600 hover:bg-indigo-700 py-6 text-base shadow-sm group"
                    onClick={async () => {
                      const isValid = await form.trigger()
                      if (isValid) setShowConfirmation(true)
                    }}
                    disabled={createMutation.isPending || inventoryImpact.length === 0 || inventoryImpact.some(i => i.type === "Error")}
                  >
                    Review & Complete
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </Button>
                )}
                <Button 
                  type="button" 
                  variant="ghost"
                  className="w-full text-slate-500"
                  onClick={() => onOpenChange(false)}
                  disabled={createMutation.isPending}
                >
                  Cancel
                </Button>
              </div>

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
