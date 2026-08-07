import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { PlusCircle, MinusCircle, BookOpen, Truck } from "lucide-react"
import { ManualAdjustmentDialog, type AdjustmentType } from "./ManualAdjustmentDialog"
import { GRNFormDialog } from "@/components/inbound/GRNFormDialog"

interface QuickInventoryActionCardProps {
  skuId: string
  currentStock: number
  itemType?: string
  onViewLedger: () => void
}

export function QuickInventoryActionCard({ skuId, currentStock, itemType = "FINISHED_GOODS", onViewLedger }: QuickInventoryActionCardProps) {
  const [adjustmentType, setAdjustmentType] = useState<AdjustmentType>("increase")
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isGrnDialogOpen, setIsGrnDialogOpen] = useState(false)

  const handleOpenDialog = (type: AdjustmentType) => {
    setAdjustmentType(type)
    setIsDialogOpen(true)
  }

  return (
    <>
      <Card className="border-slate-200 shadow-sm bg-white overflow-hidden">
        <div className="p-6 bg-slate-50/50 flex flex-col items-center justify-center border-b">
          <span className="text-sm font-medium text-slate-500 uppercase tracking-wider mb-2">Current Stock</span>
          <span className={`text-4xl font-bold ${currentStock > 0 ? 'text-indigo-600' : currentStock < 0 ? 'text-rose-600' : 'text-slate-700'}`}>
            {currentStock} <span className="text-lg font-medium text-slate-400">Units</span>
          </span>
        </div>
        <CardContent className="p-6">
          <h3 className="text-sm font-medium text-slate-700 uppercase tracking-wider mb-4 text-center">Quick Actions</h3>
          
          <div className="flex flex-col gap-3">
            <Button 
              variant="outline" 
              className="w-full justify-start text-indigo-700 border-indigo-200 bg-indigo-50 hover:bg-indigo-100 hover:text-indigo-800"
              onClick={(e) => { e.preventDefault(); e.stopPropagation(); setIsGrnDialogOpen(true); }}
            >
              <Truck className="mr-2 h-4 w-4" />
              Receive Goods (GRN)
            </Button>
            
            <div className="my-1 border-t border-slate-100"></div>
            
            {(itemType === "CONSUMABLE" || itemType === "PACKAGING_MATERIAL") && (
              <Button 
                variant="outline" 
                className="w-full justify-start text-amber-700 border-amber-200 bg-amber-50 hover:bg-amber-100 hover:text-amber-800"
                onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleOpenDialog("decrease"); }}
              >
                <MinusCircle className="mr-2 h-4 w-4" />
                Consume
              </Button>
            )}

            <Button 
              variant="outline" 
              className="w-full justify-start text-slate-600 border-slate-200 bg-white hover:bg-slate-50"
              onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleOpenDialog("increase"); }}
            >
              <PlusCircle className="mr-2 h-4 w-4" />
              Increase Stock
            </Button>
            
            <Button 
              variant="outline" 
              className="w-full justify-start text-slate-600 border-slate-200 bg-white hover:bg-slate-50"
              onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleOpenDialog("decrease"); }}
            >
              <MinusCircle className="mr-2 h-4 w-4" />
              {itemType === "CONSUMABLE" || itemType === "PACKAGING_MATERIAL" ? "Reduce Stock (Manual)" : "Reduce Stock"}
            </Button>

            <div className="my-1 border-t border-slate-100"></div>

            <Button 
              variant="ghost" 
              className="w-full justify-start text-slate-600 hover:text-indigo-600 hover:bg-indigo-50"
              onClick={onViewLedger}
            >
              <BookOpen className="mr-2 h-4 w-4" />
              View Inventory Ledger
            </Button>
          </div>
        </CardContent>
      </Card>

      <ManualAdjustmentDialog
        skuId={skuId}
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        type={adjustmentType}
      />
      
      <GRNFormDialog
        open={isGrnDialogOpen}
        onOpenChange={setIsGrnDialogOpen}
        defaultSkuId={skuId}
      />
    </>
  )
}
