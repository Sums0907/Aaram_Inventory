import { useQuery } from "@tanstack/react-query";
import { apiClient } from "./client";
import type { CategoryInfo, ProductInfo } from "./masters";

export interface HierarchyResponse {
  categories: CategoryInfo[];
  products: ProductInfo[];
}

export const fetchInventoryHierarchy = async (onlyArchived: boolean = false): Promise<HierarchyResponse> => {
  const response = await apiClient.get<{ data: HierarchyResponse }>(`/masters/hierarchy?only_archived=${onlyArchived}`);
  return (response as any).data;
};

export const useInventoryHierarchy = (onlyArchived: boolean = false) => {
  return useQuery({
    queryKey: ["inventory-hierarchy", onlyArchived],
    queryFn: () => fetchInventoryHierarchy(onlyArchived),
  });
};
