import axios from 'axios';
import { toast } from '@/hooks/use-toast';

const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MDJlYWMxMS0yMWUyLTRkNTMtYTllOS0yYmEyMWJjMDRiOWEiLCJ1c2VybmFtZSI6ImRlbW8iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE4MTc0NzI2MDZ9._cuQTw-7zam00atnpTsxsklre2ZsOFVKPkbvChQpSMM";

// Add type declaration for window.AARAM_CONFIG
declare global {
  interface Window {
    AARAM_CONFIG?: {
      API_URL?: string;
    };
  }
}

const API_BASE_URL =
  window.AARAM_CONFIG?.API_URL || "http://127.0.0.1:8100/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${TOKEN}`,
  },
});

// We can add interceptors here later if we need to handle auth tokens or global error logging

apiClient.interceptors.response.use(
  (response) => response.data, 
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Extract error message safely
    let errorMessage = "An unexpected error occurred.";
    if (error.response?.data?.error?.message) {
      errorMessage = error.response.data.error.message;
    } else if (error.response?.data?.message) {
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
