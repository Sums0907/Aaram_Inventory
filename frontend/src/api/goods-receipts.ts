// @ts-nocheck
import { apiClient as api } from "./client"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import type { PaginatedResponse, SuccessResponse } from "./suppliers" // Reusing types

export interface GoodsReceiptItem {
  id?: string
  sku_id: string
  quantity: number
  unit_of_measure?: string
}

export interface GoodsReceipt {
  id: string
  grn_number: string
  supplier_id: string
  warehouse_id: string
  receipt_date: string
  invoice_number?: string
  challan_number?: string
  remarks?: string
  status: string
  created_on: string
  updated_on: string
  items: GoodsReceiptItem[]
}

export interface CreateGoodsReceiptInput {
  grn_number: string
  supplier_id: string
  warehouse_id: string
  receipt_date: string
  invoice_number?: string
  challan_number?: string
  remarks?: string
  items: GoodsReceiptItem[]
}

export const grnKeys = {
  all: ["goods-receipts"] as const,
  lists: () => [...grnKeys.all, "list"] as const,
  list: (filters: string) => [...grnKeys.lists(), { filters }] as const,
  details: () => [...grnKeys.all, "detail"] as const,
  detail: (id: string) => [...grnKeys.details(), id] as const,
}

// Queries
export function useGoodsReceipts(skip = 0, limit = 100) {
  return useQuery({
    queryKey: grnKeys.list(`skip=${skip}&limit=${limit}`),
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<GoodsReceipt>>(`/inventory/goods-receipts`, {
        params: { skip, limit },
      })
      return response as any as PaginatedResponse<GoodsReceipt>
    },
  })
}

export function useGoodsReceipt(id: string) {
  return useQuery({
    queryKey: grnKeys.detail(id),
    queryFn: async () => {
      const response = await api.get<SuccessResponse<GoodsReceipt>>(`/inventory/goods-receipts/${id}`)
      const responseData = response as any as SuccessResponse<GoodsReceipt>
      return responseData.data
    },
    enabled: !!id,
  })
}

// Mutations
export function useCreateGoodsReceipt() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (newGRN: CreateGoodsReceiptInput) => {
      const response = await api.post<SuccessResponse<GoodsReceipt>>("/inventory/goods-receipts", newGRN)
      const responseData = response as any as SuccessResponse<GoodsReceipt>
      return responseData.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: grnKeys.lists() })
      // Since creating a GRN updates stock, invalidate inventory balances too
      queryClient.invalidateQueries({ queryKey: ['inventory-balances'] })
    },
  })
}
