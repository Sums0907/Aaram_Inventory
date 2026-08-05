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
      // Valid token for Version 1 MVP demonstration (expires in 1 year)
      const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0IiwidXNlcm5hbWUiOiJkZW1vIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxODE3NDcyNjA2fQ.J4sb028IFN8h3OBlYq1RatBHZKs0SH6p8eGuKVXKp_c";
      
      const response = await apiClient.get<SummaryResponse>('/dashboard/summary', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.data;
    },
    refetchInterval: 10000, // Refetch every 10 seconds to auto-update pipeline status
  });
}
