// Base API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Ensure trailing slash is not duplicated
const normalizeUrl = (url: string): string => {
  return url.replace(/\/$/, '');
};

// Create a base API client with common configuration
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Common headers for all requests
  private async getHeaders(): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    // Since Better Auth session might not be working with our custom backend,
    // we'll check if there's a token stored elsewhere (e.g., localStorage)
    // For now, we'll assume the token is stored in localStorage after login
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth-token');
      // Only add Authorization header if token exists
      if (token && token.trim() !== '') {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  // Generic GET request
  async get<T>(endpoint: string): Promise<T> {
    try {
      const headers = await this.getHeaders();

      // Ensure we have an authentication token before making the request (for protected endpoints)
      // Don't require token for auth/me endpoint as it's used to check if user is logged in
      if (!headers['Authorization'] && (endpoint.includes('/tasks') && !endpoint.includes('/auth/me'))) {
        throw new Error('No authentication token available');
      }

      const response = await fetch(`${normalizeUrl(this.baseUrl)}${endpoint}`, {
        method: 'GET',
        headers,
        credentials: 'omit', // Changed to 'omit' since we're using JWT tokens stored in localStorage
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      // Don't log 401 errors for /auth/me endpoint as they are expected during auth checks
      if (!(endpoint === '/auth/me' && error instanceof Error && error.message.includes('Unauthorized'))) {
        console.error(`API GET error for ${endpoint}:`, error);
      }

      // Check if it's a network error (TypeError with specific messages)
      if (error instanceof TypeError) {
        if (error.message.includes('fetch') || error.message.includes('network') || error.message.includes('Failed to fetch')) {
          throw new Error('Network error: Unable to connect to server. Please check your connection and ensure the server is running.');
        }
      }

      // Re-throw the original error if it's not a network error
      if (error instanceof Error) {
        throw error;
      }

      throw new Error(`Failed to fetch data: ${error instanceof Error ? error.message : 'Network error'}`);
    }
  }

  // Generic POST request
  async post<T>(endpoint: string, data?: any): Promise<T> {
    try {
      const headers = await this.getHeaders();

      // Ensure we have an authentication token before making the request (for protected endpoints)
      if (!headers['Authorization'] && (endpoint.includes('/tasks') || (endpoint.includes('/auth/') && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/signup') && !endpoint.includes('/auth/me')))) {
        throw new Error('No authentication token available');
      }

      const response = await fetch(`${normalizeUrl(this.baseUrl)}${endpoint}`, {
        method: 'POST',
        headers,
        body: data ? JSON.stringify(data) : undefined,
        credentials: 'omit', // Changed to 'omit' since we're using JWT tokens stored in localStorage
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      console.error(`API POST error for ${endpoint}:`, error);

      // Check if it's a network error (TypeError with specific messages)
      if (error instanceof TypeError) {
        if (error.message.includes('fetch') || error.message.includes('network') || error.message.includes('Failed to fetch')) {
          throw new Error('Network error: Unable to connect to server. Please check your connection and ensure the server is running.');
        }
      }

      // Re-throw the original error if it's not a network error
      if (error instanceof Error) {
        throw error;
      }

      throw new Error(`Failed to submit data: ${error instanceof Error ? error.message : 'Network error'}`);
    }
  }

  // Generic PUT request
  async put<T>(endpoint: string, data?: any): Promise<T> {
    try {
      const headers = await this.getHeaders();

      // Ensure we have an authentication token before making the request
      if (!headers['Authorization'] && (endpoint.includes('/tasks') || (endpoint.includes('/auth/') && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/signup') && !endpoint.includes('/auth/me')))) {
        throw new Error('No authentication token available');
      }

      const response = await fetch(`${normalizeUrl(this.baseUrl)}${endpoint}`, {
        method: 'PUT',
        headers,
        body: data ? JSON.stringify(data) : undefined,
        credentials: 'omit', // Changed to 'omit' since we're using JWT tokens stored in localStorage
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      // Don't log errors for expected scenarios
      if (!(error instanceof TypeError && (error.message.includes('fetch') || error.message.includes('network') || error.message.includes('Failed to fetch')))) {
        console.error(`API PUT error for ${endpoint}:`, error);
      }

      // Check if it's a network error (TypeError with specific messages)
      if (error instanceof TypeError) {
        if (error.message.includes('fetch') || error.message.includes('network') || error.message.includes('Failed to fetch')) {
          // This could be a CORS issue or server accessibility issue
          console.warn(`Network/CORS error for PUT ${endpoint}. Server may be inaccessible or CORS not configured properly.`);
          throw new Error('Network error: Unable to connect to server. Please check your connection and ensure the server is running.');
        }
      }

      // Re-throw the original error if it's not a network error
      if (error instanceof Error) {
        throw error;
      }

      throw new Error(`Failed to update data: ${error instanceof Error ? error.message : 'Network error'}`);
    }
  }

  // Generic DELETE request
  async delete<T>(endpoint: string): Promise<T> {
    try {
      const headers = await this.getHeaders();

      // Ensure we have an authentication token before making the request (for protected endpoints)
      if (!headers['Authorization'] && (endpoint.includes('/tasks') || (endpoint.includes('/auth/') && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/signup') && !endpoint.includes('/auth/me')))) {
        throw new Error('No authentication token available');
      }

      const response = await fetch(`${normalizeUrl(this.baseUrl)}${endpoint}`, {
        method: 'DELETE',
        headers,
        credentials: 'omit', // Changed to 'omit' since we're using JWT tokens stored in localStorage
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      console.error(`API DELETE error for ${endpoint}:`, error);

      // Check if it's a network error (TypeError with specific messages)
      if (error instanceof TypeError) {
        if (error.message.includes('fetch') || error.message.includes('network') || error.message.includes('Failed to fetch')) {
          throw new Error('Network error: Unable to connect to server. Please check your connection and ensure the server is running.');
        }
      }

      // Re-throw the original error if it's not a network error
      if (error instanceof Error) {
        throw error;
      }

      throw new Error(`Failed to delete data: ${error instanceof Error ? error.message : 'Network error'}`);
    }
  }

  // Handle response and check for errors
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      // Handle different status codes
      if (response.status === 401) {
        // Unauthorized - token might be expired
        // Remove the invalid token
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth-token');
        }

        // Dispatch an unauthorized event to notify other parts of the app
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new Event('unauthorized'));
        }

        throw new Error('Unauthorized: Please log in again');
      } else if (response.status === 403) {
        // Forbidden - user doesn't have permission
        throw new Error('Forbidden: You do not have permission to access this resource');
      } else if (response.status === 404) {
        // Not found
        throw new Error('Resource not found');
      } else {
        // Other error - try to get detailed error information
        try {
          const errorData = await response.json();
          const errorMessage = errorData.detail || errorData.message || errorData.error || `HTTP error! status: ${response.status}`;
          throw new Error(errorMessage);
        } catch (e) {
          // If response is not JSON, try to get text
          try {
            const errorText = await response.text();
            throw new Error(errorText || `HTTP error! status: ${response.status}`);
          } catch (textError) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
        }
      }
    }

    // Handle responses with no content (e.g., 204 No Content)
    if (response.status === 204) {
      return {} as T;
    }

    // Parse JSON response
    try {
      const result = await response.json();
      return result;
    } catch (e) {
      // If response is not JSON, return as text
      const textResult = await response.text();
      return textResult as unknown as T;
    }
  }
}

// Create a singleton instance of the API client
export const apiClient = new ApiClient();

// Export individual methods for convenience
export const apiGet = <T>(endpoint: string) => apiClient.get<T>(endpoint);
export const apiPost = <T>(endpoint: string, data?: any) => apiClient.post<T>(endpoint, data);
export const apiPut = <T>(endpoint: string, data?: any) => apiClient.put<T>(endpoint, data);
export const apiDelete = <T>(endpoint: string) => apiClient.delete<T>(endpoint);

// Specific API functions for authentication-related endpoints
export const authApi = {
  // Login
  login: (credentials: { email: string; password: string }) =>
    apiClient.post('/auth/login', credentials),

  // Signup
  signup: (userData: { email: string; password: string; firstName?: string; lastName?: string }) =>
    apiClient.post('/auth/signup', userData),

  // Get current user
  getCurrentUser: () => apiClient.get('/auth/me'),
};

// Define the Task interface to be used in the API
interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

// Specific API functions for task-related endpoints (will be used in User Story 3)
export const taskApi = {
  // Get all tasks for current user
  getTasks: () => apiClient.get<Task[]>('/tasks'),

  // Create a new task
  createTask: (taskData: { title: string; description?: string; completed?: boolean }) =>
    apiClient.post<Task>('/tasks', taskData),

  // Get a specific task
  getTask: (taskId: string) => apiClient.get<Task>(`/tasks/${taskId}`),

  // Update a task
  updateTask: (taskId: string, taskData: Partial<Task>) =>
    apiClient.put<Task>(`/tasks/${taskId}`, taskData),

  // Delete a task
  deleteTask: (taskId: string) => apiClient.delete<Task>(`/tasks/${taskId}`),
};

// Add event listener for unauthorized events to handle token expiration globally
if (typeof window !== 'undefined') {
  window.addEventListener('unauthorized', () => {
    // Optionally redirect to login or show a notification
    console.log('Unauthorized access detected. Token may have expired.');

    // Dispatch a custom event that the auth provider can listen to
    window.dispatchEvent(new CustomEvent('auth-expired'));
  });
}