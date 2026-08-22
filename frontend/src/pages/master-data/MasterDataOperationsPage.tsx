// @ts-nocheck
import { useAuth } from "@/hooks/use-auth";
import { MasterDataTabs } from "@/components/master-data/MasterDataTabs";
import { masterDataApi } from "@/api/master-data";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { toast } from "@/hooks/use-toast";

export function MasterDataOperationsPage() {
  const { hasPermission } = useAuth();
  const [isSyncing, setIsSyncing] = useState(false);
  
  // High-level page protection
  const canViewPage = 
    hasPermission("INVENTORY_MASTER_DATA_IMPORT") || 
    hasPermission("INVENTORY_MASTER_DATA_EXPORT") || 
    hasPermission("INVENTORY_MASTER_DATA_ACTIVITY_VIEW");

  if (!canViewPage) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-8 bg-slate-50">
        <div className="text-center space-y-4 max-w-md">
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">Access Denied</h2>
          <p className="text-slate-500">
            You do not have the required permissions to view the Master Data Operations module.
          </p>
        </div>
      </div>
    );
  }

  const handleForceSync = async () => {
    setIsSyncing(true);
    try {
      await masterDataApi.forcePackerSync();
      toast({
        title: "Sync Initiated",
        description: "Master Data and Stock Balances have been successfully queued for AaramPacking.",
        variant: "default",
      });
    } catch (error) {
      toast({
        title: "Sync Failed",
        description: "An error occurred while attempting to synchronize with Packer.",
        variant: "destructive",
      });
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Master Data Operations</h2>
          
          {hasPermission("INVENTORY_CATALOG_VIEW") && (
            <Button 
              onClick={handleForceSync} 
              disabled={isSyncing}
              variant="destructive"
              size="lg"
              className="gap-2 text-md"
            >
              <RefreshCw className={`h-4 w-4 ${isSyncing ? 'animate-spin' : ''}`} />
              {isSyncing ? "Syncing..." : "Force Sync Packer SKU Master"}
            </Button>
          )}
        </div>
        <p className="text-slate-500 max-w-2xl">
          Manage master datasets, synchronize operations, and review audit logs. All domain rules and validations are enforced server-side.
        </p>

        <div className="mt-8">
          <MasterDataTabs />
        </div>
      </div>
    </div>
  );
}
