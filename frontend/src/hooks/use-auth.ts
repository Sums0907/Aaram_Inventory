// @ts-nocheck
import { useState, useEffect } from 'react';

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

function buildUserFromPayload(payload: any): AaramUser {
  return {
    user_id: payload.sub || "",
    name: payload.name || payload.username || "",
    permissions: payload.permissions || [],
    applications: payload.applications || [],
    roles: payload.roles || [],
    isAuthenticated: true,
  };
}

function getInitialAuthState(): AaramUser {
  if (typeof window !== 'undefined') {
    // Intercept SSO tokens from URL
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    const urlRefreshToken = params.get('refresh_token');
    if (urlToken) {
      localStorage.setItem('aaram_identity_token', urlToken);
      if (urlRefreshToken) {
        localStorage.setItem('aaram_refresh_token', urlRefreshToken);
      }
      // Clean up the URL to remove the tokens
      const newUrl = window.location.pathname + window.location.hash;
      window.history.replaceState({}, document.title, newUrl);
    }

    const token = localStorage.getItem('aaram_identity_token');
    const refreshToken = localStorage.getItem('aaram_refresh_token');

    if (token) {
      const payload = decodeJWTPayload(token);
      if (payload && payload.exp * 1000 > Date.now()) {
        // Access token is still valid — use it immediately
        return buildUserFromPayload(payload);
      }
      // Access token expired
      localStorage.removeItem('aaram_identity_token');
    }

    // If access token was missing or expired, check if we have a valid refresh token
    if (refreshToken) {
      const refreshPayload = decodeJWTPayload(refreshToken);
      if (refreshPayload && refreshPayload.exp * 1000 > Date.now()) {
        // Refresh token is still valid — return last-known user state if available
        const cachedUser = localStorage.getItem('aaram_cached_user');
        if (cachedUser) {
          try {
            return { ...JSON.parse(cachedUser), isAuthenticated: true };
          } catch (e) { /* fall through */ }
        }
      } else {
        // Refresh token also expired — full logout is legitimate
        localStorage.removeItem('aaram_refresh_token');
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

  useEffect(() => {
    if (user.isAuthenticated) {
      localStorage.setItem('aaram_cached_user', JSON.stringify({
        user_id: user.user_id,
        name: user.name,
        permissions: user.permissions,
        applications: user.applications,
        roles: user.roles,
      }));
    }
  }, [user]);

  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === 'aaram_identity_token' && e.newValue) {
        const payload = decodeJWTPayload(e.newValue);
        if (payload && payload.exp * 1000 > Date.now()) {
          setUser(buildUserFromPayload(payload));
        }
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  return {
    user,
    hasPermission: (permission: string) => user.permissions.includes(permission),
    isAuthenticated: user.isAuthenticated,
    logout: () => {
      localStorage.removeItem('aaram_identity_token');
      localStorage.removeItem('aaram_refresh_token');
      localStorage.removeItem('aaram_cached_user');
      window.location.href = '/';
    }
  };
}
