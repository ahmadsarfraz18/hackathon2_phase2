'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../hooks/useAuth';

interface RequireAuthProps {
  children: React.ReactNode;
}

export default function RequireAuth({ children }: RequireAuthProps) {
  const { user, loading, error } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        // Redirect to login if not authenticated
        router.push('/login');
      }
    }
  }, [user, loading, router]);

  // Show loading while checking authentication state
  if (loading) {
    return (
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

  // If user is authenticated, render children
  if (user) {
    return <>{children}</>;
  }

  // If we reach here, the user is not authenticated and has been redirected
  return null;
}