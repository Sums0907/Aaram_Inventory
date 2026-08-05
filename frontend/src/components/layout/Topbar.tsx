import { RefreshCw, Bell, User } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Topbar() {
  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b bg-white px-6">
      <div className="flex items-center gap-4">
        <div className="text-sm text-slate-500">
          Accounting Period: <span className="font-semibold text-slate-900">October 2023</span>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" className="gap-2 border-indigo-200 text-indigo-700 hover:bg-indigo-50 hover:text-indigo-800">
          <RefreshCw className="h-4 w-4" />
          Sync ShopDeck
        </Button>
        
        <div className="flex items-center gap-2 border-l pl-4 ml-2">
          <Button variant="ghost" size="icon" className="text-slate-500 rounded-full">
            <Bell className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" className="text-slate-500 rounded-full bg-slate-100">
            <User className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  )
}
