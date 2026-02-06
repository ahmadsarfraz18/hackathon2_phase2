/**
 * Error handling utilities for API responses
 */

export interface ApiError {
  message: string;
  status: number;
  detail?: string;
}

// Handle API errors, especially authentication/authorization errors
export const handleApiError = (error: any): ApiError => {
  if (error.status) {
    // This is likely an HTTP error from our API
    const status = error.status;

    switch (status) {
      case 401:
        return {
          message: "Unauthorized: Please log in again",
          status: 401,
          detail: error.detail || "Authentication required"
        };
      case 403:
        return {
          message: "Forbidden: You don't have permission to access this resource",
          status: 403,
          detail: error.detail || "Access denied"
        };
      case 404:
        return {
          message: "Resource not found",
          status: 404,
          detail: error.detail || "The requested resource was not found"
        };
      case 422:
        return {
          message: "Validation error",
          status: 422,
          detail: error.detail || "The request contains invalid data"
        };
      case 500:
        return {
          message: "Internal server error",
          status: 500,
          detail: error.detail || "An unexpected error occurred"
        };
      default:
        return {
          message: `HTTP Error: ${status}`,
          status: status,
          detail: error.detail || "An error occurred with the request"
        };
    }
  } else if (error.message) {
    // This is likely a network or other error
    return {
      message: "Network error or other issue",
      status: 0,
      detail: error.message
    };
  } else {
    // Unknown error
    return {
      message: "An unknown error occurred",
      status: 0,
      detail: "Something went wrong"
    };
  }
};

// Check if an error is an authentication error (401)
export const isAuthError = (error: ApiError): boolean => {
  return error.status === 401;
};

// Check if an error is an authorization error (403)
export const isAuthzError = (error: ApiError): boolean => {
  return error.status === 403;
};

// Check if an error is a network error
export const isNetworkError = (error: ApiError): boolean => {
  return error.status === 0;
};

// Function to redirect to login on auth errors
export const handleAuthError = (error: ApiError, router?: any) => {
  if (isAuthError(error)) {
    // Clear any stored tokens
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }

    // Redirect to login page if router is provided
    if (router && typeof router.push === 'function') {
      router.push('/login');
    } else if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }
};

// Function to handle authorization errors
export const handleAuthzError = (error: ApiError) => {
  if (isAuthzError(error)) {
    console.error('Authorization error:', error.detail);
    // In a real app, you might want to show a specific message to the user
    // or redirect to an error page
  }
};