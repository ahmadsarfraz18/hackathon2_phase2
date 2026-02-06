/**
 * Authentication utilities for handling NextAuth in the frontend
 */

// Import NextAuth functions
import { getCsrfToken, getSession, signIn, signOut } from 'next-auth/react';

// Store NextAuth session data in localStorage (if needed for specific use cases)
export const storeSession = (session: any): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('nextauth.session', JSON.stringify(session));
  }
};

// Retrieve NextAuth session from localStorage
export const getSessionFromStorage = (): any => {
  if (typeof window !== 'undefined') {
    const sessionStr = localStorage.getItem('nextauth.session');
    return sessionStr ? JSON.parse(sessionStr) : null;
  }
  return null;
};

// Remove NextAuth session from localStorage
export const removeSession = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('nextauth.session');
  }
};

// Check if user is authenticated using NextAuth
export const isAuthenticated = async (): Promise<boolean> => {
  try {
    const session = await getSession();
    return !!session?.user;
  } catch (error) {
    console.error('Error checking authentication status:', error);
    return false;
  }
};

// Get user information from NextAuth session
export const getUser = async (): Promise<any> => {
  try {
    const session = await getSession();
    return session?.user || null;
  } catch (error) {
    console.error('Error getting user session:', error);
    return null;
  }
};

// Get CSRF token for security
export const getCSRFToken = async (): Promise<string | null> => {
  try {
    return await getCsrfToken();
  } catch (error) {
    console.error('Error getting CSRF token:', error);
    return null;
  }
};

// Sign in helper function
export const loginUser = async (email: string, password: string): Promise<any> => {
  try {
    const result = await signIn('credentials', {
      email,
      password,
      redirect: false,
    });
    return result;
  } catch (error) {
    console.error('Error during login:', error);
    throw error;
  }
};

// Sign out helper function
export const logoutUser = async (): Promise<void> => {
  try {
    await signOut({ redirect: false });
    removeSession(); // Clean up local storage
  } catch (error) {
    console.error('Error during logout:', error);
    throw error;
  }
};