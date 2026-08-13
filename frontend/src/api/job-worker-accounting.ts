import { apiClient } from './client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_BASE_URL = '/job-worker-accounting';

// --- Types ---

export interface JobWorkRate {
  id: string;
  job_worker_id: string;
  sku_id: string;
  rate: number;
  rate_basis: string;
  effective_from: string; // YYYY-MM-DD
  is_active: boolean;
  notes?: string;
  created_on: string;
}

export interface JobWorkRateCreate {
  job_worker_id: string;
  sku_id: string;
  rate: number;
  rate_basis?: string;
  effective_from: string; // YYYY-MM-DD
  notes?: string;
}

export interface JobWorkExpense {
  id: string;
  reference: string;
  job_worker_id: string;
  finished_product_id: string;
  quantity: number;
  rate: number;
  rate_basis: string;
  amount: number;
  source_receipt_id?: string;
  source_receipt_number?: string;
  expense_date: string;
  status: string;
  notes?: string;
  created_on: string;
}

export interface JobWorkerPayment {
  id: string;
  reference: string;
  job_worker_id: string;
  payment_date: string;
  amount: number;
  payment_account?: string;
  payment_reference?: string;
  notes?: string;
  status: string;
  created_on: string;
}

export interface JobWorkerPaymentCreate {
  job_worker_id: string;
  payment_date: string; // YYYY-MM-DD
  amount: number;
  payment_account?: string;
  payment_reference?: string;
  notes?: string;
}

export interface PayableDashboardWorker {
  job_worker_id: string;
  job_worker_name: string;
  total_expenses: number;
  total_paid: number;
  outstanding: number;
  last_activity_date?: string;
}

export interface PayableDashboardResponse {
  total_job_work_expenses: number;
  total_paid: number;
  total_outstanding: number;
  job_workers_with_outstanding: number;
  job_workers: PayableDashboardWorker[];
}

export interface PayableLedgerEntry {
  id: string;
  date: string; // YYYY-MM-DD
  reference: string;
  particular: string;
  expense: number | null;
  payment: number | null;
  outstanding: number;
}

export interface JobWorkerPayableLedgerResponse {
  job_worker_id: string;
  job_worker_name: string;
  entries: PayableLedgerEntry[];
  total_expenses: number;
  total_paid: number;
  outstanding: number;
}

export interface SuccessResponse<T> {
  data: T;
  message?: string;
}

// --- Hooks ---

// 1. Dashboard
export const useJobWorkerAccountingDashboard = () => {
  return useQuery({
    queryKey: ['job-worker-accounting', 'dashboard'],
    queryFn: async (): Promise<PayableDashboardResponse> => {
      const payload = await apiClient.get<any, SuccessResponse<PayableDashboardResponse>>(`${API_BASE_URL}/dashboard`);
      return payload.data;
    }
  });
};

// 2. Payable Ledger
export const useJobWorkerPayableLedger = (jobWorkerId?: string) => {
  return useQuery({
    queryKey: ['job-worker-accounting', 'ledger', jobWorkerId],
    queryFn: async (): Promise<JobWorkerPayableLedgerResponse> => {
      const payload = await apiClient.get<any, SuccessResponse<JobWorkerPayableLedgerResponse>>(`${API_BASE_URL}/worker/${jobWorkerId}/ledger`);
      return payload.data;
    },
    enabled: !!jobWorkerId,
  });
};

// 3. Rates
export const useJobWorkerRates = () => {
  return useQuery({
    queryKey: ['job-worker-accounting', 'rates'],
    queryFn: async (): Promise<JobWorkRate[]> => {
      const payload = await apiClient.get<any, SuccessResponse<JobWorkRate[]>>(`${API_BASE_URL}/rates`);
      return payload.data;
    }
  });
};

export const useCreateJobWorkRate = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: JobWorkRateCreate) => {
      const payload = await apiClient.post<any, SuccessResponse<JobWorkRate>>(`${API_BASE_URL}/rates`, data);
      return payload;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-worker-accounting', 'rates'] });
    }
  });
};

// 4. Payments
export const useRecordJobWorkerPayment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: JobWorkerPaymentCreate) => {
      const payload = await apiClient.post<any, SuccessResponse<JobWorkerPayment>>(`${API_BASE_URL}/payments`, data);
      return payload;
    },
    onSuccess: (_, variables) => {
      // Invalidate the ledger for this specific worker, and the general dashboard
      queryClient.invalidateQueries({ queryKey: ['job-worker-accounting', 'ledger', variables.job_worker_id] });
      queryClient.invalidateQueries({ queryKey: ['job-worker-accounting', 'dashboard'] });
    }
  });
};

// 5. Expenses
export const useJobWorkerExpenses = (jobWorkerId?: string) => {
  return useQuery({
    queryKey: ['job-worker-accounting', 'expenses', jobWorkerId],
    queryFn: async (): Promise<JobWorkExpense[]> => {
      const response = await axios.get<SuccessResponse<JobWorkExpense[]>>(`${API_BASE_URL}/expenses/worker/${jobWorkerId}`);
      return response.data.data;
    },
    enabled: !!jobWorkerId,
  });
};
