import { useQuery } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { CategoryInfo, ProductInfo } from "./masters";

export interface HierarchyResponse {
  categories: CategoryInfo[];
  products: ProductInfo[];
}

export const fetchInventoryHierarchy = async (): Promise<HierarchyResponse> => {
  const response = await apiClient.get<{ data: HierarchyResponse }>("/masters/hierarchy");
  return (response as any).data;
};

export const useInventoryHierarchy = () => {
  return useQuery({
    queryKey: ["inventory-hierarchy"],
    queryFn: fetchInventoryHierarchy,
  });
};
