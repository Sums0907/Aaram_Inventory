import { useQuery } from '@tanstack/react-query';
import { apiClient } from './client';

export interface JournalLine {
  ledger_name: string;
  debit: number;
  credit: number;
}

export interface JournalEntryResponse {
  id: string;
  entry_date: string | null;
  reference_type: string;
  reference_id: string;
  narration: string;
  lines: JournalLine[];
}

interface ListJournalsResponse {
  success: boolean;
  data: JournalEntryResponse[];
}

const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0IiwidXNlcm5hbWUiOiJkZW1vIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxODE3NDcyNjA2fQ.J4sb028IFN8h3OBlYq1RatBHZKs0SH6p8eGuKVXKp_c";

export function useJournals() {
  return useQuery({
    queryKey: ['journals'],
    queryFn: async () => {
      const response = await apiClient.get<ListJournalsResponse>('/accounting/journals', {
        headers: { Authorization: `Bearer ${TOKEN}` }
      });
      return response.data.data;
    },
  });
}
