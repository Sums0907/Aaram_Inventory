import { Outlet } from "react-router-dom"
import { Topbar } from "./Topbar"

export function AppLayout() {
  return (
    <div className="flex h-screen w-full bg-slate-50 flex-col overflow-hidden font-sans">
      <Topbar />
      <main className="flex-1 overflow-y-auto bg-slate-50/50 relative flex flex-col">
        <Outlet />
      </main>
    </div>
  )
}
