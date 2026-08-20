// @ts-nocheck
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ImportPanel } from "./ImportPanel";
import { ExportPanel } from "./ExportPanel";
import { ActivityHistoryPanel } from "./ActivityHistoryPanel";
import { useAuth } from "@/hooks/use-auth";

export function MasterDataTabs() {
  const { hasPermission } = useAuth();
  
  const canImport = hasPermission("MASTER_DATA_IMPORT");
  const canExport = hasPermission("MASTER_DATA_EXPORT");
  const canHistory = hasPermission("MASTER_DATA_ACTIVITY_VIEW");

  // If user cannot do anything, render an empty state or access denied
  if (!canExport && !canHistory && !canImport) {
    return (
      <div className="p-8 text-center text-slate-500 bg-white rounded-lg border border-slate-200">
        You do not have permission to access Master Data Operations.
      </div>
    );
  }

  // Default to import if they have access, otherwise default to export
  const defaultValue = canImport ? "import" : "export";

  return (
    <Tabs defaultValue={defaultValue} className="w-full">
      <TabsList className="grid w-full grid-cols-3 max-w-md mb-6">
        {canImport && <TabsTrigger value="import">Import</TabsTrigger>}
        {canExport && <TabsTrigger value="export">Export</TabsTrigger>}
        {canHistory && <TabsTrigger value="history">Activity History</TabsTrigger>}
      </TabsList>
      
      {canImport && (
        <TabsContent value="import" className="outline-none">
          <ImportPanel />
        </TabsContent>
      )}
      
      {canExport && (
        <TabsContent value="export" className="outline-none">
          <ExportPanel />
        </TabsContent>
      )}
      
      {canHistory && (
        <TabsContent value="history" className="outline-none">
          <ActivityHistoryPanel />
        </TabsContent>
      )}
    </Tabs>
  );
}
