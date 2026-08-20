// @ts-nocheck
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Settings2, Save, Key, UserCircle, BellRing, Link2 } from "lucide-react"

export function SettingsPage() {
  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Workspace Settings</h1>
        <p className="text-slate-500">Manage integrations, team members, and application preferences.</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        <aside className="lg:w-1/4">
          <nav className="flex flex-col space-y-1">
            <Button variant="secondary" className="justify-start gap-2 text-indigo-700 bg-indigo-50 hover:bg-indigo-100">
              <Link2 className="h-4 w-4" />
              API Integrations
            </Button>
            <Button variant="ghost" className="justify-start gap-2 text-slate-600 hover:text-slate-900">
              <UserCircle className="h-4 w-4" />
              Team Members
            </Button>
            <Button variant="ghost" className="justify-start gap-2 text-slate-600 hover:text-slate-900">
              <BellRing className="h-4 w-4" />
              Notifications
            </Button>
            <Button variant="ghost" className="justify-start gap-2 text-slate-600 hover:text-slate-900">
              <Settings2 className="h-4 w-4" />
              Advanced
            </Button>
          </nav>
        </aside>

        <main className="flex-1 space-y-8 max-w-3xl">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="bg-slate-50/50 border-b">
              <CardTitle className="text-lg flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-xs">SD</div>
                ShopDeck Integration
              </CardTitle>
              <CardDescription>
                Configure credentials to pull sales orders, inventory, and invoices.
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <form className="space-y-4">
                <div className="grid gap-2">
                  <Label htmlFor="shopdeck-api-key" className="text-slate-700">API Key</Label>
                  <div className="relative">
                    <Key className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                    <Input id="shopdeck-api-key" type="password" placeholder="sk_live_..." className="pl-9" defaultValue="sk_live_dummy123" />
                  </div>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="shopdeck-webhook" className="text-slate-700">Webhook Secret</Label>
                  <div className="relative">
                    <Key className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                    <Input id="shopdeck-webhook" type="password" placeholder="whsec_..." className="pl-9" defaultValue="whsec_dummy123" />
                  </div>
                </div>
                <div className="pt-2 flex justify-end">
                  <Button className="gap-2 bg-indigo-600 hover:bg-indigo-700">
                    <Save className="h-4 w-4" /> Save ShopDeck Configuration
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="bg-slate-50/50 border-b">
              <CardTitle className="text-lg flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-xs">RP</div>
                Razorpay Integration
              </CardTitle>
              <CardDescription>
                Configure credentials to pull payment status and settlement reports.
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <form className="space-y-4">
                <div className="grid gap-2">
                  <Label htmlFor="rzp-key-id" className="text-slate-700">Key ID</Label>
                  <Input id="rzp-key-id" placeholder="rzp_live_..." defaultValue="rzp_live_dummy123" />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="rzp-key-secret" className="text-slate-700">Key Secret</Label>
                  <div className="relative">
                    <Key className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                    <Input id="rzp-key-secret" type="password" placeholder="secret..." className="pl-9" defaultValue="secret_dummy123" />
                  </div>
                </div>
                <div className="pt-2 flex justify-end">
                  <Button className="gap-2 bg-indigo-600 hover:bg-indigo-700">
                    <Save className="h-4 w-4" /> Save Razorpay Configuration
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  )
}
