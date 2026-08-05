import axios from 'axios';

export const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// We can add interceptors here later if we need to handle auth tokens or global error logging
import { toast } from '@/hooks/use-toast';

apiClient.interceptors.response.use(
  (response) => response.data, 
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Extract error message safely
    let errorMessage = "An unexpected error occurred.";
    if (error.response?.data?.message) {
      errorMessage = error.response.data.message;
    } else if (error.response?.data?.detail) {
      // FastAPI default validation error format
      if (Array.isArray(error.response.data.detail)) {
        errorMessage = error.response.data.detail[0]?.msg || "Validation Error";
      } else {
        errorMessage = error.response.data.detail;
      }
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    toast({
      variant: "destructive",
      title: "Network Error",
      description: errorMessage,
    });
    
    return Promise.reject(error);
  }
);
