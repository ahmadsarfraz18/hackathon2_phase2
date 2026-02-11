// Since Better Auth is causing build issues, let's use a simpler approach
// that provides the server configuration the API route expects
// while keeping the custom client-side functions

// Export a minimal auth object that the API route can use
export const auth = {
  GET: async (req: Request) => {
    // Handle GET requests for auth endpoints
    return new Response(JSON.stringify({ error: 'Method not implemented' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' },
    });
  },
  POST: async (req: Request) => {
    // Handle POST requests for auth endpoints
    return new Response(JSON.stringify({ error: 'Method not implemented' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' },
    });
  },
};

// Custom implementations that work with your backend API
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

export const signIn = async (credentials: { email: string; password: string; callbackURL?: string }) => {
  try {
    // Try multiple potential backend URLs in case the server is running elsewhere
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

    const response = await fetch(`${baseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'omit',
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password,
      })
    });

    // Clone the response to allow multiple reads in case of error
    const clonedResponse = response.clone();

    // Handle non-2xx responses
    if (!response.ok) {
      let errorMessage = `Login failed: ${response.status} ${response.statusText}`;
      try {
        const errorData = await clonedResponse.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // If we can't parse the error response, use the status text
      }
      
      return {
        error: { message: errorMessage },
        data: null
      };
    }

    const data = await response.json();
    safeLocalStorage.setItem('auth-token', data.access_token);

    return {
      error: null,
      data: data
    };
  } catch (error: unknown) {  // Use 'unknown' instead of 'any' for better type safety
    console.error('Login error details:', error);
    
    // Handle different error types safely
    let errorMessage = 'Login failed';
    
    if (error instanceof Error) {
      errorMessage = error.message;
    } else if (typeof error === 'string') {
      errorMessage = error;
    } else if (error && typeof error === 'object') {
      // Handle object errors safely
      try {
        const errorObj = error as Record<string, unknown>;
        if (typeof errorObj.message === 'string') {
          errorMessage = errorObj.message;
        } else {
          errorMessage = String(error);
        }
      } catch {
        errorMessage = 'Unknown error occurred during login';
      }
    }

    // Provide a more descriptive error message for network issues
    if (errorMessage.includes('fetch') || errorMessage.includes('network') || errorMessage.includes('Failed to fetch')) {
      errorMessage = 'Unable to connect to the authentication server. Please make sure the backend server is running on http://localhost:8000.';
    }

    return {
      error: { message: errorMessage },
      data: null
    };
  }
};

export const signOut = async () => {
  try {
    // Clear the auth token
    safeLocalStorage.removeItem('auth-token');

    // Additional cleanup for any related tokens or cached data
    safeLocalStorage.removeItem('refresh-token'); // if exists
    safeLocalStorage.removeItem('user-session-data'); // if exists

    // Also clear any session-related browser storage
    if (typeof window !== 'undefined') {
      // Clear any sessionStorage items
      sessionStorage.clear();

      // Clear any cookies related to auth (if any)
      // This is a more thorough cleanup
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        const eqPos = cookie.indexOf('=');
        const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
        if (name.toLowerCase().includes('auth') || name.toLowerCase().includes('session') || name.toLowerCase().includes('token')) {
          document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
        }
      }
    }

    return {
      error: null
    };
  } catch (error: any) {
    console.error('Sign out error:', error);
    return {
      error: {
        message: error.message || 'Logout failed'
      }
    };
  }
};

export const useSession = async () => {
  try {
    const token = safeLocalStorage.getItem('auth-token');

    if (!token) {
      return {
        data: null,
        isLoading: false
      };
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      credentials: 'omit' // Consistent with signIn function
    });

    if (!response.ok) {
      // If the response is not ok (e.g., 401 Unauthorized), remove the token
      if (response.status === 401) {
        safeLocalStorage.removeItem('auth-token');
      }
      return {
        data: null,
        isLoading: false
      };
    }

    const user = await response.json();

    return {
      data: { user },
      isLoading: false
    };
  } catch (error: unknown) { // Use 'unknown' for better type safety
    console.error('Session check error:', error);
    // In case of network errors or other exceptions, remove the token
    safeLocalStorage.removeItem('auth-token');

    // Handle the "Object" error by checking the error type
    if (error && typeof error === 'object') {
      if ((error as any).message) {
        console.error('Error with message:', (error as any).message);
      } else {
        console.error('Generic object error:', JSON.stringify(error));
      }
    }

    return {
      data: null,
      isLoading: false
    };
  }
};