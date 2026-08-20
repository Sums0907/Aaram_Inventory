// @ts-nocheck
import { useQuery } from '@tanstack/react-query'
import { apiClient } from './client'

export interface JobWorkerInventoryResponse {
  job_worker_id: string
  item_id: string
  issued_quantity: number
  consumed_quantity: number
  returned_quantity: number
  pending_quantity: number
  last_movement_id?: string
}

export interface JobWorkerInventoryDetailResponse extends JobWorkerInventoryResponse {
  job_worker_name: string
  item_code: string
  item_name: string
  uom: string
}

export interface JobWorkerStockKPIResponse {
  job_workers_with_stock: number
  items_with_pending_stock: number
  total_pending_lines: number
}

export interface JobWorkerPendingStockResponse {
  kpis: JobWorkerStockKPIResponse
  items: JobWorkerInventoryDetailResponse[]
}

export interface JobWorkIssueCreate {
  job_worker_id: string
  item_id: string
  quantity: number
  warehouse_id?: string
}

export interface JobWorkReturnCreate {
  job_worker_id: string
  item_id: string
  quantity: number
  warehouse_id?: string
}

export interface InventoryTransformationRecordResponse {
  id: string
  source_item_id: string
  destination_item_id: string
  quantity_consumed: number
  quantity_produced: number
  job_worker_id?: string
  reference_document: string
  transformation_reason: string
  created_on: string
}

// -----------------------------------------------------------------------
// Stock Custody Ledger types
// -----------------------------------------------------------------------
export interface CustodyLedgerEntry {
  date: string
  reference: string
  particular: string   // "Material Issued" | "Material Consumed" | "Material Returned"
  issue: string        // decimal string e.g. "100.00", "0.00" when not applicable
  consumption: string
  return: string
  pending: string
}

export interface CustodyLedgerItem {
  item_id: string
  item_code: string
  item_name: string
  uom: string
  entries: CustodyLedgerEntry[]
}

export interface CustodyLedgerResponse {
  supplier_id: string
  supplier_name: string
  items: CustodyLedgerItem[]
}

// -----------------------------------------------------------------------
// Query hooks
// -----------------------------------------------------------------------

export const usePendingStock = (supplierId: string) => {
  return useQuery({
    queryKey: ['job-works', 'pending-stock', supplierId],
    queryFn: async () => {
      if (!supplierId) return [];
      const { data } = await apiClient.get<{ data: JobWorkerInventoryResponse[] }>(
        `/inventory/job-works/suppliers/${supplierId}/pending-stock`
      )
      return data
    },
    enabled: !!supplierId,
  })
}

export const useAllPendingStock = () => {
  return useQuery({
    queryKey: ['job-works', 'all-pending-stock'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: JobWorkerPendingStockResponse }>(
        `/inventory/job-works/pending-stock`
      )
      return data
    },
  })
}

export const useJobWorkerActivities = (supplierId: string) => {
  return useQuery({
    queryKey: ['job-works', 'activities', supplierId],
    queryFn: async () => {
      if (!supplierId) return [];
      const { data } = await apiClient.get<{ data: any[] }>(
        `/inventory/job-works/suppliers/${supplierId}/activities`
      )
      return data
    },
    enabled: !!supplierId,
  })
}

export const useAllJobWorkerActivities = () => {
  return useQuery({
    queryKey: ['job-works', 'all-activities'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: any[] }>(
        `/inventory/job-works/activities`
      )
      return data
    }
  })
}

export const useTransformations = () => {
  return useQuery({
    queryKey: ['job-works', 'transformations'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: InventoryTransformationRecordResponse[] }>(
        `/inventory/transformations`
      )
      return data
    }
  })
}

/** Stock Custody Ledger — full chronological passbook for one Job Worker */
export const useCustodyLedger = (supplierId: string, enabled = true) => {
  return useQuery({
    queryKey: ['job-works', 'custody-ledger', supplierId],
    queryFn: async () => {
      // apiClient interceptor already unwraps response to response.data
      // so the shape here is: { success, error, data: CustodyLedgerResponse }
      const response = await apiClient.get<{ data: CustodyLedgerResponse }>(
        `/inventory/job-works/suppliers/${supplierId}/custody-ledger`
      )
      return (response as any).data as CustodyLedgerResponse
    },
    enabled: !!supplierId && enabled,
  })
}

import { useMutation, useQueryClient } from '@tanstack/react-query'

export const useCreateJobWorkIssue = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: JobWorkIssueCreate) => {
      const { data } = await apiClient.post<{ data: any }>(
        `/inventory/job-works/issues`,
        payload
      )
      return data.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['job-works', 'pending-stock', variables.job_worker_id] })
      queryClient.invalidateQueries({ queryKey: ['job-works', 'custody-ledger', variables.job_worker_id] })
      queryClient.invalidateQueries({ queryKey: ['inventory', 'balances'] })
    }
  })
}

export const useCreateJobWorkReturn = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: JobWorkReturnCreate) => {
      const { data } = await apiClient.post<{ data: any }>(
        `/inventory/job-works/returns`,
        payload
      )
      return data.data
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['job-works', 'pending-stock', variables.job_worker_id] })
      queryClient.invalidateQueries({ queryKey: ['job-works', 'custody-ledger', variables.job_worker_id] })
      queryClient.invalidateQueries({ queryKey: ['inventory', 'balances'] })
    }
  })
}
