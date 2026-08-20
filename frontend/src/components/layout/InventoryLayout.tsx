// @ts-nocheck
import { Outlet, Link, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import { AlertTriangle, ArrowRightLeft, FileDown, LayoutDashboard, Package, Settings2 } from "lucide-react"
import { InventoryOthersDropdown } from "./InventoryOthersDropdown"
import { useAuth } from "@/hooks/use-auth"

const INVENTORY_NAV_ITEMS = [
  { name: "Dashboard", href: "/inventory", icon: LayoutDashboard, permission: "CATALOG_VIEW" },
  { name: "Catalog", href: "/inventory/catalog", icon: Package, permission: "CATALOG_VIEW" },
  { name: "Products", href: "/inventory/products", icon: Package, permission: "PRODUCT_VIEW" },
  { name: "Goods Receipts", href: "/inventory/goods-receipts", icon: FileDown, permission: "INVENTORY_RECEIPT_VIEW" },
  { name: "Job Worker Stock", href: "/inventory/job-worker-stock", icon: Package, permission: "INVENTORY_JOBWORK_VIEW" },
  { name: "Activity", href: "/inventory/activity", icon: ArrowRightLeft, permission: "INVENTORY_ACTIVITY_VIEW" },
  { name: "Exceptions", href: "/inventory/exceptions", icon: AlertTriangle, permission: "INVENTORY_EXCEPTION_VIEW" },
]

export function InventoryLayout() {
  const location = useLocation()
  const { hasPermission } = useAuth()

  return (
    <div className="flex h-full flex-col w-full relative">
      <div className="border-b border-slate-200 bg-white px-6 py-3 shrink-0 sticky top-0 z-10 w-full">
        <nav className="flex space-x-1 overflow-x-auto no-scrollbar">
          {INVENTORY_NAV_ITEMS.filter(item => !item.permission || hasPermission(item.permission)).map((item) => {
            // Determine active state
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
          
          {/* Append the Others dropdown */}
          <InventoryOthersDropdown />
        </nav>
      </div>
      <div className="flex-1 overflow-y-auto bg-slate-50 p-6">
        <Outlet />
      </div>
    </div>
  )
}
