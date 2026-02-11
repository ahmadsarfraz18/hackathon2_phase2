'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/navigation';

// Define User interface
interface User {
  id: string;
  email: string;
  name?: string;
}

// Define AuthContext type
interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuthStatus: () => Promise<boolean>;
  initializeAuth: () => Promise<void>;
}

// Create AuthContext
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Utility function to safely access localStorage
const safeLocalStorage = {
  getItem: (key: string): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(key);
    }
    return null;
  },
  setItem: (key: string, value: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(key, value);
    }
  },
  removeItem: (key: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(key);
    }
  }
};

// API helper to clear any cached headers or interceptors
const clearAxiosHeaders = () => {
  // If using axios, this would clear defaults
  // axios.defaults.headers.common['Authorization'] = undefined;

  // For fetch-based requests, we'll rely on not including the header when token is missing
  // But we can dispatch an event to notify any interceptors
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('auth-token-cleared'));
  }
};

// API helper to set headers
const setAxiosHeaders = (token: string) => {
  // If using axios, this would set the default header
  // axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

  // For fetch-based requests, we'll handle this in our API client
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('auth-token-set', { detail: token }));
  }
};

// Function to verify token and get user data (mock implementation - replace with your actual API call)
const verifyTokenAndGetUser = async (token: string): Promise<User | null> => {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Token is invalid/expired, remove it
        safeLocalStorage.removeItem('auth-token');
        clearAxiosHeaders();
        return null;
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const userData = await response.json();
    return {
      id: userData.id,
      email: userData.email,
      name: `${userData.first_name || ''} ${userData.last_name || ''}`.trim() || userData.email,
    };
  } catch (error) {
    console.error('Error verifying token:', error);
    // Remove token if verification fails
    safeLocalStorage.removeItem('auth-token');
    clearAxiosHeaders();
    return null;
  }
};

// Main AuthProvider component
export const SecureAuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const router = useRouter();

  // Initialize auth status
  const initializeAuth = useCallback(async () => {
    setLoading(true);
    try {
      const token = safeLocalStorage.getItem('auth-token');

      if (token) {
        const userData = await verifyTokenAndGetUser(token);
        if (userData) {
          setUser(userData);
          setAxiosHeaders(token);
        } else {
          // Token was invalid, ensure user is null
          setUser(null);
          safeLocalStorage.removeItem('auth-token');
        }
      } else {
        // No token, ensure user is null
        setUser(null);
      }
    } catch (error) {
      console.error('Error initializing auth:', error);
      setUser(null);
      safeLocalStorage.removeItem('auth-token');
    } finally {
      setLoading(false);
    }
  }, []);

  // Check auth status manually
  const checkAuthStatus = useCallback(async () => {
    try {
      const token = safeLocalStorage.getItem('auth-token');

      if (token) {
        const userData = await verifyTokenAndGetUser(token);
        if (userData) {
          setUser(userData);
          setAxiosHeaders(token);
          return true;
        } else {
          // Token was invalid, ensure user is null
          setUser(null);
          safeLocalStorage.removeItem('auth-token');
          return false;
        }
      } else {
        // No token, ensure user is null
        setUser(null);
        return false;
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      setUser(null);
      safeLocalStorage.removeItem('auth-token');
      return false;
    }
  }, []);

  // Login function
  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      // Clone the response to allow multiple reads
      const clonedResponse = response.clone();

      if (!response.ok) {
        const errorData = await clonedResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      const token = data.access_token;

      // Store the token
      safeLocalStorage.setItem('auth-token', token);

      // Verify the token and get user data
      const userData = await verifyTokenAndGetUser(token);

      if (userData) {
        setUser(userData);
        setAxiosHeaders(token);
      } else {
        throw new Error('Unable to verify user after login');
      }
    } catch (error) {
      console.error('Login error:', error);
      // Ensure state is clean if login fails
      setUser(null);
      safeLocalStorage.removeItem('auth-token');
      clearAxiosHeaders();
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  // Logout function - BULLETPROOF
  const logout = useCallback(async () => {
    setLoading(true);
    try {
      // Call the backend logout endpoint if available
      try {
        const token = safeLocalStorage.getItem('auth-token');
        if (token) {
          await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/auth/logout`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });
        }
      } catch (logoutError) {
        // If backend logout fails, continue with client-side cleanup
        console.error('Backend logout failed:', logoutError);
      }

      // Clear everything - BULLETPROOF CLEANUP
      setUser(null);
      safeLocalStorage.removeItem('auth-token');
      safeLocalStorage.removeItem('refresh-token'); // Remove any refresh tokens
      safeLocalStorage.removeItem('user-data'); // Remove any cached user data
      sessionStorage.clear(); // Clear session storage

      // Clear any cookies related to auth (if any)
      if (typeof document !== 'undefined') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
          const eqPos = cookie.indexOf('=');
          const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
          if (name.toLowerCase().includes('auth') || name.toLowerCase().includes('session') || name.toLowerCase().includes('token')) {
            document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
          }
        }
      }

      // Clear Axios headers
      clearAxiosHeaders();

      // Reset any other auth-related state
      // Force navigation to login
      router.replace('/login');

    } catch (error) {
      console.error('Logout error:', error);
      // Ensure cleanup happens even if there are errors
      setUser(null);
      safeLocalStorage.removeItem('auth-token');
      safeLocalStorage.removeItem('refresh-token');
      safeLocalStorage.removeItem('user-data');
      sessionStorage.clear();
      clearAxiosHeaders();
      router.replace('/login');
    } finally {
      setLoading(false);
    }
  }, [router]);

  // Effect to initialize auth on mount
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // Provide context value
  const value = {
    user,
    loading,
    isAuthenticated: !!user && !loading, // Only authenticated if user exists and not loading
    login,
    logout,
    checkAuthStatus,
    initializeAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within a SecureAuthProvider');
  }
  return context;
};