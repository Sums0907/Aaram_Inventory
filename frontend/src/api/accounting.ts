// @ts-nocheck
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

export function useJournals() {
  return useQuery({
    queryKey: ['journals'],
    queryFn: async () => {
      const response = await apiClient.get<ListJournalsResponse>('/accounting/journals');
      return response.data.data;
    },
  });
}
