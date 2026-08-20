import { Link, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import { MoreHorizontal, Users, Settings2, FileUp, ClipboardCheck, ArrowRightLeft } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useAuth } from "@/hooks/use-auth"

const OTHERS_NAV_ITEMS = [
  { name: "Suppliers", href: "/inventory/suppliers", icon: Users, permission: "CATALOG_VIEW" },
  { name: "BOMs", href: "/inventory/boms", icon: Settings2, permission: "PRODUCT_VIEW" },
  { name: "UOMs", href: "/inventory/units-of-measure", icon: Settings2, permission: "CATALOG_VIEW" },
  { name: "Purchase Returns", href: "/inventory/purchase-returns", icon: FileUp, permission: "INVENTORY_RETURN_CREATE" },
  { name: "Verification", href: "/inventory/verification", icon: ClipboardCheck, permission: "INVENTORY_VERIFICATION_EXECUTE" },
  { name: "Adjustments", href: "/inventory/adjustments", icon: Settings2, permission: "INVENTORY_ADJUSTMENT_CREATE" },
  { name: "Transformations", href: "/inventory/transformations", icon: ArrowRightLeft, permission: "INVENTORY_TRANSFORMATION_CREATE" },
]

export function InventoryOthersDropdown() {
  const location = useLocation()
  const { hasPermission } = useAuth()
  
  const filteredItems = OTHERS_NAV_ITEMS.filter(item => !item.permission || hasPermission(item.permission))
  
  // Check if any of the "Others" items are currently active
  const isAnyActive = filteredItems.some(item => location.pathname === item.href)
  
  if (filteredItems.length === 0) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className={cn(
            "flex items-center whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition-colors outline-none",
            isAnyActive
              ? "bg-indigo-50 text-indigo-700"
              : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
          )}
        >
          <MoreHorizontal
            className={cn(
              "mr-2 h-4 w-4",
              isAnyActive ? "text-indigo-600" : "text-slate-400"
            )}
          />
          Others
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {filteredItems.map((item) => {
          const isActive = location.pathname === item.href
          const Icon = item.icon
          
          return (
            <DropdownMenuItem key={item.name} asChild>
              <Link 
                to={item.href} 
                className={cn(
                  "w-full cursor-pointer",
                  isActive ? "bg-indigo-50/50 font-medium text-indigo-700" : ""
                )}
              >
                <Icon className={cn("mr-2 h-4 w-4", isActive ? "text-indigo-600" : "text-slate-500")} />
                <span>{item.name}</span>
              </Link>
            </DropdownMenuItem>
          )
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
