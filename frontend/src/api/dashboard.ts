// @ts-nocheck
import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';

export interface VerificationDetails {
  status: string;
  checks: {
    golden_dataset_matches: boolean;
    journals_balanced: boolean;
  };
}

export interface DashboardSummary {
  "Total Revenue": number;
  "Total Settlements": number;
  "Platform Fees": number;
  "Sales Orders": number;
  "Tax Invoices": number;
  "Fulfillment Rate": number;
  "Golden Dataset Status": string;
  "Verification Details": VerificationDetails;
}

interface SummaryResponse {
  success: boolean;
  data: DashboardSummary;
}

export function useDashboardSummary() {
  return useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: async () => {
      // The apiClient interceptor already returns the response payload (response.data).
      // Since it returns SummaryResponse directly, we just return response.data to get DashboardSummary.
      const response = await apiClient.get<SummaryResponse>('/dashboard/summary');
      return (response as any).data;
    },
    refetchInterval: 10000, // Refetch every 10 seconds to auto-update pipeline status
  });
}
