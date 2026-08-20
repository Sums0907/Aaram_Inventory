import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from './client';

export interface MatchExceptionResponse {
  id: string;
  exception_type: string;
  source_type: string;
  source_id: string;
  status: string;
  description: string;
  severity: string;
  resolved_at: string | null;
  created_at: string;
}

interface ListMatchExceptionsResponse {
  success: boolean;
  data: MatchExceptionResponse[];
}

export function useMatchExceptions() {
  return useQuery({
    queryKey: ['match-exceptions'],
    queryFn: async () => {
      const response = await apiClient.get<ListMatchExceptionsResponse>('/matching/exceptions');
      return response.data.data;
    },
  });
}

export function useRunMatchingPipeline() {
  return useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/matching/jobs', {});
      return response.data;
    }
  });
}
