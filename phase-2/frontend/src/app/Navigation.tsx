'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '../hooks/useAuth';

export default function Navigation() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, logout, loading } = useAuth();

  return (
    <>
      {/* Desktop Navigation - Conditional based on auth status */}
      {user ? (
        <div className="hidden md:flex items-center space-x-2">
          <Link
            href="/dashboard"
            className="px-4 py-2 text-sm font-medium text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-200 ease-in-out"
          >
            Dashboard
          </Link>
          <button
            onClick={() => logout()}
            className="px-4 py-2 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-all duration-200 ease-in-out"
          >
            Logout
          </button>
        </div>
      ) : (
        <nav className="hidden md:flex items-center space-x-1">
          <a
            href="/"
            className="px-4 py-2 text-sm font-medium text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-200 ease-in-out"
          >
            Home
          </a>
          <a
            href="/login"
            className="px-4 py-2 text-sm font-medium text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-all duration-200 ease-in-out"
          >
            Login
          </a>
          <a
            href="/signup"
            className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 rounded-lg transition-all duration-200 ease-in-out shadow-sm hover:shadow-md"
          >
            Sign Up
          </a>
        </nav>
      )}

      {/* Mobile menu button */}
      <div className="md:hidden flex items-center">
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

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden py-4 border-t border-slate-700/50">
          <nav className="flex flex-col space-y-1">
            <Link
              href="/"
              className="px-4 py-3 text-base font-medium text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-colors duration-200"
              onClick={() => setMobileMenuOpen(false)}
            >
              Home
            </Link>

            {user ? (
              <>
                <Link
                  href="/dashboard"
                  className="px-4 py-3 text-base font-medium text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-colors duration-200"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
                <button
                  onClick={() => {
                    logout();
                    setMobileMenuOpen(false);
                  }}
                  className="w-full text-left px-4 py-3 text-base font-medium text-red-400 hover:text-red-300 hover:bg-red-900/30 rounded-lg transition-colors duration-200"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="px-4 py-3 text-base font-medium text-slate-200 hover:text-white hover:bg-slate-800/50 rounded-lg transition-colors duration-200"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Login
                </Link>
                <Link
                  href="/signup"
                  className="px-4 py-3 text-base font-medium text-white bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 rounded-lg transition-colors duration-200 shadow-sm"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Sign Up
                </Link>
              </>
            )}
          </nav>
        </div>
      )}
    </>
  );
}