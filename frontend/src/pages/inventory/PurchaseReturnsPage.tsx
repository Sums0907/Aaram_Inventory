import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

export function PurchaseReturnsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Purchase Returns</h1>
          <p className="text-sm text-slate-500">
            Record outbound inventory movements for supplier returns.
          </p>
        </div>
        <div className="flex gap-2">
          <Button className="bg-indigo-600 hover:bg-indigo-700">
            <Plus className="mr-2 h-4 w-4" />
            Create Return
          </Button>
        </div>
      </div>
      
      <div className="rounded-md border bg-white p-8 text-center text-slate-500">
        Purchase Returns management UI coming soon.
      </div>
    </div>
  )
}
