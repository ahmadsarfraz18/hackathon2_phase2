'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export default function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const { user, loading, isMounted } = useAuth();
  const router = useRouter();
  const [hasCheckedAuth, setHasCheckedAuth] = useState(false);

  useEffect(() => {
    if (isMounted) {
      if (!loading) {
        if (!user) {
          // Redirect to login if user is not authenticated
          router.push('/login');
        } else {
          setHasCheckedAuth(true);
        }
      }
    }
  }, [user, loading, isMounted, router]);

  // Show loading state while checking authentication
  if (loading || !isMounted || !hasCheckedAuth) {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-indigo-50 to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="relative inline-block">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600 mx-auto"></div>
            <div className="absolute inset-0 animate-ping rounded-full h-12 w-12 border border-indigo-200"></div>
          </div>
          <p className="mt-4 text-lg text-gray-600 animate-fade-in">Checking authentication status...</p>
        </div>
      </div>
    );
  }

  // Render children only if user is authenticated
  return <>{children}</>;
}