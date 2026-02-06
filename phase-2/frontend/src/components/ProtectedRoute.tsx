import React, { ReactNode } from 'react';
import { useAuth } from '../hooks/useAuth'; // Adjust import path as needed
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
  fallback?: ReactNode; // Optional fallback while checking auth status
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  fallback = (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-indigo-50 to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="text-center">
        <div className="relative inline-block">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600 mx-auto"></div>
          <div className="absolute inset-0 animate-ping rounded-full h-12 w-12 border border-indigo-200"></div>
        </div>
        <p className="mt-4 text-lg text-gray-600 animate-fade-in">Verifying authentication...</p>
      </div>
    </div>
  )
}) => {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If user is not authenticated and auth is initialized, redirect to login
    if (!loading && !isAuthenticated) {
      router.replace('/login');
    }
  }, [isAuthenticated, loading, router]);

  // Show loading state while checking auth status
  if (loading) {
    return fallback;
  }

  // If authenticated, show the protected content
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // If not authenticated and not loading, return fallback
  // The useEffect will handle redirect, but we return fallback in case of timing
  return fallback;
};

export default ProtectedRoute;