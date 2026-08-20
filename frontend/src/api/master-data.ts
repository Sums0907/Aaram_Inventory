// @ts-nocheck
import { apiClient } from './client';

export interface ImportRowResult {
  row_index: number;
  action: 'CREATED' | 'UPDATED' | 'IGNORED' | 'FAILED' | 'AMBIGUOUS';
  entity_id: string | null;
  identifier: string | null;
  errors: string[];
}

export interface ImportResult {
  batch_id: string;
  entity_type: string;
  total_records: number;
  created_count: number;
  updated_count: number;
  ignored_count: number;
  failed_count: number;
  ambiguous_count: number;
  row_results: ImportRowResult[];
  global_errors: string[];
}

export interface ImportAuditLog {
  id: string;
  batch_id: string;
  filename: string;
  entity_type: string;
  environment: string;
  executed_by_user_id: string | null;
  status: string;
  rollback_status: string;
  records_processed: number;
  success_count: number;
  failure_count: number;
  start_time: string;
  end_time: string;
}

export const masterDataApi = {
  import: async (file: File, domain: string, isDryRun: boolean): Promise<ImportResult> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('domain', domain);
    formData.append('is_dry_run', String(isDryRun));

    return apiClient.post('/master-data/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  export: async (domain: string): Promise<Blob> => {
    // Return Blob directly since the API returns a file download
    // Ensure axios receives it as a blob
    return apiClient.get('/master-data/export', {
      params: { domain },
      responseType: 'blob',
    });
  },

  getActivityHistory: async (params?: {
    domain?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<ImportAuditLog[]> => {
    return apiClient.get('/master-data/activity-history', { params });
  },
};
