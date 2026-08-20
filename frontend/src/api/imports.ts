// @ts-nocheck
import { useQuery, useMutation } from '@tanstack/react-query';
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
  file_path: string | null;
}

interface ListImportJobsResponse {
  success: boolean;
  data: ImportJobResponse[];
}


export function useImportJobs() {
  return useQuery({
    queryKey: ['import-jobs'],
    queryFn: async () => {
      const response = await apiClient.get<ListImportJobsResponse>('/data-ingestion/import-jobs');
      return response.data.data;
    },
    refetchInterval: 5000,
  });
}

export interface SyncRequest {
  integration_id: string;
  period_start?: string;
  period_end?: string;
  report_type?: string;
}

export function useSyncShopDeck() {
  return useMutation({
    mutationFn: async (data: SyncRequest) => {
      const response = await apiClient.post<any>('/shopdeck/sync', data);
      return response.data;
    }
  });
}

export interface ImportJobPreview {
  report_date_min: string | null;
  report_date_max: string | null;
  total_orders: number;
  total_skus: number;
  units_sold: number;
  units_returned: number;
}

export function useImportJobPreview(jobId: string | null) {
  return useQuery({
    queryKey: ['import-job-preview', jobId],
    queryFn: async () => {
      if (!jobId) return null;
      const response = await apiClient.get<{success: boolean, data: ImportJobPreview}>(`/data-ingestion/import-jobs/${jobId}/preview`);
      return (response as any).data;
    },
    enabled: !!jobId
  });
}

export interface DynamicReportWindowResponse {
  required_report_start_date: string | null;
  required_report_end_date: string | null;
  oldest_active_order_date: string | null;
  oldest_active_order_id: string | null;
  active_order_count: number;
  reason: string;
}

export function useReportWindow() {
  return useQuery({
    queryKey: ['shopdeck-report-window'],
    queryFn: async () => {
      const response = await apiClient.get<{success: boolean, data: DynamicReportWindowResponse}>('/operations/lifecycle/shopdeck-reports/window');
      return (response as any).data;
    }
  });
}

export function useUploadShopDeckOrders() {
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await apiClient.post<{success: boolean, data: ImportJobResponse}>('/data-ingestion/shopdeck/orders', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return (response as any).data;
    }
  });
}

export function useCommitImportJob() {
  return useMutation({
    mutationFn: async (jobId: string) => {
      await apiClient.post(`/data-ingestion/import-jobs/${jobId}/approve`);
      await apiClient.post(`/data-ingestion/import-jobs/${jobId}/commit`);
      return true;
    }
  });
}
