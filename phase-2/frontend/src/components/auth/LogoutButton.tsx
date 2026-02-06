'use client';

import React from 'react';
import { useAuth } from '../../hooks/useAuth';

interface LogoutButtonProps {
  className?: string;
  onLogout?: () => void;
}

export const LogoutButton: React.FC<LogoutButtonProps> = ({
  className = "inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500",
  onLogout
}) => {
  const { logout, loading } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      if (onLogout) {
        onLogout();
      }
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <button
      onClick={handleLogout}
      disabled={loading}
      className={`${className} ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      {loading ? 'Logging out...' : 'Logout'}
    </button>
  );
};