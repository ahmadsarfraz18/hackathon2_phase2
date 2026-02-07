'use client';

import { useState, useEffect, createContext, useContext, ReactNode, useCallback } from 'react';
import { signIn, signOut, useSession as getSession } from '../auth';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  name?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuthStatus: () => Promise<void>;
  initializeAuth: () => Promise<void>;
}

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

// Function to verify token and get user data
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
    return null;
  }
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
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
      console.error('Error checking auth status:', error);
      setUser(null);
      safeLocalStorage.removeItem('auth-token');
    }
  }, []);

  // Login function
  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      const result = await signIn({ email, password });

      if (result.error) {
        throw new Error(result.error.message || 'Login failed');
      }

      // Verify the token and get user data
      const token = safeLocalStorage.getItem('auth-token');
      if (token) {
        const userData = await verifyTokenAndGetUser(token);
        if (userData) {
          setUser(userData);
        } else {
          throw new Error('Unable to verify user after login');
        }
      } else {
        throw new Error('No token found after login');
      }
    } catch (error) {
      console.error('Login error:', error);
      // Ensure state is clean if login fails
      setUser(null);
      safeLocalStorage.removeItem('auth-token');
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

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};