// @ts-nocheck
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';

export interface ProductInfo {
  id: string;
  product_code: string;
  product_name: string;
  brand: string | null;
  product_type: string | null;
  item_type?: string;
  category_id?: string;
  status: string;
}

export interface UnitOfMeasureInfo {
  id: string;
  unit_code: string;
  unit_name: string;
  unit_type?: "INTEGER" | "DECIMAL";
}

export interface PricingInfo {
  selling_price: number;
  mrp: number;
  cost_price: number;
  gst_percentage: number;
  hsn_code: string | null;
}

export interface CreateCategoryPayload {
  category_name: string;
  category_code?: string;
  item_type: string;
  parent_id?: string;
  attributes?: string[];
}

export interface CategoryInfo {
  id: string;
  category_code: string;
  category_name: string;
  item_type: string;
  parent_id?: string;
  attributes?: { attribute_name: string; is_required: boolean }[];
  status: string;
}

export interface ImageInfo {
  image_url: string;
  display_order: number;
}

export interface SKUResponse {
  id: string;
  item_code: string;
  sku_code: string | null;
  status: string;
  size: string | null;
  color: string | null;
  pattern: string | null;
  material: string | null;
  thread_count: string | null;
  barcode: string | null;
  product: ProductInfo | null;
  uom: UnitOfMeasureInfo | null;
  pricing: PricingInfo | null;
  images: ImageInfo[];
  attribute_values: Record<string, string>;
  updated_on?: string;
  has_bom?: boolean;
}

export interface InventoryItemCreatePayload {
  item_type: string;
  category_id?: string;
  new_category_name?: string;
  product_id?: string;
  new_product_name?: string;
  item_code: string;
  sku_code?: string;
  size?: string;
  color?: string;
  pattern?: string;
  material?: string;
  thread_count?: string;
  barcode?: string;
  attribute_values?: Record<string, string>;
  uom_id?: string;
}

export interface SKUCreatePayload {
  item_code: string;
  sku_code?: string;
  product_id: string;
  size?: string;
  color?: string;
  pattern?: string;
  material?: string;
  thread_count?: string;
  barcode?: string;
  attribute_values?: Record<string, string>;
}

export interface SKUUpdatePayload {
  size?: string;
  color?: string;
  pattern?: string;
  material?: string;
  thread_count?: string;
  barcode?: string;
  attribute_values?: Record<string, string>;
}

export function useSKUs() {
  return useQuery({
    queryKey: ['masters-skus'],
    queryFn: async () => {
      const payload = await apiClient.get<any>('/masters/skus') as any;
      return (payload?.data || []) as SKUResponse[];
    },
  });
}

export function useProducts() {
  return useQuery({
    queryKey: ['masters-products'],
    queryFn: async () => {
      // Mocking for now since there might not be a direct products endpoint matching SKUResponse structure.
      // But let's call it and hope it returns the list of products for dropdown selection.
      const payload = await apiClient.get<any>('/masters/products').catch(() => ({ data: [] })) as any;
      return (payload?.data || []) as ProductInfo[];
    },
  });
}

export function useCategories(itemType?: string) {
  return useQuery({
    queryKey: ['masters-categories', itemType],
    queryFn: async () => {
      const url = itemType ? `/masters/categories?item_type=${itemType}` : '/masters/categories';
      const payload = await apiClient.get<any>(url).catch(() => ({ data: [] })) as any;
      return (payload?.data || []) as CategoryInfo[];
    },
  });
}

export interface UnitOfMeasureInfo {
  id: string;
  unit_code: string;
  unit_name: string;
  short_name: string;
  description?: string;
  status: string;
  unit_type?: "INTEGER" | "DECIMAL";
}

export function useUnitsOfMeasure() {
  return useQuery({
    queryKey: ['masters-uoms'],
    queryFn: async () => {
      const payload = await apiClient.get<any>('/masters/units-of-measure').catch(() => ({ data: [] })) as any;
      return (payload?.data || []) as UnitOfMeasureInfo[];
    },
  });
}

export function useCreateUOM() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Omit<UnitOfMeasureInfo, 'id' | 'status'>) => {
      const payload = await apiClient.post<any>('/masters/units-of-measure', data);
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-uoms'] });
    },
  });
}

export function useUpdateUOM() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string, data: Partial<UnitOfMeasureInfo> }) => {
      const payload = await apiClient.put<any>(`/masters/units-of-measure/${id}`, data);
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-uoms'] });
    },
  });
}

export function useActivateUOM() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const payload = await apiClient.patch<any>(`/masters/units-of-measure/${id}/activate`, {});
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-uoms'] });
    },
  });
}

export function useDeactivateUOM() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const payload = await apiClient.patch<any>(`/masters/units-of-measure/${id}/deactivate`, {});
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-uoms'] });
    },
  });
}

export function useCreateCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: { category_name: string; category_code?: string; item_type: string; parent_id?: string }) => {
      const payload = await apiClient.post<any>('/masters/categories', data);
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-categories'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-hierarchy'] });
    },
  });
}

export function useUpdateCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string, data: any }) => {
      const payload = await apiClient.put<any>(`/masters/categories/${id}`, data);
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-categories'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-hierarchy'] });
    },
  });
}

export function useArchiveCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const payload = await apiClient.patch<any>(`/masters/categories/${id}/archive`, {});
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-categories'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-hierarchy'] });
    },
  });
}

export function useDeleteCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const payload = await apiClient.delete<any>(`/masters/categories/${id}`);
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-categories'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-hierarchy'] });
    },
  });
}

export function useCreateInventoryItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: InventoryItemCreatePayload) => {
      const payload = await apiClient.post<any>('/masters/inventory-items', data);
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-skus'] });
      queryClient.invalidateQueries({ queryKey: ['masters-products'] });
      queryClient.invalidateQueries({ queryKey: ['masters-categories'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-hierarchy'] });
    },
  });
}

export function useCreateSKU() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: SKUCreatePayload) => {
      const payload = await apiClient.post<any>('/masters/skus', data);
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-skus'] });
    },
  });
}

export function useUpdateSKU() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: SKUUpdatePayload }) => {
      const payload = await apiClient.put<any>(`/masters/skus/${id}`, data);
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-skus'] });
    },
  });
}

export function useDeactivateSKU() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const payload = await apiClient.patch<any>(`/masters/skus/${id}/deactivate`, {});
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-skus'] });
    },
  });
}

export function useArchiveSKU() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const payload = await apiClient.patch<any>(`/masters/skus/${id}/archive`, {});
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-skus'] });
    },
  });
}

export function useArchiveProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const payload = await apiClient.patch<any>(`/masters/products/${id}/archive`, {});
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-products'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-hierarchy'] });
    }
  });
}

export function useUpdateProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, data }: { id: string, data: { product_name: string } }) => {
      const payload = await apiClient.put<any>(`/masters/products/${id}`, data);
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-products'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-hierarchy'] });
    },
  });
}

export function useDeleteProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const payload = await apiClient.delete<any>(`/masters/products/${id}`);
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-products'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-hierarchy'] });
    },
  });
}
