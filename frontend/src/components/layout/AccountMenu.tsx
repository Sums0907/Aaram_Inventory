// @ts-nocheck
import { Link } from "react-router-dom"
import { useAuth } from "@/hooks/use-auth"
import { User, Settings, Database, ArrowLeftRight, Download, FileOutput, LogOut } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"

export function AccountMenu() {
  const { user, hasPermission, logout } = useAuth()
  
  const canSeeMasterData = 
    hasPermission("MASTER_DATA_IMPORT") || 
    hasPermission("MASTER_DATA_EXPORT") || 
    hasPermission("MASTER_DATA_ACTIVITY_VIEW")

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="text-slate-400 hover:bg-slate-800 hover:text-white rounded-full">
          <User className="h-5 w-5" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="end" forceMount>
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">{user?.name || "Unknown User"}</p>
            <p className="text-xs leading-none text-muted-foreground">
              Role: <span className="font-semibold uppercase">{user?.roles?.join(', ') || "User"}</span>
            </p>
          </div>
        </DropdownMenuLabel>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuGroup>
          <DropdownMenuItem disabled>
            <User className="mr-2 h-4 w-4" />
            <span>Account Settings</span>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link to="/settings" className="w-full cursor-pointer">
              <Settings className="mr-2 h-4 w-4" />
              <span>System Settings</span>
            </Link>
          </DropdownMenuItem>
        </DropdownMenuGroup>
        
        {canSeeMasterData && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <Link to="/admin/master-data" className="w-full cursor-pointer">
                <Database className="mr-2 h-4 w-4" />
                <span>Master Data Operations</span>
              </Link>
            </DropdownMenuItem>
          </>
        )}
        
        <DropdownMenuSeparator />
        
        <DropdownMenuSub>
          <DropdownMenuSubTrigger>
            <span>Upcoming Modules</span>
          </DropdownMenuSubTrigger>
          <DropdownMenuSubContent>
            <DropdownMenuItem asChild>
              <Link to="/matching" className="w-full cursor-pointer">
                <ArrowLeftRight className="mr-2 h-4 w-4" />
                <span>Matching</span>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link to="/imports" className="w-full cursor-pointer">
                <Download className="mr-2 h-4 w-4" />
                <span>Imports</span>
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link to="/exports" className="w-full cursor-pointer">
                <FileOutput className="mr-2 h-4 w-4" />
                <span>Exports</span>
              </Link>
            </DropdownMenuItem>
          </DropdownMenuSubContent>
        </DropdownMenuSub>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={logout} className="text-red-600 focus:bg-red-50 focus:text-red-700 cursor-pointer">
          <LogOut className="mr-2 h-4 w-4" />
          <span>Log out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
