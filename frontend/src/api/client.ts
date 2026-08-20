// @ts-nocheck
import axios from 'axios';
import { toast } from '@/hooks/use-toast';

// Add type declaration for window.AARAM_CONFIG
declare global {
  interface Window {
    AARAM_CONFIG?: {
      API_URL?: string;
    };
  }
}

const API_BASE_URL =
  window.AARAM_CONFIG?.API_URL || "http://localhost:8100/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('aaram_identity_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response.data, 
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and reload to force AaramIdentity redirect via useAuth
      localStorage.removeItem('aaram_identity_token');
      window.location.href = '/';
      return Promise.reject(error);
    }
    
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
