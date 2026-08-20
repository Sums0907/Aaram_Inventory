// @ts-nocheck
import { useAuth } from "@/hooks/use-auth";

export function ActivityHistoryPanel() {
  const { hasPermission } = useAuth();

  // UX Enforcement: MASTER_DATA_ACTIVITY_VIEW
  if (!hasPermission("MASTER_DATA_ACTIVITY_VIEW")) {
    return (
      <div className="p-8 text-center text-slate-500">
        You do not have permission to view Activity History.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-2">
        <h3 className="text-lg font-medium">Master Data Activity History</h3>
        <p className="text-sm text-slate-500">
          View the audit log of all previous import and export events.
        </p>
      </div>
      
      {/* Skeleton for History Table */}
      <div className="border border-slate-200 rounded-lg p-8 flex items-center justify-center bg-slate-50/50">
        <p className="text-slate-500">Activity History Data Table (To be implemented)</p>
      </div>
    </div>
  );
}
