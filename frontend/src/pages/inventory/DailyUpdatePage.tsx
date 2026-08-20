// @ts-nocheck
import React, { useState } from 'react';
import { useUploadShopDeckOrders, useImportJobPreview, useCommitImportJob, useReportWindow } from '@/api/imports';
import { useRunMatchingPipeline } from '@/api/matching';
import { UploadCloud, CheckCircle, Package, TrendingUp, TrendingDown, Calendar, FileText, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { Card } from '@/components/ui/card';

export function DailyUpdatePage() {
  const [file, setFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [step, setStep] = useState<1 | 2 | 3>(1); // 1 = Upload, 2 = Preview, 3 = Complete

  const uploadMutation = useUploadShopDeckOrders();
  const previewQuery = useImportJobPreview(jobId);
  const commitMutation = useCommitImportJob();
  const matchingMutation = useRunMatchingPipeline();
  const windowQuery = useReportWindow();

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "";
    const d = new Date(dateStr);
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const day = d.getDate().toString().padStart(2, '0');
    const month = months[d.getMonth()];
    const year = d.getFullYear();
    return `${day} ${month} ${year}`;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    try {
      const response = await uploadMutation.mutateAsync(file);
      setJobId(response.id);
      setStep(2);
      toast.success("File uploaded and parsed successfully.");
    } catch (e: any) {
      toast.error(e.response?.data?.message || "Failed to upload file");
    }
  };

  const handleConfirm = async () => {
    if (!jobId) return;
    try {
      toast.loading("Committing job...", { id: "commit" });
      await commitMutation.mutateAsync(jobId);
      toast.loading("Running Matching & Inventory Rules...", { id: "commit" });
      await matchingMutation.mutateAsync();
      toast.success("Inventory updated successfully!", { id: "commit" });
      setStep(3);
    } catch (e: any) {
      toast.error(e.response?.data?.message || "Failed to commit job", { id: "commit" });
    }
  };

  const reset = () => {
    setFile(null);
    setJobId(null);
    setStep(1);
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-2">Daily Inventory Update <span className="text-sm px-2 py-1 bg-red-100 text-red-800 rounded-md ml-2 align-middle">LEGACY</span></h1>
        <p className="text-gray-600">Import your daily ShopDeck Order Reconciliation Report to synchronize inventory balances.</p>
        
        <div className="mt-4 flex items-center gap-3 p-4 rounded-lg bg-amber-50 border border-amber-200 text-amber-800">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <div className="text-sm">
            <strong>ARCHIVED FUNCTIONALITY:</strong> This workflow is deprecated. ShopDeck Reconciliation no longer affects Inventory physical movements. 
            Physical inventory is now handled automatically in real-time via the Packer System integration. 
            This page remains active only for historical/fallback purposes and only creates accounting journals.
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center space-x-4 mb-8">
        <div className={`flex items-center space-x-2 ${step >= 1 ? 'text-gray-900' : 'text-gray-500'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white ${step >= 1 ? 'bg-indigo-600' : 'bg-gray-300'}`}>1</div>
          <span className="font-medium">Upload CSV</span>
        </div>
        <div className="h-px bg-gray-300 flex-1"></div>
        <div className={`flex items-center space-x-2 ${step >= 2 ? 'text-gray-900' : 'text-gray-500'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white ${step >= 2 ? 'bg-indigo-600' : 'bg-gray-300'}`}>2</div>
          <span className="font-medium">Preview</span>
        </div>
        <div className="h-px bg-gray-300 flex-1"></div>
        <div className={`flex items-center space-x-2 ${step >= 3 ? 'text-gray-900' : 'text-gray-500'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white ${step >= 3 ? 'bg-emerald-600' : 'bg-gray-300'}`}>3</div>
          <span className="font-medium">Complete</span>
        </div>
      </div>

      {/* Step 1: Upload */}
      {step === 1 && (
        <Card className="p-8 border border-gray-200 bg-white shadow-sm flex flex-col items-center justify-center space-y-6">
          <div className="w-20 h-20 bg-indigo-50 rounded-full flex items-center justify-center">
            <UploadCloud className="w-10 h-10 text-indigo-600" />
          </div>
          <div className="text-center">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload Order Reconciliation Report</h3>
            <p className="text-gray-600 text-sm max-w-md mx-auto">
              Select the daily CSV report downloaded from your ShopDeck dashboard to begin the synchronization process.
            </p>
          </div>

          {/* Rolling Window Banner */}
          {windowQuery.isLoading ? (
            <div className="w-full max-w-lg p-4 bg-gray-100 rounded-lg animate-pulse h-24"></div>
          ) : windowQuery.data?.required_report_start_date ? (
            <div className="w-full max-w-lg p-4 bg-indigo-50 border border-indigo-200 rounded-lg text-left">
              <h4 className="font-semibold text-indigo-900 mb-1">ShopDeck Report Required</h4>
              <p className="text-sm text-indigo-700 mb-3">
                Please download the Order Reconciliation Report from <strong>{formatDate(windowQuery.data.required_report_start_date)} to {formatDate(windowQuery.data.required_report_end_date)}</strong> from ShopDeck before uploading it.
              </p>
              <div className="text-xs text-indigo-600">
                <p>Oldest active order: <code className="bg-indigo-100 px-1 py-0.5 rounded text-indigo-800 font-mono">{windowQuery.data.oldest_active_order_id?.substring(0, 8) || 'N/A'}...</code></p>
                <p>Active orders being monitored: <strong>{windowQuery.data.active_order_count}</strong></p>
              </div>
            </div>
          ) : windowQuery.data ? (
            <div className="w-full max-w-lg p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-left">
              <h4 className="font-semibold text-emerald-800 mb-1">No active ShopDeck orders currently require monitoring.</h4>
              <p className="text-sm text-emerald-700">
                Any recent ShopDeck report can be uploaded.
              </p>
            </div>
          ) : null}
          
          <div className="w-full max-w-md">
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer hover:bg-gray-50 hover:border-indigo-500 transition-all duration-200">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <p className="mb-2 text-sm text-gray-600"><span className="font-semibold text-indigo-600">Click to browse</span> or drag and drop</p>
                <p className="text-xs text-gray-500">CSV file only</p>
                {file && <p className="mt-2 text-emerald-600 font-medium text-sm flex items-center gap-1"><FileText className="w-4 h-4"/> {file.name}</p>}
              </div>
              <input type="file" className="hidden" accept=".csv" onChange={handleFileChange} />
            </label>
          </div>

          <button 
            onClick={handleUpload}
            disabled={!file || uploadMutation.isPending}
            className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-medium shadow-lg shadow-indigo-500/20 transition-all active:scale-95"
          >
            {uploadMutation.isPending ? 'Uploading & Parsing...' : 'Process Report'}
          </button>
        </Card>
      )}

      {/* Step 2: Preview */}
      {step === 2 && previewQuery.data && (
        <div className="space-y-6 animate-in slide-in-from-right-8 duration-500">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <Card className="p-5 border-gray-200 bg-white shadow-sm flex flex-col gap-3 group hover:border-indigo-300 transition-colors">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 text-sm font-medium">Report Period</span>
                <Calendar className="w-5 h-5 text-indigo-500 group-hover:scale-110 transition-transform" />
              </div>
              <div>
                <div className="text-xl font-semibold text-gray-900">
                  {previewQuery.data.report_date_min === previewQuery.data.report_date_max 
                    ? previewQuery.data.report_date_min 
                    : `${previewQuery.data.report_date_min} to ${previewQuery.data.report_date_max}`}
                </div>
                <div className="text-xs text-gray-500 mt-1">Based on normalized data</div>
              </div>
            </Card>

            <Card className="p-5 border-gray-200 bg-white shadow-sm flex flex-col gap-3 group hover:border-emerald-300 transition-colors">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 text-sm font-medium">Total Orders</span>
                <FileText className="w-5 h-5 text-emerald-500 group-hover:scale-110 transition-transform" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{previewQuery.data.total_orders}</div>
                <div className="text-xs text-gray-500 mt-1">Unique tracking IDs</div>
              </div>
            </Card>

            <Card className="p-5 border-gray-200 bg-white shadow-sm flex flex-col gap-3 group hover:border-blue-300 transition-colors">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 text-sm font-medium">Unique SKUs</span>
                <Package className="w-5 h-5 text-blue-500 group-hover:scale-110 transition-transform" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{previewQuery.data.total_skus}</div>
                <div className="text-xs text-gray-500 mt-1">Impacted catalog items</div>
              </div>
            </Card>

            <Card className="p-5 border-gray-200 bg-white shadow-sm flex flex-col gap-3 group hover:border-amber-300 transition-colors">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 text-sm font-medium">Net Units Movement</span>
                <TrendingUp className="w-5 h-5 text-amber-500 group-hover:scale-110 transition-transform" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 flex gap-2">
                  <span className="text-emerald-600">-{previewQuery.data.units_sold}</span>
                  <span className="text-gray-400">/</span>
                  <span className="text-blue-600">+{previewQuery.data.units_returned}</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">Sold / Returned</div>
              </div>
            </Card>
          </div>

          <div className="flex items-center gap-3 p-4 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-800">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm">
              Please verify the metrics above. Clicking <strong>Confirm Import</strong> will officially record these sales and decrement inventory quantities automatically.
            </p>
          </div>

          <div className="flex gap-4">
            <button 
              onClick={reset}
              className="px-6 py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded-lg font-medium transition-colors"
            >
              Cancel
            </button>
            <button 
              onClick={handleConfirm}
              disabled={commitMutation.isPending || matchingMutation.isPending}
              className="flex-1 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg font-medium shadow-lg shadow-emerald-600/20 transition-all active:scale-95 flex items-center justify-center gap-2"
            >
              {(commitMutation.isPending || matchingMutation.isPending) ? (
                <span>Processing Inventory Rules...</span>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5" />
                  <span>Confirm Import & Update Inventory</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Success */}
      {step === 3 && (
        <Card className="p-12 border-emerald-200 bg-emerald-50 flex flex-col items-center justify-center space-y-6 animate-in zoom-in-95 duration-500 shadow-sm">
          <div className="w-24 h-24 bg-emerald-100 rounded-full flex items-center justify-center mb-2">
            <CheckCircle className="w-12 h-12 text-emerald-600" />
          </div>
          <div className="text-center">
            <h2 className="text-3xl font-bold text-emerald-900 mb-3">Inventory Updated!</h2>
            <p className="text-emerald-700 max-w-md mx-auto">
              The Daily Order Reconciliation report has been successfully processed. All corresponding inventory movements have been generated and final balances recalculated.
            </p>
          </div>
          <button 
            onClick={reset}
            className="mt-4 px-8 py-3 bg-gray-900 hover:bg-gray-800 text-white rounded-lg font-medium transition-colors"
          >
            Import Another Report
          </button>
        </Card>
      )}

    </div>
  );
}
