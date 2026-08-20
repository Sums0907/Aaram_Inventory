// @ts-nocheck
import { useState, useEffect } from 'react';

// AaramIdentity Authentication Adapter
// This acts purely as a UX interface. Backend is the source of truth for all security.
export interface AaramUser {
  user_id: string;
  name: string;
  permissions: string[];
  applications: string[];
  roles: string[];
  isAuthenticated: boolean;
}

function decodeJWTPayload(token: string) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

function getInitialAuthState(): AaramUser {
  if (typeof window !== 'undefined') {
    // Intercept SSO token from URL
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    if (urlToken) {
      localStorage.setItem('aaram_identity_token', urlToken);
      // Clean up the URL to remove the token
      const newUrl = window.location.pathname + window.location.hash;
      window.history.replaceState({}, document.title, newUrl);
    }

    const token = localStorage.getItem('aaram_identity_token');
    if (token) {
      const payload = decodeJWTPayload(token);
      if (payload && payload.exp * 1000 > Date.now()) {
        return {
          user_id: payload.sub || "",
          name: payload.name || payload.username || "",
          permissions: payload.permissions || [],
          applications: payload.applications || [],
          roles: payload.roles || [],
          isAuthenticated: true,
        };
      } else {
        localStorage.removeItem('aaram_identity_token');
      }
    }
  }
  
  return {
    user_id: "",
    name: "",
    permissions: [],
    applications: [],
    roles: [],
    isAuthenticated: false,
  };
}

export function useAuth() {
  const [user, setUser] = useState<AaramUser>(getInitialAuthState);

  return {
    user,
    hasPermission: (permission: string) => user.permissions.includes(permission),
    isAuthenticated: user.isAuthenticated,
    logout: () => {
      localStorage.removeItem('aaram_identity_token');
      window.location.href = '/';
    }
  };
}
