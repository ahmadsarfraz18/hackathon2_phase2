'use client';

import { useState, useEffect, createContext, useContext, ReactNode, useCallback } from 'react';
import { signIn as authSignIn, signOut as authSignOut, useSession as getSession } from '../auth';

interface User {
  id: string;
  email: string;
  name?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  isInitialized: boolean; // Changed from isMounted to isInitialized for clarity
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  signup: (email: string, password: string, firstName: string, lastName: string) => Promise<void>;
  clearError: () => void;
  refreshSession: () => Promise<void>;
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

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Memoized function to check session
  const checkSession = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Use the updated auth function to get session
      const sessionResult = await getSession();

      if (sessionResult.data?.user) {
        const userData = sessionResult.data.user;
        const userObject: User = {
          id: userData.id,
          email: userData.email,
          name: `${userData.first_name || ''} ${userData.last_name || ''}`.trim() || userData.email,
        };

        setUser(userObject);
      } else {
        // If no user in session, explicitly set user to null
        setUser(null);
      }
    } catch (err) {
      console.error('Error checking session:', err);
      // If there's an error, clear the token
      safeLocalStorage.removeItem('auth-token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Only run on client side after mounting
    if (typeof window !== 'undefined') {
      // Initialize auth state
      checkSession().finally(() => {
        setIsInitialized(true);
      });
    } else {
      // On server or before mounting, ensure loading state
      setLoading(true);
    }
  }, [checkSession]);

  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);

    try {
      // Use the updated signIn function
      const result = await authSignIn({ email, password });

      if (result.error) {
        throw new Error(result.error.message || 'Login failed');
      }

      // After successful login, we should have a token stored
      // Now fetch the user session to populate the user state
      const sessionResult = await getSession();

      if (sessionResult.data?.user) {
        const userData = sessionResult.data.user;
        const userObject: User = {
          id: userData.id,
          email: userData.email,
          name: `${userData.first_name || ''} ${userData.last_name || ''}`.trim() || userData.email,
        };

        setUser(userObject);
      } else {
        // If session retrieval failed after login, clear the token
        safeLocalStorage.removeItem('auth-token');
        throw new Error('Login succeeded but unable to retrieve user session');
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
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      // Use the updated signOut function
      await authSignOut();
      // Explicitly clear user state
      setUser(null);
      // Clear any potential cached tokens
      safeLocalStorage.removeItem('auth-token');
    } catch (err) {
      console.error('Logout error:', err);
      setError('Failed to logout');
    } finally {
      setLoading(false);
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

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
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
      throw new Error(errorMessage); // Re-throw with the same message for the calling function
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => {
    setError(null);
  };

  const refreshSession = async () => {
    await checkSession();
  };

  const value = {
    user,
    loading,
    error,
    isInitialized,
    isAuthenticated: !!user && isInitialized, // True only if user exists and auth is initialized
    login,
    logout,
    signup,
    clearError,
    refreshSession,
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