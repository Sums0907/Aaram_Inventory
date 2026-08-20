// @ts-nocheck
import { Card, CardContent } from "@/components/ui/card"
import type { SKUResponse } from "@/api/masters"
import { Package, IndianRupee, AlertTriangle, ShieldCheck, XCircle, Grid } from "lucide-react"

interface ExecutiveSummaryProps {
  skus: SKUResponse[]
  balances: any[] // using any for balance type to avoid tight coupling if types change
}

export function ExecutiveSummary({ skus, balances }: ExecutiveSummaryProps) {
  const totalProducts = skus.length
  
  const categories = new Set(skus.map(s => s.product?.product_type).filter(Boolean))
  const totalCategories = categories.size

  // Calculate Inventory Value
  let inventoryValue = 0
  let lowStockCount = 0
  let outOfStockCount = 0

  skus.forEach(sku => {
    const b = balances?.find(b => b.sku_id === sku.id)
    const stock = b ? b.balance : 0
    
    if (stock <= 0) {
      outOfStockCount++
    } else if (stock < 10) {
      lowStockCount++ // Arbitrary threshold for "low stock" for now
    }

    if (stock > 0 && sku.pricing?.cost_price) {
      inventoryValue += stock * sku.pricing.cost_price
    }
  })

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      <Card className="shadow-sm border-slate-200">
        <CardContent className="p-4 flex flex-col justify-center items-center text-center">
          <Package className="h-5 w-5 text-indigo-500 mb-2" />
          <p className="text-2xl font-bold text-slate-900">{totalProducts}</p>
          <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mt-1">Products</p>
        </CardContent>
      </Card>
      
      <Card className="shadow-sm border-slate-200">
        <CardContent className="p-4 flex flex-col justify-center items-center text-center">
          <Grid className="h-5 w-5 text-indigo-500 mb-2" />
          <p className="text-2xl font-bold text-slate-900">{totalCategories}</p>
          <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mt-1">Categories</p>
        </CardContent>
      </Card>

      <Card className="shadow-sm border-slate-200 lg:col-span-2">
        <CardContent className="p-4 flex flex-col justify-center items-center text-center bg-indigo-50/50">
          <IndianRupee className="h-5 w-5 text-emerald-600 mb-2" />
          <p className="text-2xl font-bold text-slate-900">
            ₹{inventoryValue.toLocaleString('en-IN')}
          </p>
          <p className="text-xs text-slate-600 uppercase tracking-wider font-medium mt-1">Inventory Value</p>
        </CardContent>
      </Card>

      <Card className="shadow-sm border-slate-200">
        <CardContent className="p-4 flex flex-col justify-center items-center text-center">
          <AlertTriangle className="h-5 w-5 text-amber-500 mb-2" />
          <p className="text-2xl font-bold text-slate-900">{lowStockCount}</p>
          <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mt-1">Low Stock</p>
        </CardContent>
      </Card>

      <Card className="shadow-sm border-slate-200">
        <CardContent className="p-4 flex flex-col justify-center items-center text-center">
          <XCircle className="h-5 w-5 text-rose-500 mb-2" />
          <p className="text-2xl font-bold text-slate-900">{outOfStockCount}</p>
          <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mt-1">Out of Stock</p>
        </CardContent>
      </Card>
    </div>
  )
}
