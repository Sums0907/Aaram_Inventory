import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';

export interface InventoryBalanceResponse {
  warehouse: string;
  sku_code: string;
  sku_name: string;
  balance: number;
  in_transit: number;
}

interface ListBalancesResponse {
  success: boolean;
  data: InventoryBalanceResponse[];
}

const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0IiwidXNlcm5hbWUiOiJkZW1vIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxODE3NDcyNjA2fQ.J4sb028IFN8h3OBlYq1RatBHZKs0SH6p8eGuKVXKp_c";

export function useInventoryBalances() {
  return useQuery({
    queryKey: ['inventory-balances'],
    queryFn: async () => {
      const response = await apiClient.get<ListBalancesResponse>('/inventory/balances', {
        headers: { Authorization: `Bearer ${TOKEN}` }
      });
      return response.data.data;
    },
  });
}
