import { useQuery } from "@tanstack/react-query";
import { apiClient } from "./client";

export interface Warehouse {
  id: string;
  warehouse_name: string;
  location?: string;
  capacity?: number;
  is_active: boolean;
}

export const useGetWarehouses = () => {
  return useQuery({
    queryKey: ["warehouses"],
    queryFn: async (): Promise<Warehouse[]> => {
      const payload = await apiClient.get<any>("/masters/warehouses").catch(() => ({ data: [] })) as any;
      return (payload?.data || []) as Warehouse[];
    },
  });
};
