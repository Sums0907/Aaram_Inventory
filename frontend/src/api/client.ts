// @ts-nocheck
import axios from 'axios';
import { toast } from '@/hooks/use-toast';

// Add type declaration for window.AARAM_CONFIG
declare global {
  interface Window {
    AARAM_CONFIG?: {
      API_URL?: string;
      IDENTITY_URL?: string;
      IDENTITY_API_URL?: string;
    };
  }
}

const API_BASE_URL =
  window.AARAM_CONFIG?.API_URL || "http://localhost:8100/api/v1";

// BUG FIX #2: Use IDENTITY_API_URL (backend) for refresh calls, not IDENTITY_URL (frontend UI).
// On localhost, IDENTITY_API_URL = http://127.0.0.1:9000
// On production, IDENTITY_API_URL = https://api.identity.aarambooks.cloud
function getIdentityApiUrl(): string {
  return (
    window.AARAM_CONFIG?.IDENTITY_API_URL ||
    window.AARAM_CONFIG?.IDENTITY_URL ||
    "http://127.0.0.1:9000"
  ).replace(/\/$/, "");
}

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

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function subscribeTokenRefresh(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}

function onRefreshed(token: string) {
  refreshSubscribers.forEach(cb => cb(token));
  refreshSubscribers = [];
}

apiClient.interceptors.response.use(
  (response) => response.data, 
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('aaram_refresh_token');

      if (!refreshToken) {
        localStorage.removeItem('aaram_identity_token');
        localStorage.removeItem('aaram_refresh_token');
        localStorage.removeItem('aaram_cached_user');
        window.location.href = '/';
        return Promise.reject(error);
      }

      if (!isRefreshing) {
        isRefreshing = true;

        try {
          const currentRefresh = localStorage.getItem('aaram_refresh_token');
          if (currentRefresh && currentRefresh !== refreshToken) {
            // Another tab already refreshed
            const newAccess = localStorage.getItem('aaram_identity_token');
            isRefreshing = false;
            onRefreshed(newAccess);
            originalRequest.headers.Authorization = `Bearer ${newAccess}`;
            return axios(originalRequest);
          }

          const refreshUrl = `${getIdentityApiUrl()}/auth/refresh`;
          const refreshRes = await axios.post(refreshUrl, {
            refresh_token: refreshToken,
            platform: 'AARAM_INVENTORY_WEB'
          });

          const data = refreshRes.data?.data || refreshRes.data;
          
          if (data.access_token) {
            localStorage.setItem('aaram_identity_token', data.access_token);
            localStorage.setItem('aaram_refresh_token', data.refresh_token);
            
            isRefreshing = false;
            onRefreshed(data.access_token);
          } else {
            throw new Error("No tokens in response");
          }
        } catch (refreshError) {
          isRefreshing = false;
          const status = refreshError.response?.status;
          if (status === 401 || status === 403 || refreshError.message === "No tokens in response") {
            localStorage.removeItem('aaram_identity_token');
            localStorage.removeItem('aaram_refresh_token');
            localStorage.removeItem('aaram_cached_user');
            window.location.href = '/';
          }
          return Promise.reject(refreshError);
        }
      }

      return new Promise((resolve) => {
        subscribeTokenRefresh((newToken) => {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          resolve(axios(originalRequest));
        });
      });
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
