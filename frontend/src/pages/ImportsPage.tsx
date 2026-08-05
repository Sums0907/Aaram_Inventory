import { useImportJobs } from "@/api/imports"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatDistanceToNow } from "date-fns"
import { UploadCloud, CheckCircle2, AlertCircle, Clock, RefreshCw } from "lucide-react"

export function ImportsPage() {
  const { data: jobs, isLoading } = useImportJobs()

  // Find latest job for each platform
  const latestShopdeck = jobs?.find(j => j.job_type.startsWith('SHOPDECK'))
  const latestRazorpay = jobs?.find(j => j.job_type.startsWith('RAZORPAY'))

  const renderIntegrationCard = (
    title: string, 
    description: string, 
    latestJob: any, 
    statusColor: string, 
    logoText: string
  ) => (
    <Card className="border-slate-200 shadow-sm transition-all hover:shadow-md overflow-hidden relative">
      <div className={`absolute top-0 left-0 w-1 h-full ${statusColor}`} />
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-slate-100 flex items-center justify-center font-bold text-slate-700">
              {logoText}
            </div>
            <div>
              <CardTitle className="text-lg">{title}</CardTitle>
              <CardDescription className="mt-1">{description}</CardDescription>
            </div>
          </div>
          {latestJob?.status === 'COMMITTED' || latestJob?.status === 'COMPLETED' ? (
            <Badge className="bg-emerald-100 text-emerald-800 hover:bg-emerald-100 border-0 flex gap-1 items-center px-2 py-1">
              <CheckCircle2 className="h-3 w-3" /> Connected
            </Badge>
          ) : (
            <Badge className="bg-amber-100 text-amber-800 hover:bg-amber-100 border-0 flex gap-1 items-center px-2 py-1">
              <AlertCircle className="h-3 w-3" /> Needs Sync
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-2">
        <div className="flex items-center justify-between mt-2">
          <div className="text-sm text-slate-500 flex items-center gap-2">
            <Clock className="h-4 w-4 text-slate-400" />
            {latestJob?.finished_at 
              ? `Last synced ${formatDistanceToNow(new Date(latestJob.finished_at))} ago`
              : 'Never synced'
            }
          </div>
          <Button variant="outline" className="gap-2 shadow-sm">
            <RefreshCw className="h-4 w-4" />
            Sync Now
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Integrations</h1>
          <p className="text-slate-500">Connect and sync data from your sales channels and payment gateways.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button className="gap-2 bg-indigo-600 hover:bg-indigo-700">
            <UploadCloud className="h-4 w-4" />
            Manual Upload
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2">
          <Card className="border-slate-200 h-48 animate-pulse bg-slate-50/50" />
          <Card className="border-slate-200 h-48 animate-pulse bg-slate-50/50" />
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-2 max-w-5xl">
          {renderIntegrationCard(
            "ShopDeck", 
            "Sync orders, inventory, and tax invoices.", 
            latestShopdeck, 
            "bg-blue-500",
            "SD"
          )}
          
          {renderIntegrationCard(
            "Razorpay", 
            "Sync payment settlements and fees.", 
            latestRazorpay, 
            "bg-indigo-500",
            "RP"
          )}
        </div>
      )}
    </div>
  )
}
