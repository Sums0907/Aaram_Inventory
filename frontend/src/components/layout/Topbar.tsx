import { Link, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import { 
  RefreshCw, 
  Bell, 
  User, 
  LayoutDashboard, 
  Download, 
  ArrowLeftRight, 
  Package, 
  BookOpen, 
  FileOutput, 
  Settings 
} from "lucide-react"
import { Button } from "@/components/ui/button"

const GLOBAL_NAV_ITEMS = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Imports", href: "/imports", icon: Download },
  { name: "Matching", href: "/matching", icon: ArrowLeftRight },
  { name: "Inventory", href: "/inventory", icon: Package },
  { name: "Accounting", href: "/accounting", icon: BookOpen },
  { name: "Exports", href: "/exports", icon: FileOutput },
  { name: "Settings", href: "/settings", icon: Settings },
]

export function Topbar() {
  const location = useLocation()

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b bg-slate-950 text-slate-50 px-6 sticky top-0 z-50">
      <div className="flex items-center gap-8 h-full">
        {/* Brand Logo */}
        <Link to="/" className="text-lg font-bold tracking-tight text-white flex items-center gap-2 shrink-0">
          <div className="size-5 bg-indigo-500 rounded flex items-center justify-center">
             <div className="size-2 bg-white rounded-sm"></div>
          </div>
          AaramBooks
        </Link>
        
        {/* Level 1 Application Navigation */}
        <nav className="hidden md:flex space-x-1 h-full items-center">
          {GLOBAL_NAV_ITEMS.map((item) => {
            // Check if current path starts with item.href (but handle "/" specifically)
            const isActive = item.href === "/" 
              ? location.pathname === "/"
              : location.pathname.startsWith(item.href)

            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center rounded-md px-3 py-2 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-indigo-500/15 text-indigo-300 font-semibold shadow-inner"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                )}
              >
                {isActive && (
                   <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mr-2 shrink-0 animate-pulse"></span>
                )}
                {item.name}
              </Link>
            )
          })}
        </nav>
      </div>
      
      {/* Global Actions */}
      <div className="flex items-center gap-4 shrink-0">
        <Button variant="outline" size="sm" className="gap-2 border-slate-700 bg-slate-900 text-slate-300 hover:bg-slate-800 hover:text-white">
          <RefreshCw className="h-4 w-4" />
          Sync ShopDeck
        </Button>
        
        <div className="flex items-center gap-2 border-l border-slate-800 pl-4 ml-2">
          <Button variant="ghost" size="icon" className="text-slate-400 hover:bg-slate-800 hover:text-white rounded-full">
            <Bell className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" className="text-slate-400 hover:bg-slate-800 hover:text-white rounded-full">
            <User className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  )
}
