'use client';

import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { LogoutButton } from '../../components/auth/LogoutButton';

interface ResponsiveHeaderProps {
  title?: string;
}

export const ResponsiveHeader: React.FC<ResponsiveHeaderProps> = ({ title = 'Todo Dashboard' }) => {
  const { user } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="bg-slate-900/80 backdrop-blur-md shadow-sm border-b border-slate-700/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center">
            <h1 className="text-xl font-semibold text-white">{title}</h1>
          </div>

          {/* Desktop menu */}
          <div className="hidden md:flex items-center space-x-4">
            {user && (
              <span className="text-slate-200 hidden sm:block">
                Hello, {user.name || user.email.split('@')[0]}
              </span>
            )}
            {user && <LogoutButton />}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            {user && (
              <span className="text-slate-200 mr-3 text-sm">
                {user.name || user.email.split('@')[0]}
              </span>
            )}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-slate-200 hover:text-white hover:bg-slate-800/50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
            >
              <span className="sr-only">Open main menu</span>
              {/* Hamburger icon */}
              <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-2 border-t border-slate-700/50">
            <div className="flex flex-col space-y-2 pt-2 pb-3">
              {user && (
                <div className="px-4">
                  <LogoutButton className="w-full justify-center px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700" />
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};