// @ts-nocheck
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/hooks/use-auth';

export function ProtectedRoute() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    // In a real AaramIdentity setup, we redirect the user to the Identity provider
    const identityUrl = window.AARAM_CONFIG?.IDENTITY_URL || "http://localhost:9001";
    window.location.href = `${identityUrl}/login?redirect=${encodeURIComponent(window.location.href)}`;
    return null;
  }

  return <Outlet />;
}
