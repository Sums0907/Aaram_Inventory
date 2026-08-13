import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "@/components/ui/table";
import { AlertCircle, PackageSearch, Activity, Package, ArrowRight, ArrowDownToLine, ArrowUpFromLine, Search } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface DashboardKPIs {
  total_skus_tracked: number;
  total_negative_inventory: number;
  total_low_stock: number;
  bom_health: { skus_missing_bom: number };
  total_pending_job_work: number;
}

interface RecentActivity {
  id: string;
  movement_number: string;
  sku_id: string;
  quantity: number;
  movement_type: string;
  reference_document: string;
  status: string;
  created_on: string;
}

export const InventoryPage: React.FC = () => {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [kpiRes, activityRes] = await Promise.all([
          fetch("/api/v1/inventory/dashboard/kpis"),
          fetch("/api/v1/inventory/dashboard/recent-activity")
        ]);
        
        if (kpiRes.ok) {
          const data = await kpiRes.json();
          setKpis(data.data);
        }
        
        if (activityRes.ok) {
          const data = await activityRes.json();
          setRecentActivity(data.data);
        }
      } catch (error) {
        console.error("Failed to load dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center p-8">
        <Activity className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-8 w-full max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Inventory Intelligence</h1>
          <p className="text-muted-foreground mt-2">Control centre for inventory truth, health and movements.</p>
        </div>
        <div className="flex gap-4">
          <Button variant="outline" asChild>
            <Link to="/inventory/receipts"><ArrowDownToLine className="mr-2 h-4 w-4" /> Receive Goods</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/inventory/suppliers"><ArrowUpFromLine className="mr-2 h-4 w-4" /> Issue to Job Worker</Link>
          </Button>
          <Button asChild>
            <Link to="/inventory/products"><Search className="mr-2 h-4 w-4" /> Browse Inventory</Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Items</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis?.total_skus_tracked || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Low Stock</CardTitle>
            <AlertCircle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis?.total_low_stock || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Negative Stock</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">{kpis?.total_negative_inventory || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Job Work</CardTitle>
            <PackageSearch className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis?.total_pending_job_work || 0}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">BOM Incomplete</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpis?.bom_health?.skus_missing_bom || 0}</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Needs Attention</CardTitle>
              <CardDescription>Critical operational items requiring action</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              {(kpis?.total_negative_inventory ?? 0) > 0 && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Negative Stock Detected</AlertTitle>
                  <AlertDescription className="flex items-center justify-between">
                    <span>{kpis?.total_negative_inventory} items currently have negative balance.</span>
                    <Button variant="link" size="sm" asChild className="p-0 h-auto">
                      <Link to="/inventory/products?filter=negative">Resolve <ArrowRight className="ml-1 h-3 w-3"/></Link>
                    </Button>
                  </AlertDescription>
                </Alert>
              )}
              
              {(kpis?.total_low_stock ?? 0) > 0 && (
                <Alert className="border-orange-200 bg-orange-50 text-orange-900">
                  <AlertCircle className="h-4 w-4 text-orange-600" />
                  <AlertTitle className="text-orange-900">Low Stock</AlertTitle>
                  <AlertDescription className="flex items-center justify-between text-orange-800">
                    <span>{kpis?.total_low_stock} items are running low.</span>
                    <Button variant="link" size="sm" asChild className="p-0 h-auto text-orange-700">
                      <Link to="/inventory/products?filter=low">View Items <ArrowRight className="ml-1 h-3 w-3"/></Link>
                    </Button>
                  </AlertDescription>
                </Alert>
              )}
              
              {(kpis?.total_pending_job_work ?? 0) > 0 && (
                <Alert className="border-yellow-200 bg-yellow-50 text-yellow-900">
                  <PackageSearch className="h-4 w-4 text-yellow-600" />
                  <AlertTitle className="text-yellow-900">Pending Job Work</AlertTitle>
                  <AlertDescription className="flex items-center justify-between text-yellow-800">
                    <span>{kpis?.total_pending_job_work} items are currently with Job Workers.</span>
                    <Button variant="link" size="sm" asChild className="p-0 h-auto text-yellow-700">
                      <Link to="/inventory/suppliers">View Job Workers <ArrowRight className="ml-1 h-3 w-3"/></Link>
                    </Button>
                  </AlertDescription>
                </Alert>
              )}
              
              {(kpis?.bom_health?.skus_missing_bom ?? 0) > 0 && (
                <Alert>
                  <Activity className="h-4 w-4" />
                  <AlertTitle>Missing BOMs</AlertTitle>
                  <AlertDescription className="flex items-center justify-between">
                    <span>{kpis?.bom_health?.skus_missing_bom} finished goods are missing a BOM definition.</span>
                    <Button variant="link" size="sm" asChild className="p-0 h-auto">
                      <Link to="/inventory/boms">Setup BOMs <ArrowRight className="ml-1 h-3 w-3"/></Link>
                    </Button>
                  </AlertDescription>
                </Alert>
              )}
              
              {(!kpis || (kpis.total_negative_inventory === 0 && kpis.total_low_stock === 0 && kpis.total_pending_job_work === 0 && kpis.bom_health?.skus_missing_bom === 0)) && (
                <div className="text-sm text-muted-foreground py-4 text-center">
                  All inventory health metrics look good. No critical items require attention.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
        
        <Card className="flex flex-col h-full">
          <CardHeader>
            <CardTitle>Recent Inventory Activity</CardTitle>
            <CardDescription>Latest immutable ledger movements</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 overflow-auto p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="pl-6">Date</TableHead>
                  <TableHead>Movement</TableHead>
                  <TableHead className="text-right pr-6">Quantity</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentActivity.map((activity) => (
                  <TableRow key={activity.id}>
                    <TableCell className="pl-6 text-muted-foreground whitespace-nowrap">
                      {new Date(activity.created_on).toLocaleString(undefined, {
                        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                      })}
                    </TableCell>
                    <TableCell>
                      <div className="font-medium text-xs bg-muted px-2 py-1 rounded inline-block mb-1">{activity.movement_type}</div>
                      <div className="text-xs text-muted-foreground">{activity.reference_document || activity.movement_number}</div>
                    </TableCell>
                    <TableCell className={`text-right font-medium pr-6 ${activity.quantity > 0 ? "text-green-600" : activity.quantity < 0 ? "text-red-600" : ""}`}>
                      {activity.quantity > 0 ? "+" : ""}{activity.quantity}
                    </TableCell>
                  </TableRow>
                ))}
                
                {recentActivity.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={3} className="h-24 text-center text-muted-foreground">
                      No recent activity recorded.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
          <div className="p-4 border-t border-border mt-auto">
             <Button variant="ghost" className="w-full" asChild>
                <Link to="/inventory/activity">View All Activity <ArrowRight className="ml-2 h-4 w-4"/></Link>
             </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};
