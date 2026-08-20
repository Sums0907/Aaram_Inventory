import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Download, Loader2, CheckCircle2 } from "lucide-react";
import { masterDataApi } from "@/api/master-data";
import { useToast } from "@/hooks/use-toast";

const EXPORT_DOMAINS = [
  { id: "RAW_MATERIAL", label: "Raw Materials", desc: "Outputs all raw material definitions" },
  { id: "OPERATIONAL_CATEGORY", label: "Operational Categories", desc: "Outputs category hierarchy" },
  { id: "SUPPLIER", label: "Suppliers", desc: "Outputs registered suppliers" },
  { id: "UOM", label: "Unit of Measure (UoM)", desc: "Outputs active units of measure" },
  { id: "BOM", label: "Bill of Materials (BOM)", desc: "Outputs product recipes and dependencies" },
];

export function ExportPanel() {
  const { hasPermission } = useAuth();
  const { toast } = useToast();
  const [exportingDomain, setExportingDomain] = useState<string | null>(null);
  const [lastExport, setLastExport] = useState<{ domain: string, timestamp: string, filename: string } | null>(null);

  // UX Enforcement: MASTER_DATA_EXPORT
  if (!hasPermission("MASTER_DATA_EXPORT")) {
    return (
      <div className="p-8 text-center text-slate-500">
        You do not have permission to access the Export Operations.
      </div>
    );
  }

  const handleExport = async (domain: string, label: string) => {
    setExportingDomain(domain);
    try {
      const blob = await masterDataApi.export(domain);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      const filename = `export_${domain.toLowerCase()}_${new Date().getTime()}.xlsx`;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setLastExport({
        domain: label,
        filename,
        timestamp: new Date().toLocaleString()
      });

      toast({
        title: "Export Successful",
        description: `${label} export has been downloaded.`,
      });
      
    } catch (error) {
      console.error(error);
      // Actual error UI is managed by the API interceptor, but we can have a fallback toast if needed
    } finally {
      setExportingDomain(null);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex flex-col space-y-2">
        <h3 className="text-lg font-medium">Export Master Data</h3>
        <p className="text-sm text-slate-500">
          Generate and download round-trippable datasets for different domains.
        </p>
      </div>

      {lastExport && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 flex items-start gap-3 animate-in fade-in slide-in-from-top-4">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-emerald-900">Export Completed Successfully</h4>
            <div className="mt-2 space-y-1 text-sm text-emerald-800">
              <p><span className="font-medium">Domain:</span> {lastExport.domain}</p>
              <p><span className="font-medium">Filename:</span> {lastExport.filename}</p>
              <p><span className="font-medium">Generated At:</span> {lastExport.timestamp}</p>
            </div>
          </div>
        </div>
      )}
      
      <div className="border border-slate-200 rounded-lg bg-white overflow-hidden">
        <div className="bg-slate-50 border-b border-slate-200 px-4 py-3">
          <h4 className="font-medium text-slate-900 text-sm">Available Exports</h4>
        </div>
        
        <div className="divide-y divide-slate-100">
          {EXPORT_DOMAINS.map((domain) => (
            <div key={domain.id} className="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors">
              <div>
                <p className="font-medium text-sm text-slate-900">{domain.label}</p>
                <p className="text-xs text-slate-500 mt-0.5">{domain.desc}</p>
              </div>
              <Button 
                size="sm" 
                variant="outline" 
                className="gap-2 min-w-28"
                onClick={() => handleExport(domain.id, domain.label)}
                disabled={exportingDomain !== null}
              >
                {exportingDomain === domain.id ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Exporting...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 text-slate-500" />
                    Export
                  </>
                )}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
