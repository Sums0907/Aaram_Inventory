// @ts-nocheck
import { apiClient } from './client';

export interface ExceptionInventoryItem {
  inventory_code: string;
  name: string;
}

export interface EnrichedExceptionResponse {
  id: string;
  exception_number: string;
  warehouse_id: string;
  sku_id: string;
  exception_date: string;
  source_system: string;
  expected_quantity: number;
  actual_quantity: number;
  difference: number;
  status: string;
  resolution_notes: string | null;
  created_on: string;
  inventory_item: ExceptionInventoryItem;
}

export interface ExceptionListResponse {
  total_count: number;
  items: EnrichedExceptionResponse[];
}

export interface ResolveExceptionRequest {
  resolution_notes: string;
}

export const exceptionsApi = {
  getExceptions: async (): Promise<ExceptionListResponse> => {
    const response = await apiClient.get('/inventory/exceptions');
    return response.data;
  },

  resolveException: async (id: string, data: ResolveExceptionRequest): Promise<EnrichedExceptionResponse> => {
    const response = await apiClient.post(`/inventory/exceptions/${id}/resolve`, data);
    return response.data;
  }
};
