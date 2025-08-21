'use client';

import { ReactNode } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Loading } from '@/components/ui/loading';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Shield, AlertTriangle } from 'lucide-react';

interface RoleGuardProps {
  children: ReactNode;
  allowedRoles?: string[];
  requiredPermissions?: string[];
  fallback?: ReactNode;
  redirectTo?: string;
}

export default function RoleGuard({ 
  children, 
  allowedRoles = [], 
  requiredPermissions = [], 
  fallback,
  redirectTo = '/login'
}: RoleGuardProps) {
  const { user, isAuthenticated, hasPermission, hasRole, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push(redirectTo);
    }
  }, [loading, isAuthenticated, router, redirectTo]);

  // Show loading while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <Loading size="lg" text="Checking permissions..." />
      </div>
    );
  }

  // If not authenticated, show loading (will redirect)
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <Loading size="lg" text="Redirecting to login..." />
      </div>
    );
  }

  // Check role permissions
  const hasRequiredRole = allowedRoles.length === 0 || allowedRoles.some(role => hasRole(role));
  
  // Check specific permissions
  const hasRequiredPermissions = requiredPermissions.length === 0 || 
    requiredPermissions.every(permission => hasPermission(permission));

  // If user doesn't have required role or permissions
  if (!hasRequiredRole || !hasRequiredPermissions) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md shadow-xl border-0">
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <CardTitle className="text-xl font-bold text-slate-900">Access Denied</CardTitle>
            <CardDescription className="text-slate-600">
              You don't have permission to access this page
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <div className="space-y-4">
              <div className="text-sm text-slate-500">
                <p>Current role: <span className="font-medium">{user?.role}</span></p>
                {allowedRoles.length > 0 && (
                  <p>Required roles: <span className="font-medium">{allowedRoles.join(', ')}</span></p>
                )}
                {requiredPermissions.length > 0 && (
                  <p>Required permissions: <span className="font-medium">{requiredPermissions.join(', ')}</span></p>
                )}
              </div>
              <button
                onClick={() => router.push('/dashboard')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Go to Dashboard
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // User has required permissions, render children
  return <>{children}</>;
}

// Convenience components for specific roles
export function AdminGuard({ children, fallback }: { children: ReactNode; fallback?: ReactNode }) {
  return (
    <RoleGuard allowedRoles={['admin']} fallback={fallback}>
      {children}
    </RoleGuard>
  );
}

export function DeveloperGuard({ children, fallback }: { children: ReactNode; fallback?: ReactNode }) {
  return (
    <RoleGuard allowedRoles={['admin', 'developer']} fallback={fallback}>
      {children}
    </RoleGuard>
  );
}

export function InvestorGuard({ children, fallback }: { children: ReactNode; fallback?: ReactNode }) {
  return (
    <RoleGuard allowedRoles={['admin', 'investor']} fallback={fallback}>
      {children}
    </RoleGuard>
  );
}

export function ConsultantGuard({ children, fallback }: { children: ReactNode; fallback?: ReactNode }) {
  return (
    <RoleGuard allowedRoles={['admin', 'consultant']} fallback={fallback}>
      {children}
    </RoleGuard>
  );
} 