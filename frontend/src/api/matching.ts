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

const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0IiwidXNlcm5hbWUiOiJkZW1vIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxODE3NDcyNjA2fQ.J4sb028IFN8h3OBlYq1RatBHZKs0SH6p8eGuKVXKp_c";

export function useMatchExceptions() {
  return useQuery({
    queryKey: ['match-exceptions'],
    queryFn: async () => {
      const response = await apiClient.get<ListMatchExceptionsResponse>('/matching/exceptions', {
        headers: { Authorization: `Bearer ${TOKEN}` }
      });
      return response.data.data;
    },
  });
}

export function useRunMatchingPipeline() {
  return useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/matching/jobs', {}, {
        headers: { Authorization: `Bearer ${TOKEN}` }
      });
      return response.data;
    }
  });
}
