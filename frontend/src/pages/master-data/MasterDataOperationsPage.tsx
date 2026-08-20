import { useAuth } from "@/hooks/use-auth";
import { MasterDataTabs } from "@/components/master-data/MasterDataTabs";

export function MasterDataOperationsPage() {
  const { hasPermission } = useAuth();
  
  // High-level page protection
  const canViewPage = 
    hasPermission("MASTER_DATA_IMPORT") || 
    hasPermission("MASTER_DATA_EXPORT") || 
    hasPermission("MASTER_DATA_ACTIVITY_VIEW");

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

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Master Data Operations</h2>
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
