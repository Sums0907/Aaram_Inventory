import { Outlet, Link, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import { 
  LayoutDashboard, 
  Wallet,
  Users,
  Settings2,
  BookOpen
} from "lucide-react"

const ACCOUNTING_NAV_ITEMS = [
  { name: "Dashboard", href: "/accounting", icon: LayoutDashboard },
  // { name: "Sales", href: "/accounting/sales", icon: Wallet },
  // { name: "Expenses", href: "/accounting/expenses", icon: Wallet },
  // { name: "Bank / Cash", href: "/accounting/bank", icon: Wallet },
  // { name: "Ledgers", href: "/accounting/ledgers", icon: BookOpen },
]

const JW_ACCOUNTING_NAV_ITEMS = [
  { name: "JW Dashboard", href: "/accounting/job-worker/dashboard", icon: LayoutDashboard },
  { name: "JW Payables", href: "/accounting/job-worker/payables", icon: Users },
  { name: "JW Rates", href: "/accounting/job-worker/rates", icon: Settings2 },
]

export function AccountingLayout() {
  const location = useLocation()

  return (
    <div className="flex h-full flex-col w-full relative">
      <div className="border-b border-slate-200 bg-white px-6 py-3 shrink-0 sticky top-0 z-10 w-full flex items-center justify-between">
        <nav className="flex space-x-1 overflow-x-auto no-scrollbar">
          {ACCOUNTING_NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                )}
              >
                <Icon
                  className={cn(
                    "mr-2 h-4 w-4",
                    isActive ? "text-indigo-600" : "text-slate-400"
                  )}
                />
                {item.name}
              </Link>
            )
          })}
          
          <div className="w-px h-6 bg-slate-200 mx-2 self-center"></div>
          
          {JW_ACCOUNTING_NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                )}
              >
                <Icon
                  className={cn(
                    "mr-2 h-4 w-4",
                    isActive ? "text-indigo-600" : "text-slate-400"
                  )}
                />
                {item.name}
              </Link>
            )
          })}
        </nav>
      </div>
      <div className="flex-1 overflow-y-auto bg-slate-50 p-6">
        <Outlet />
      </div>
    </div>
  )
}
