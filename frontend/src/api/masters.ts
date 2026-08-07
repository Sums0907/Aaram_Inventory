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
  pricing: PricingInfo | null;
  images: ImageInfo[];
  attribute_values: Record<string, string>;
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

const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MDJlYWMxMS0yMWUyLTRkNTMtYTllOS0yYmEyMWJjMDRiOWEiLCJ1c2VybmFtZSI6ImRlbW8iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE4MTc0NzI2MDZ9._cuQTw-7zam00atnpTsxsklre2ZsOFVKPkbvChQpSMM";

export function useSKUs() {
  return useQuery({
    queryKey: ['masters-skus'],
    queryFn: async () => {
      const payload = await apiClient.get<any>('/masters/skus', {
        headers: { Authorization: `Bearer ${TOKEN}` }
      }) as any;
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
      const payload = await apiClient.get<any>('/masters/products', {
        headers: { Authorization: `Bearer ${TOKEN}` }
      }).catch(() => ({ data: [] })) as any;
      return (payload?.data || []) as ProductInfo[];
    },
  });
}

export function useCategories(itemType?: string) {
  return useQuery({
    queryKey: ['masters-categories', itemType],
    queryFn: async () => {
      const url = itemType ? `/masters/categories?item_type=${itemType}` : '/masters/categories';
      const payload = await apiClient.get<any>(url, {
        headers: { Authorization: `Bearer ${TOKEN}` }
      }).catch(() => ({ data: [] })) as any;
      return (payload?.data || []) as CategoryInfo[];
    },
  });
}

export function useCreateCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: { category_name: string; category_code?: string; item_type: string; parent_id?: string }) => {
      const payload = await apiClient.post<any>('/masters/categories', data, {
        headers: { Authorization: `Bearer ${TOKEN}` }
      });
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
      const payload = await apiClient.post<any>('/masters/inventory-items', data, {
        headers: { Authorization: `Bearer ${TOKEN}` }
      });
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
      const payload = await apiClient.post<any>('/masters/skus', data, {
        headers: { Authorization: `Bearer ${TOKEN}` }
      });
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
      const payload = await apiClient.put<any>(`/masters/skus/${id}`, data, {
        headers: { Authorization: `Bearer ${TOKEN}` }
      });
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
      const payload = await apiClient.patch<any>(`/masters/skus/${id}/deactivate`, {}, {
        headers: { Authorization: `Bearer ${TOKEN}` }
      });
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
      const payload = await apiClient.patch<any>(`/masters/skus/${id}/archive`, {}, {
        headers: { Authorization: `Bearer ${TOKEN}` }
      });
      return payload?.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['masters-skus'] });
    },
  });
}
