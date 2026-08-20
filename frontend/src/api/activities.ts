// @ts-nocheck
import { apiClient } from './client';

export interface InventoryItemResponse {
  id: string;
  name: string;
  inventory_code: string;
  type: string;
}

export interface ActivityReference {
  type: string;
  number: string;
  id: string;
}

export interface ActivityResponse {
  id: string;
  activity_type: string;
  activity_name: string;
  date: string;
  inventory_item: InventoryItemResponse;
  quantity: number;
  balance_after_activity: number | null;
  reference: ActivityReference;
  remarks: string | null;
  created_on: string;
}

export interface ActivityListResponse {
  total_count: number;
  items: ActivityResponse[];
}

export interface GetActivitiesParams {
  skip?: number;
  limit?: number;
  movement_type?: string;
  sku_id?: string;
  item_type?: string;
  date_from?: string;
  date_to?: string;
}

export const inventoryActivitiesApi = {
  getActivities: async (params?: GetActivitiesParams): Promise<ActivityListResponse> => {
    const response = await apiClient.get('/inventory/movements/activities', { params });
    // axios interceptor handles unwrapping the standard data object but based on client.ts interceptor:
    // `response => response.data` gives us the SuccessResponse object. 
    // And `response.data.data` is accessed if we don't unwrap. But wait, let's check what `apiClient` returns.
    // If interceptor returns `response.data`, then `response` here is already `SuccessResponse`, so we return `response.data`.
    return response.data;
  },
};
