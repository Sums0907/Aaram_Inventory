// @ts-nocheck
import { apiClient as api } from "./client"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"

export interface PaginatedResponse<T> {
  data: T[]
  meta: {
    total: number
    page: number
    size: number
    pages: number
  }
}

export interface SuccessResponse<T> {
  data: T
  message?: string
}


export interface Supplier {
  id: string
  name: string
  gstin?: string
  contact_number?: string
  email?: string
  address?: string
  remarks?: string
  is_job_worker: boolean
  created_on: string
  updated_on: string
}

export interface CreateSupplierInput {
  name: string
  gstin?: string
  contact_number?: string
  email?: string
  address?: string
  remarks?: string
  is_job_worker: boolean
}

export interface UpdateSupplierInput extends Partial<CreateSupplierInput> {
  id: string
}

export const supplierKeys = {
  all: ["suppliers"] as const,
  lists: () => [...supplierKeys.all, "list"] as const,
  list: (filters: string) => [...supplierKeys.lists(), { filters }] as const,
  details: () => [...supplierKeys.all, "detail"] as const,
  detail: (id: string) => [...supplierKeys.details(), id] as const,
}

// Queries
export function useSuppliers(skip = 0, limit = 100) {
  return useQuery({
    queryKey: supplierKeys.list(`skip=${skip}&limit=${limit}`),
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<Supplier>>(`/masters/suppliers`, {
        params: { skip, limit },
      })
      return response as any as PaginatedResponse<Supplier>
    },
  })
}

export function useSupplier(id: string) {
  return useQuery({
    queryKey: supplierKeys.detail(id),
    queryFn: async () => {
      const response = await api.get<SuccessResponse<Supplier>>(`/masters/suppliers/${id}`)
      const responseData = response as any as SuccessResponse<Supplier>
      return responseData.data
    },
    enabled: !!id,
  })
}

// Mutations
export function useCreateSupplier() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (newSupplier: CreateSupplierInput) => {
      const response = await api.post<SuccessResponse<Supplier>>("/masters/suppliers", newSupplier)
      const responseData = response as any as SuccessResponse<Supplier>
      return responseData.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: supplierKeys.lists() })
    },
  })
}

export function useUpdateSupplier() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (supplier: UpdateSupplierInput) => {
      const { id, ...updateData } = supplier
      const response = await api.put<SuccessResponse<Supplier>>(`/masters/suppliers/${id}`, updateData)
      const responseData = response as any as SuccessResponse<Supplier>
      return responseData.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: supplierKeys.lists() })
      queryClient.invalidateQueries({ queryKey: supplierKeys.detail(data.id) })
    },
  })
}

export function useDeleteSupplier() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.delete<SuccessResponse<null>>(`/masters/suppliers/${id}`)
      return response as any as SuccessResponse<null>
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: supplierKeys.lists() })
    },
  })
}
