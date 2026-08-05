import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';

export interface ImportJobResponse {
  id: string;
  integration_id: string | null;
  job_type: string;
  status: string;
  started_at: string | null;
  finished_at: string | null;
  created_on: string;
  updated_on: string;
}

interface ListImportJobsResponse {
  success: boolean;
  data: ImportJobResponse[];
}

const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0IiwidXNlcm5hbWUiOiJkZW1vIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxODE3NDcyNjA2fQ.J4sb028IFN8h3OBlYq1RatBHZKs0SH6p8eGuKVXKp_c";

export function useImportJobs() {
  return useQuery({
    queryKey: ['import-jobs'],
    queryFn: async () => {
      const response = await apiClient.get<ListImportJobsResponse>('/data-ingestion/import-jobs', {
        headers: { Authorization: `Bearer ${TOKEN}` }
      });
      return response.data.data;
    },
    refetchInterval: 5000,
  });
}
