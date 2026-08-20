import { useAuth } from "@/hooks/use-auth";
import { ImportWizard } from "./ImportWizard";

export function ImportPanel() {
  const { hasPermission } = useAuth();

  // UX Enforcement: MASTER_DATA_IMPORT
  if (!hasPermission("MASTER_DATA_IMPORT")) {
    return (
      <div className="p-8 text-center text-slate-500">
        You do not have permission to access the Import Operations.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-2">
        <h3 className="text-lg font-medium">Import Master Data</h3>
        <p className="text-sm text-slate-500">
          Upload and validate master data. The data will be validated via a dry-run before any changes are committed to the database.
        </p>
      </div>
      
      {/* Import Wizard */}
      <div className="mt-4">
        <ImportWizard />
      </div>
    </div>
  );
}
