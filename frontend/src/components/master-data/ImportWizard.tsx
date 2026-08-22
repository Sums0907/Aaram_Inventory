// @ts-nocheck
import { useState, useRef } from "react";
import { masterDataApi } from "@/api/master-data";
import type { ImportResult, ImportRowResult } from "@/api/master-data";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { AlertCircle, CheckCircle2, FileUp, Play, CheckSquare, Loader2, UploadCloud, AlertTriangle } from "lucide-react";

const DOMAINS = [
  { id: "UOM", label: "Unit of Measure (UoM)" },
  { id: "OPERATIONAL_CATEGORY", label: "Operational Categories" },
  { id: "SUPPLIER", label: "Suppliers" },
  { id: "RAW_MATERIAL", label: "Raw Materials" },
  { id: "BOM", label: "Bill of Materials (BOM)" },
  { id: "PRODUCT_SKU", label: "ShopDeck SKU Sync" }
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export function ImportWizard() {
  const { toast } = useToast();
  const [step, setStep] = useState<number>(1);
  const [selectedDomain, setSelectedDomain] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [dryRunResult, setDryRunResult] = useState<ImportResult | null>(null);
  const [commitResult, setCommitResult] = useState<ImportResult | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- Step 1 & 2: Selection & Upload ---
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validation
    const isExcel = file.name.endsWith('.xlsx');
    const isCsv = file.name.endsWith('.csv');
    
    if (!isExcel && !isCsv) {
      toast({ variant: "destructive", title: "Invalid File", description: "Only .xlsx and .csv files are supported." });
      return;
    }
    
    if (file.size > MAX_FILE_SIZE) {
      toast({ variant: "destructive", title: "File too large", description: "File size exceeds 10MB limit." });
      return;
    }

    if (!selectedDomain) {
      toast({ variant: "destructive", title: "Domain Required", description: "Please select a domain first." });
      return;
    }

    setSelectedFile(file);
  };

  // --- Step 3 & 4: Dry Run ---
  const handleDryRun = async () => {
    if (!selectedFile || !selectedDomain) return;
    
    setIsProcessing(true);
    try {
      const result = await masterDataApi.import(selectedFile, selectedDomain, true);
      setDryRunResult(result);
      setStep(3); // Move to Preview / Commit step
    } catch (error: any) {
      // Error handling is managed partly by axios interceptor, but we can capture explicit failures here.
      console.error(error);
    } finally {
      setIsProcessing(false);
    }
  };

  // --- Step 5: Commit ---
  const handleCommit = async () => {
    if (!selectedFile || !selectedDomain) return;
    
    setIsProcessing(true);
    try {
      const result = await masterDataApi.import(selectedFile, selectedDomain, false);
      setCommitResult(result);
      setStep(4); // Move to Success screen
    } catch (error: any) {
      console.error(error);
    } finally {
      setIsProcessing(false);
    }
  };

  const resetWizard = () => {
    setStep(1);
    setSelectedDomain("");
    setSelectedFile(null);
    setDryRunResult(null);
    setCommitResult(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const canCommit = dryRunResult && dryRunResult.failed_count === 0 && dryRunResult.ambiguous_count === 0;

  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-sm">
      {/* Header / Stepper Progress */}
      <div className="flex items-center justify-between p-4 border-b border-slate-100 bg-slate-50/50 rounded-t-lg">
        <div className="flex items-center gap-6 text-sm font-medium">
          <span className={`flex items-center gap-2 ${step >= 1 ? 'text-indigo-600' : 'text-slate-400'}`}>
            <div className={`w-6 h-6 flex items-center justify-center rounded-full text-xs ${step >= 1 ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500'}`}>1</div>
            Upload
          </span>
          <span className={`flex items-center gap-2 ${step >= 3 ? 'text-indigo-600' : 'text-slate-400'}`}>
            <div className={`w-6 h-6 flex items-center justify-center rounded-full text-xs ${step >= 3 ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500'}`}>2</div>
            Preview
          </span>
          <span className={`flex items-center gap-2 ${step >= 4 ? 'text-indigo-600' : 'text-slate-400'}`}>
            <div className={`w-6 h-6 flex items-center justify-center rounded-full text-xs ${step >= 4 ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-500'}`}>3</div>
            Complete
          </span>
        </div>
      </div>

      <div className="p-6">
        {/* Step 1 & 2: Setup & Upload */}
        {step === 1 && (
          <div className="space-y-6 max-w-xl">
            <div className="space-y-3">
              <label className="text-sm font-medium text-slate-700">1. Select Data Domain</label>
              <div className="grid grid-cols-2 gap-3">
                {DOMAINS.map(d => (
                  <button
                    key={d.id}
                    onClick={() => setSelectedDomain(d.id)}
                    className={`p-3 text-left border rounded-lg transition-all ${selectedDomain === d.id ? 'border-indigo-600 bg-indigo-50 ring-1 ring-indigo-600' : 'border-slate-200 hover:border-slate-300 bg-white'}`}
                  >
                    <span className={`text-sm font-medium ${selectedDomain === d.id ? 'text-indigo-900' : 'text-slate-700'}`}>{d.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-3 pt-4 border-t border-slate-100">
              <label className="text-sm font-medium text-slate-700">2. Select File (.xlsx or .csv)</label>
              <div 
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${selectedFile ? 'border-indigo-300 bg-indigo-50/50' : 'border-slate-200 bg-slate-50 hover:bg-slate-100'}`}
              >
                {!selectedFile ? (
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-12 h-12 bg-white rounded-full shadow-sm border border-slate-100 flex items-center justify-center mb-2">
                      <UploadCloud className="w-6 h-6 text-slate-400" />
                    </div>
                    <p className="text-sm text-slate-600">Click to browse or drag and drop</p>
                    <p className="text-xs text-slate-400">Maximum file size 10MB</p>
                    <input 
                      type="file" 
                      accept=".xlsx,.csv" 
                      className="hidden" 
                      ref={fileInputRef}
                      onChange={handleFileChange}
                    />
                    <Button variant="outline" size="sm" className="mt-4" onClick={() => fileInputRef.current?.click()}>
                      Select File
                    </Button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-3">
                    <FileUp className="w-8 h-8 text-indigo-500" />
                    <div className="text-center">
                      <p className="text-sm font-medium text-indigo-900">{selectedFile.name}</p>
                      <p className="text-xs text-indigo-600/70">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                    <Button variant="ghost" size="sm" className="text-slate-500 hover:text-slate-700" onClick={() => setSelectedFile(null)}>
                      Remove File
                    </Button>
                  </div>
                )}
              </div>
            </div>

            <div className="pt-6 flex justify-end">
              <Button 
                onClick={handleDryRun} 
                disabled={!selectedFile || !selectedDomain || isProcessing}
                className="gap-2 bg-indigo-600 hover:bg-indigo-700"
              >
                {isProcessing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                Execute Dry Run
              </Button>
            </div>
          </div>
        )}

        {/* Step 3 & 4: Preview Diff & Commit Approval */}
        {step === 3 && dryRunResult && (
          <div className="space-y-6">
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-semibold text-amber-900">Dry Run Validation Complete</h4>
                <p className="text-sm text-amber-700 mt-1">Review the changes below. No data has been committed to the database yet.</p>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="p-4 border border-slate-100 rounded-lg bg-slate-50 text-center">
                <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">Total</p>
                <p className="text-2xl font-bold text-slate-900 mt-1">{dryRunResult.total_records}</p>
              </div>
              <div className="p-4 border border-emerald-100 rounded-lg bg-emerald-50 text-center">
                <p className="text-xs text-emerald-600 font-medium uppercase tracking-wider">Created</p>
                <p className="text-2xl font-bold text-emerald-700 mt-1">{dryRunResult.created_count}</p>
              </div>
              <div className="p-4 border border-blue-100 rounded-lg bg-blue-50 text-center">
                <p className="text-xs text-blue-600 font-medium uppercase tracking-wider">Updated</p>
                <p className="text-2xl font-bold text-blue-700 mt-1">{dryRunResult.updated_count}</p>
              </div>
              <div className="p-4 border border-red-100 rounded-lg bg-red-50 text-center">
                <p className="text-xs text-red-600 font-medium uppercase tracking-wider">Failed</p>
                <p className="text-2xl font-bold text-red-700 mt-1">{dryRunResult.failed_count}</p>
              </div>
              <div className="p-4 border border-orange-100 rounded-lg bg-orange-50 text-center">
                <p className="text-xs text-orange-600 font-medium uppercase tracking-wider">Ambiguous</p>
                <p className="text-2xl font-bold text-orange-700 mt-1">{dryRunResult.ambiguous_count}</p>
              </div>
            </div>

            {/* Full Line-Item Preview Table */}
            {dryRunResult.row_results && dryRunResult.row_results.length > 0 && (
              <div className="border border-slate-200 rounded-lg overflow-hidden mt-6 bg-white">
                <div className="bg-slate-50 border-b border-slate-200 px-4 py-3 flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-slate-900">Line-Item Preview</h4>
                  <div className="flex gap-2 text-xs">
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span> Created</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500"></span> Updated</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-slate-300"></span> Ignored</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500"></span> Failed</span>
                  </div>
                </div>

                {dryRunResult.global_errors.length > 0 && (
                  <div className="p-4 bg-red-50 border-b border-red-100">
                    <p className="text-sm font-medium text-red-900 mb-2 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" /> Global Validation Errors:
                    </p>
                    <ul className="list-disc pl-5 space-y-1 text-sm text-red-700">
                      {dryRunResult.global_errors.map((err, i) => <li key={i}>{err}</li>)}
                    </ul>
                  </div>
                )}

                <div className="max-h-96 overflow-y-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-white sticky top-0 shadow-sm z-10 text-slate-500 font-medium border-b border-slate-200">
                      <tr>
                        <th className="px-4 py-3 w-20">Row</th>
                        <th className="px-4 py-3 w-48">Identifier</th>
                        <th className="px-4 py-3 w-32">Status</th>
                        <th className="px-4 py-3">Details / Errors</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {dryRunResult.row_results.map((r, i) => {
                        let statusColor = "bg-slate-100 text-slate-700";
                        if (r.action === 'CREATED') statusColor = "bg-emerald-100 text-emerald-700";
                        if (r.action === 'UPDATED') statusColor = "bg-blue-100 text-blue-700";
                        if (r.action === 'FAILED') statusColor = "bg-red-100 text-red-700";
                        if (r.action === 'AMBIGUOUS') statusColor = "bg-orange-100 text-orange-700";
                        
                        return (
                          <tr key={i} className="hover:bg-slate-50 transition-colors">
                            <td className="px-4 py-3 text-slate-500 font-medium">#{r.row_index}</td>
                            <td className="px-4 py-3 font-mono text-xs text-slate-700">{r.identifier || '-'}</td>
                            <td className="px-4 py-3">
                              <span className={`px-2 py-1 rounded text-xs font-semibold ${statusColor}`}>
                                {r.action}
                              </span>
                            </td>
                            <td className="px-4 py-3">
                              {r.errors && r.errors.length > 0 ? (
                                <ul className="list-disc pl-4 text-red-600 text-xs space-y-0.5">
                                  {r.errors.map((e, ei) => <li key={ei}>{e}</li>)}
                                </ul>
                              ) : (
                                <span className="text-slate-400 text-xs italic">No issues detected</span>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="flex items-center justify-between pt-6 border-t border-slate-100">
              <Button variant="outline" onClick={resetWizard} disabled={isProcessing}>
                Cancel & Start Over
              </Button>
              <div className="flex items-center gap-4">
                {!canCommit && (
                  <span className="text-sm text-red-600 font-medium flex items-center gap-1.5">
                    <AlertCircle className="w-4 h-4" />
                    Commit blocked due to validation errors
                  </span>
                )}
                <Button 
                  onClick={handleCommit} 
                  disabled={!canCommit || isProcessing}
                  className="bg-indigo-600 hover:bg-indigo-700 min-w-32"
                >
                  {isProcessing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <CheckSquare className="w-4 h-4 mr-2" />}
                  Commit Data
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Step 5: Result Screen */}
        {step === 4 && commitResult && (
          <div className="py-8 text-center max-w-md mx-auto space-y-6">
            <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            
            <div>
              <h3 className="text-2xl font-bold text-slate-900">Import Successful</h3>
              <p className="text-slate-500 mt-2">
                The master data has been successfully committed to the database.
              </p>
            </div>

            <div className="bg-slate-50 border border-slate-100 rounded-lg p-4 text-left space-y-3">
              <div className="flex justify-between items-center pb-3 border-b border-slate-200">
                <span className="text-sm text-slate-500 font-medium">Batch ID</span>
                <span className="text-sm font-mono font-semibold text-slate-900">{commitResult.batch_id}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-500">Domain</span>
                <span className="font-medium text-slate-900">{commitResult.entity_type}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-500">Records Created</span>
                <span className="font-medium text-emerald-600">{commitResult.created_count}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-500">Records Updated</span>
                <span className="font-medium text-blue-600">{commitResult.updated_count}</span>
              </div>
            </div>

            <div className="pt-4 flex flex-col gap-3">
              <Button variant="outline" className="w-full" onClick={resetWizard}>
                Import Another File
              </Button>
              <Button variant="link" className="text-indigo-600">
                View Activity History &rarr;
              </Button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
