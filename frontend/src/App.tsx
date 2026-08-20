// @ts-nocheck
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ErrorBoundary } from "react-error-boundary"
import { Toaster } from "@/components/ui/toaster"

import { AppLayout } from "@/components/layout/AppLayout"
import { InventoryLayout } from "@/components/layout/InventoryLayout"
import { DashboardPage } from "@/pages/DashboardPage"
import { ImportsPage } from "@/pages/ImportsPage"
import { MatchingPage } from "@/pages/MatchingPage"
import { InventoryExplorerDashboard } from "@/pages/inventory/InventoryExplorerDashboard"
import { InventoryPage } from "@/pages/inventory/InventoryDashboard"
import { ProductsPage } from "@/pages/inventory/ProductsPage"
import { SuppliersPage } from "@/pages/inventory/SuppliersPage"
import { JobWorkerStockPage } from "@/pages/inventory/JobWorkerStockPage"
import { GoodsReceiptsPage } from "@/pages/inventory/GoodsReceiptsPage"
import { PurchaseReturnsPage } from "@/pages/inventory/PurchaseReturnsPage"
import { ActivityPage } from "@/pages/inventory/ActivityPage"
import { PhysicalVerificationPage } from "@/pages/inventory/PhysicalVerificationPage"
import { AdjustmentsPage } from "@/pages/inventory/AdjustmentsPage"
import { ExceptionsPage } from "@/pages/inventory/ExceptionsPage"
import { ConfidencePage } from "@/pages/inventory/ConfidencePage"
import { DailyUpdatePage } from "@/pages/inventory/DailyUpdatePage"
import { AccountingLayout } from "@/components/layout/AccountingLayout"
import { AccountingDashboardPage } from "@/pages/AccountingDashboardPage"
import { JobWorkerAccountingDashboard } from "@/pages/accounting/job-worker-accounting/JobWorkerAccountingDashboard"
import { JobWorkerPayablesWorkspace } from "@/pages/accounting/job-worker-accounting/JobWorkerPayablesWorkspace"
import { JobWorkRatesPage } from "@/pages/accounting/job-worker-accounting/JobWorkRatesPage"
import { ExportsPage } from "@/pages/ExportsPage"
import { SettingsPage } from "@/pages/SettingsPage"
import { BOMSetupPage } from "@/pages/inventory/BOMSetupPage"
import { TransformationsPage } from "@/pages/inventory/TransformationsPage"
import UnitsOfMeasurePage from "@/pages/inventory/UnitsOfMeasurePage"
import { MasterDataOperationsPage } from "@/pages/master-data/MasterDataOperationsPage"

const queryClient = new QueryClient()

function GlobalErrorFallback({ error, resetErrorBoundary }: any) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="max-w-md w-full bg-white rounded-xl shadow-sm border border-red-100 p-8 text-center">
        <div className="mx-auto w-12 h-12 bg-red-100 text-red-600 rounded-full flex items-center justify-center mb-4">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">Something went wrong</h2>
        <p className="text-sm text-slate-500 mb-6">
          The application encountered an unexpected error. Don't worry, your data is safe.
        </p>
        <button 
          onClick={resetErrorBoundary}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors w-full"
        >
          Reload Application
        </button>
      </div>
    </div>
  );
}

import { ProtectedRoute } from "@/components/auth/ProtectedRoute"

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ErrorBoundary FallbackComponent={GlobalErrorFallback} onReset={() => window.location.href = '/'}>
          <Routes>
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="imports" element={<ImportsPage />} />
              <Route path="matching" element={<MatchingPage />} />
              
              {/* Inventory Workspace */}
              <Route path="inventory" element={<InventoryLayout />}>
                <Route index element={<InventoryPage />} />
                <Route path="catalog" element={<InventoryExplorerDashboard />} />
                <Route path="daily-update" element={<DailyUpdatePage />} />
                <Route path="products" element={<ProductsPage />} />
                <Route path="suppliers" element={<SuppliersPage />} />
                <Route path="job-worker-stock" element={<JobWorkerStockPage />} />
                <Route path="goods-receipts" element={<GoodsReceiptsPage />} />
                <Route path="purchase-returns" element={<PurchaseReturnsPage />} />
                <Route path="activity" element={<ActivityPage />} />
                <Route path="verification" element={<PhysicalVerificationPage />} />
                <Route path="adjustments" element={<AdjustmentsPage />} />
                <Route path="exceptions" element={<ExceptionsPage />} />
                <Route path="confidence" element={<ConfidencePage />} />
                <Route path="boms" element={<BOMSetupPage />} />
                <Route path="transformations" element={<TransformationsPage />} />
                <Route path="units-of-measure" element={<UnitsOfMeasurePage />} />
              </Route>

              <Route path="accounting" element={<AccountingLayout />}>
                <Route index element={<AccountingDashboardPage />} />
                <Route path="job-worker">
                  <Route path="dashboard" element={<JobWorkerAccountingDashboard />} />
                  <Route path="payables" element={<JobWorkerPayablesWorkspace />} />
                  <Route path="rates" element={<JobWorkRatesPage />} />
                </Route>
              </Route>
              <Route path="exports" element={<ExportsPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="admin/master-data" element={<MasterDataOperationsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
              </Route>
            </Route>
          </Routes>

        </ErrorBoundary>
        <Toaster />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
