import { useQuery } from '@tanstack/react-query'
import { apiClient } from './client'

export interface BOMItemResponse {
  component_item_id: string
  quantity: number
  unit_of_measure: string
}

export interface BOMResponse {
  id: string
  bom_number: string
  bom_name?: string
  target_item_id: string
  target_quantity: number
  status: string
  items: BOMItemResponse[]
}

export const useBOMs = () => {
  return useQuery({
    queryKey: ['masters', 'boms'],
    queryFn: async () => {
      const res = await apiClient.get<{ data: BOMResponse[] }>('/masters/boms')
      return (res as any).data as BOMResponse[]
    }
  })
}

import { useMutation, useQueryClient } from '@tanstack/react-query'

export interface BOMItemCreate {
  component_item_id: string
  quantity: number
  unit_of_measure: string
  wastage_percentage?: number
  tolerance_percentage?: number
}

export interface BOMCreate {
  bom_number: string
  bom_name?: string
  target_item_id: string
  target_quantity: number
  status: string
  items: BOMItemCreate[]
}

export const useCreateBOM = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: BOMCreate) => {
      const res = await apiClient.post<{ data: BOMResponse }>('/masters/boms', data)
      return (res as any).data as BOMResponse
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters', 'boms'] })
      queryClient.invalidateQueries({ queryKey: ['masters', 'skus'] })
    }
  })
}

export const useArchiveBOM = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (bomId: string) => {
      const res = await apiClient.post<{ data: boolean }>(`/masters/boms/${bomId}/archive`)
      return (res as any).data as boolean
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters', 'boms'] })
    }
  })
}

export const useRestoreBOM = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (bomId: string) => {
      const res = await apiClient.post<{ data: boolean }>(`/masters/boms/${bomId}/restore`)
      return (res as any).data as boolean
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters', 'boms'] })
    }
  })
}
