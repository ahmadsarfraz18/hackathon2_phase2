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
  error: string | null;
  isInitialized: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  safeLogout: () => Promise<void>;
  signup: (email: string, password: string, firstName: string, lastName: string) => Promise<void>;
  clearError: () => void;
  refreshSession: () => Promise<void>;
  forceClearAuth: () => void;
  initializeAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

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

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true); // Always start as loading initially
  const [error, setError] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);
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
    } catch (err) {
      console.error('Error initializing auth:', err);
      setUser(null);
      safeLocalStorage.removeItem('auth-token');
    } finally {
      setLoading(false);
      setIsInitialized(true);
    }
  }, []);

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);

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
    } catch (err: any) {
      // Handle the "Object" error issue by providing better error handling
      let errorMessage = 'Login failed';
      if (err && typeof err === 'object' && err.message) {
        errorMessage = err.message;
      } else if (err && typeof err === 'string') {
        errorMessage = err;
      } else if (err && typeof err === 'object') {
        // Handle generic object errors
        try {
          errorMessage = JSON.stringify(err);
        } catch (stringifyErr) {
          errorMessage = 'Unknown error occurred during login';
        }
      }

      setError(errorMessage);
      // Clear any potentially invalid token
      safeLocalStorage.removeItem('auth-token');
      // Ensure we're throwing an Error instance, not a raw object
      if (err instanceof Error) {
        throw err;
      } else {
        throw new Error(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  // BULLETPROOF logout function
  const logout = async () => {
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
      setError(null);
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

    } catch (err) {
      console.error('Logout error:', err);
      // Ensure cleanup happens even if there are errors
      setUser(null);
      setError(null);
      safeLocalStorage.removeItem('auth-token');
      safeLocalStorage.removeItem('refresh-token');
      safeLocalStorage.removeItem('user-data');
      sessionStorage.clear();
      router.replace('/login');
    } finally {
      setLoading(false);
    }
  };

  // Safe logout function that handles errors gracefully to prevent promise rejections
  const safeLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Safe logout error:', error);
      // Logout function already handles all cleanup, so we don't need additional handling here
    }
  };

  const signup = async (email: string, password: string, firstName: string, lastName: string) => {
    setLoading(true);
    setError(null);

    try {
      // For signup, we need to call the API directly since Better Auth doesn't handle this
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          first_name: firstName,
          last_name: lastName
        }),
      });

      // Clone the response to allow multiple reads
      const clonedResponse = response.clone();

      if (!response.ok) {
        const errorData = await clonedResponse.json().catch(() => ({}));
        const errorMessage = errorData.detail || errorData.message || 'Signup failed';
        throw new Error(errorMessage);
      }

      const userData = await response.json();

      // After successful signup, we should log the user in
      // Call login to complete the session setup
      await login(email, password);

      console.log('Signup successful');
    } catch (err: any) {
      // Log the exact error message for debugging
      console.error('Detailed signup error:', err);
      const errorMessage = err.message || 'Signup failed';
      setError(errorMessage);
      // Clear any potential partial state
      safeLocalStorage.removeItem('auth-token');
      setUser(null);
      // Ensure we're throwing an Error instance, not a raw object
      throw new Error(errorMessage); // Re-throw with the same message for the calling function
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => {
    setError(null);
  };

  const refreshSession = async () => {
    try {
      setLoading(true);
      const token = safeLocalStorage.getItem('auth-token');

      if (token) {
        const userData = await verifyTokenAndGetUser(token);
        if (userData) {
          setUser(userData);
        } else {
          setUser(null);
        }
      } else {
        setUser(null);
      }
    } catch (err) {
      console.error('Error refreshing session:', err);
      safeLocalStorage.removeItem('auth-token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  // Method to force clear all auth state completely
  const forceClearAuth = () => {
    setUser(null);
    setError(null);
    setLoading(false);
    setIsInitialized(false);
    safeLocalStorage.removeItem('auth-token');
    safeLocalStorage.removeItem('refresh-token');
    safeLocalStorage.removeItem('user-data');
    // Clear any other auth-related storage
    sessionStorage.clear();
  };

  const value = {
    user,
    loading,
    error,
    isInitialized,
    isAuthenticated: !!user && isInitialized && !loading, // True only if user exists, auth is initialized, and not loading
    login,
    logout,
    safeLogout,
    signup,
    clearError,
    refreshSession,
    forceClearAuth,
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