// @ts-nocheck
import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { masterDataApi, type ImportAuditLog } from "@/api/master-data";
import { Badge } from "@/components/ui/badge";
import { RefreshCw, FileText, Clock, CheckCircle2, XCircle, Activity } from "lucide-react";

const STATUS_CONFIG = {
  COMMITTED: { label: "Committed", color: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  DRY_RUN:   { label: "Dry Run",   color: "bg-blue-100 text-blue-700 border-blue-200" },
  FAILED:    { label: "Failed",    color: "bg-red-100 text-red-700 border-red-200" },
};

const DOMAIN_LABELS: Record<string, string> = {
  UOM: "Unit of Measure",
  OPERATIONAL_CATEGORY: "Operational Categories",
  SUPPLIER: "Suppliers",
  RAW_MATERIAL: "Raw Materials",
  BOM: "Bill of Materials",
  CATEGORY: "Categories",
  PRODUCT_SKU: "ShopDeck SKU Sync",
};

function formatDuration(start: string, end: string): string {
  if (!start || !end) return "—";
  const ms = new Date(end).getTime() - new Date(start).getTime();
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

function formatDate(iso: string): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-IN", {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit", hour12: true,
  });
}

export function ActivityHistoryPanel() {
  const { hasPermission } = useAuth();
  const [logs, setLogs] = useState<ImportAuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [domainFilter, setDomainFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await masterDataApi.getActivityHistory({
        domain: domainFilter || undefined,
        status: statusFilter || undefined,
        limit: 100,
      });
      setLogs(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setError("Failed to load activity history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLogs(); }, [domainFilter, statusFilter]);

  // UX Enforcement: INVENTORY_MASTER_DATA_ACTIVITY_VIEW
  if (!hasPermission("INVENTORY_MASTER_DATA_ACTIVITY_VIEW")) {
    return (
      <div className="p-8 text-center text-slate-500">
        You do not have permission to view Activity History.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Activity History</h3>
          <p className="text-sm text-slate-500 mt-0.5">Audit log of all import and export operations.</p>
        </div>
        <button
          onClick={fetchLogs}
          className="flex items-center gap-2 text-sm text-slate-600 hover:text-indigo-600 border border-slate-200 hover:border-indigo-300 rounded-lg px-3 py-2 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-indigo-500" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <select
          value={domainFilter}
          onChange={e => setDomainFilter(e.target.value)}
          className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        >
          <option value="">All Domains</option>
          {Object.entries(DOMAIN_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        >
          <option value="">All Statuses</option>
          <option value="COMMITTED">Committed</option>
          <option value="DRY_RUN">Dry Run</option>
          <option value="FAILED">Failed</option>
        </select>
      </div>

      {/* Table */}
      <div className="border border-slate-200 rounded-lg overflow-hidden bg-white">
        {loading ? (
          <div className="flex items-center justify-center py-16 gap-3 text-slate-500">
            <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
            <span className="text-sm">Loading activity history…</span>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-16 gap-2 text-red-500">
            <XCircle className="w-5 h-5" />
            <span className="text-sm">{error}</span>
          </div>
        ) : logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 gap-3 text-slate-400">
            <Activity className="w-10 h-10 text-slate-200" />
            <p className="text-sm font-medium">No activity records found.</p>
            <p className="text-xs text-slate-400">Import or export some data to see the audit log here.</p>
          </div>
        ) : (
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-4 py-3 font-medium text-slate-500 uppercase tracking-wider text-xs">Batch ID</th>
                <th className="px-4 py-3 font-medium text-slate-500 uppercase tracking-wider text-xs">Domain</th>
                <th className="px-4 py-3 font-medium text-slate-500 uppercase tracking-wider text-xs">File</th>
                <th className="px-4 py-3 font-medium text-slate-500 uppercase tracking-wider text-xs">Status</th>
                <th className="px-4 py-3 font-medium text-slate-500 uppercase tracking-wider text-xs text-center">Total</th>
                <th className="px-4 py-3 font-medium text-slate-500 uppercase tracking-wider text-xs text-center">Success</th>
                <th className="px-4 py-3 font-medium text-slate-500 uppercase tracking-wider text-xs text-center">Failed</th>
                <th className="px-4 py-3 font-medium text-slate-500 uppercase tracking-wider text-xs">Duration</th>
                <th className="px-4 py-3 font-medium text-slate-500 uppercase tracking-wider text-xs">Started At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {logs.map((log) => {
                const statusConf = STATUS_CONFIG[log.status] || { label: log.status, color: "bg-slate-100 text-slate-600" };
                return (
                  <tr key={log.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{log.batch_id?.slice(0, 12)}…</td>
                    <td className="px-4 py-3">
                      <span className="font-medium text-slate-800">{DOMAIN_LABELS[log.entity_type] || log.entity_type}</span>
                    </td>
                    <td className="px-4 py-3 max-w-[180px] truncate">
                      <div className="flex items-center gap-1.5 text-slate-600">
                        <FileText className="w-3.5 h-3.5 shrink-0 text-slate-400" />
                        <span className="truncate text-xs">{log.filename}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${statusConf.color}`}>
                        {statusConf.label}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center text-slate-700 font-medium">{log.records_processed}</td>
                    <td className="px-4 py-3 text-center">
                      <span className="text-emerald-600 font-semibold">{log.success_count}</span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={log.failure_count > 0 ? "text-red-600 font-semibold" : "text-slate-400"}>{log.failure_count}</span>
                    </td>
                    <td className="px-4 py-3 text-slate-500 text-xs">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {formatDuration(log.start_time, log.end_time)}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-500 text-xs whitespace-nowrap">{formatDate(log.start_time)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
