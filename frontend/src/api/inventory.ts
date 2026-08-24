// @ts-nocheck
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';

export interface InventoryBalanceResponse {
  sku_id: string;
  warehouse_id: string;
  warehouse: string;
  sku_code: string;
  sku_name: string;
  balance: number;
  confidence_score: number;
  in_transit: number;
}

export interface InventoryPositionResponse {
  sku_id: string;
  total_stock: number;
  warehouse_stock: number;
  job_worker_total: number;
  job_workers: { name: string; stock: number }[];
}

interface ListBalancesResponse {
  success: boolean;
  data: InventoryBalanceResponse[];
}

export interface InventoryMovementResponse {
  id: string;
  movement_date: string;
  movement_type: string;
  quantity: number;
  reference_type: string;
  reference_number: string;
}

export interface InventoryLedgerEntry {
  movement: InventoryMovementResponse;
  running_balance: number;
}

export interface InventoryLedgerResponse {
  sku_id: string;
  opening_balance: number;
  entries: InventoryLedgerEntry[];
  closing_balance: number;
  generated_at: string;
}

export interface InventoryConfidenceResponse {
  sku_id: string;
  confidence_score: number;
  positive_signals: string[];
  negative_signals: string[];
}

export function useInventoryBalances() {
  return useQuery({
    queryKey: ['inventory-balances'],
    queryFn: async () => {
      // apiClient interceptor unwraps AxiosResponse into the JSON body { success, data }
      const payload = await apiClient.get<any>('/inventory/balances') as any;
      return Array.isArray(payload) ? payload : (payload?.data || []);
    },
  });
}

export function useInventoryLedger(skuId: string | null) {
  return useQuery({
    queryKey: ['inventory-ledger', skuId],
    queryFn: async () => {
      if (!skuId) return null;
      const payload = await apiClient.get<any>(`/inventory/ledger/${skuId}`) as any;
      return payload?.data;
    },
    enabled: !!skuId,
  });
}

export function useInventoryConfidence(skuId: string | null) {
  return useQuery({
    queryKey: ['inventory-confidence', skuId],
    queryFn: async () => {
      if (!skuId) return null;
      const payload = await apiClient.get<any>(`/inventory/confidence/${skuId}`) as any;
      return payload?.data;
    },
    enabled: !!skuId,
  });
}

export function useDashboardKPIs() {
  return useQuery({
    queryKey: ['inventory-dashboard-kpis'],
    queryFn: async () => {
      const payload = await apiClient.get<any>('/inventory/dashboard/kpis') as any;
      return payload?.data || {};
    }
  });
}

export function useDashboardExceptions() {
  return useQuery({
    queryKey: ['inventory-dashboard-exceptions'],
    queryFn: async () => {
      const payload = await apiClient.get<any>('/inventory/dashboard/exceptions') as any;
      return payload?.data || [];
    }
  });
}

export interface ManualAdjustmentRequest {
  warehouse_id: string;
  sku_id: string;
  quantity: number;
  reason: string;
  reference_number: string;
  adjustment_date: string;
}

export interface StockCountAdjustmentRequest {
  warehouse_id: string;
  sku_id: string;
  system_quantity: number;
  physical_count: number;
  difference: number;
  stock_count_reference: string;
  count_date: string;
}

export function useCreateManualAdjustment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ManualAdjustmentRequest) => {
      const response = await apiClient.post<any>('/inventory/movements/manual-adjustments', data);
      return response;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['inventory-balances'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-ledger', variables.sku_id] });
      queryClient.invalidateQueries({ queryKey: ['inventory-confidence', variables.sku_id] });
      queryClient.invalidateQueries({ queryKey: ['inventory-activities'] });
    },
  });
}

export function useCreateStockCountAdjustment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: StockCountAdjustmentRequest) => {
      const response = await apiClient.post<any>('/inventory/movements/stock-counts', data);
      return response;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['inventory-balances'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-ledger', variables.sku_id] });
      queryClient.invalidateQueries({ queryKey: ['inventory-confidence', variables.sku_id] });
      queryClient.invalidateQueries({ queryKey: ['inventory-activities'] });
    },
  });
}

export function useInventoryPosition() {
  return useQuery({
    queryKey: ['inventory-position'],
    queryFn: async () => {
      const response = await apiClient.get<any>('/inventory/position');
      return response.data || [];
    },
  });
}
