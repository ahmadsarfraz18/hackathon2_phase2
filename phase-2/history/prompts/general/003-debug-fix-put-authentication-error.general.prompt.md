---
id: 003
title: Debug and fix PUT authentication network error in Next.js + Backend
stage: general
date: 2026-01-17
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: 001-todo-cli-core
user: Claude
command: "debug and fix PUT authentication network error"
labels: ["authentication", "cors", "api", "nextjs", "backend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/lib/api.ts
  - backend/src/main.py
  - frontend/src/app/dashboard/page.tsx
tests:
  - "Verified CORS configuration for PUT requests"
  - "Tested authentication header injection consistency"
---

## Prompt

# 🛠️ Debug & Fix PUT Authentication Network Error (Next.js + Backend)

## Role

You are a **senior full-stack engineer** with deep expertise in:

* Next.js App Router
* REST APIs
* Authentication (JWT / Bearer tokens)
* CORS & browser networking behavior

## Context (Confirmed Facts — do NOT question these)

* Backend is running on: `http://localhost:8000`

* `GET /health` returns:

  ```json
  { "status": "healthy" }
  ```

* Backend endpoints include (all protected):

  * `GET /tasks/{id}`
  * `PUT /tasks/{id}`

* Opening this in the browser:

  ```
  http://localhost:8000/tasks/1
  ```

  returns:

  ```json
  { "detail": "Not authenticated" }
  ```

  ✅ This confirms the endpoint is protected and requires Authorization.

* Frontend:

  * Next.js App Router (Turbopack)
  * Error occurs in:
    `ApiClient.put()`
    called from `src/app/dashboard/page.tsx`

* Behavior:

  * POST and DELETE requests work
  * PUT (edit task) fails with:

    ```
    Network error: Unable to connect to server
    ```

## Goal

Fix the **PUT /tasks/{id} (edit task)** functionality completely.

---

## Your Tasks

### 1️⃣ Root Cause Analysis

Explain clearly:

* Why PUT requests fail while GET/POST may appear to work
* How **missing Authorization headers** cause browser PUT requests to fail
* Why the browser shows a **"Network error" instead of a normal 401**

### 2️⃣ Authentication Fix (Frontend)

Provide a **production-ready solution** that:

* Injects the Bearer token into **ALL requests**, especially PUT
* Uses Axios interceptor or fetch wrapper
* Works correctly in a Next.js App Router client component

### 3️⃣ CORS Fix (Backend)

Show the **exact backend CORS configuration** required:

* Allow `Authorization` header
* Allow `OPTIONS` preflight
* Support `PUT` method

### 4️⃣ Correct Code Examples

Provide **minimal but complete examples** of:

* `api.ts` (token injection)
* Edit handler (e.g. `handleToggleTask`)
* Any required middleware or configuration

---

## Important Rules

* ❌ Do NOT give partial solutions
* ✅ Provide complete, copy-paste ready solutions

## Response snapshot

## 1️⃣ Root Cause Analysis

### Why PUT requests fail while GET/POST work

The issue stems from several factors related to how browsers handle different HTTP methods and CORS preflight requests:

1. **CORS Preflight Behavior**: Unlike GET and POST requests (which are "simple" requests), PUT requests typically trigger a CORS preflight request (OPTIONS) to verify that the server allows the request. If the preflight request fails, the actual PUT request never reaches the server.

2. **Different Authentication Handling**: As I identified earlier, the API client's PUT method had stricter authentication requirements than GET/POST methods. The PUT method required an Authorization header for ALL requests, while GET/POST only required it for specific endpoints.

3. **Browser Security Model**: When a CORS preflight request fails, browsers deliberately obscure the actual error details to prevent information leakage. Instead of showing the actual server response (like a 401 Unauthorized), the browser returns a generic "Network error".

## 2️⃣ How Missing Authorization Headers Cause Browser PUT Requests to Fail

When a PUT request lacks proper Authorization headers:

1. The browser sends a preflight OPTIONS request to the server
2. The server receives the request but sees no Authorization header
3. The server responds with an error (likely 401/403) to the OPTIONS request
4. The browser considers the preflight to have failed
5. The actual PUT request is never sent
6. The browser reports a "Network error" instead of the actual server response

## 3️⃣ Why Browser Shows "Network Error" Instead of Normal 401

Browsers intentionally mask CORS failures to protect security. When a CORS preflight request fails:

- The browser returns a generic `TypeError: Failed to fetch` or "Network error"
- Actual server error details (like 401 Unauthorized) are hidden
- This prevents malicious sites from learning about server internals
- The error appears as a network-level issue rather than an application-level authentication error

## 2️⃣ Authentication Fix (Frontend)

Here's a production-ready solution that injects the Bearer token into ALL requests, especially PUT:

### Updated `api.ts` with Consistent Token Injection

```typescript
// Base API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Create a base API client with common configuration
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Common headers for all requests with consistent authentication
  private async getHeaders(): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    // Always check for token in browser environment
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth-token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  // Generic GET request
  async get<T>(endpoint: string): Promise<T> {
    try {
      const headers = await this.getHeaders();

      // Check authentication for protected endpoints
      if (!headers['Authorization'] && this.isProtectedEndpoint(endpoint)) {
        throw new Error('No authentication token available');
      }

      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'GET',
        headers,
        credentials: 'include',
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      this.handleError('GET', endpoint, error);
      throw error;
    }
  }

  // Generic POST request
  async post<T>(endpoint: string, data?: any): Promise<T> {
    try {
      const headers = await this.getHeaders();

      // Check authentication for protected endpoints
      if (!headers['Authorization'] && this.isProtectedEndpoint(endpoint)) {
        throw new Error('No authentication token available');
      }

      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers,
        body: data ? JSON.stringify(data) : undefined,
        credentials: 'include',
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      this.handleError('POST', endpoint, error);
      throw error;
    }
  }

  // Fixed PUT request with consistent authentication handling
  async put<T>(endpoint: string, data?: any): Promise<T> {
    try {
      const headers = await this.getHeaders();

      // Apply the same authentication check as other methods
      if (!headers['Authorization'] && this.isProtectedEndpoint(endpoint)) {
        throw new Error('No authentication token available');
      }

      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'PUT',
        headers,
        body: data ? JSON.stringify(data) : undefined,
        credentials: 'include',
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      this.handleError('PUT', endpoint, error);
      throw error;
    }
  }

  // Generic DELETE request
  async delete<T>(endpoint: string): Promise<T> {
    try {
      const headers = await this.getHeaders();

      // Check authentication for protected endpoints
      if (!headers['Authorization'] && this.isProtectedEndpoint(endpoint)) {
        throw new Error('No authentication token available');
      }

      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'DELETE',
        headers,
        credentials: 'include',
      });

      return this.handleResponse<T>(response);
    } catch (error) {
      this.handleError('DELETE', endpoint, error);
      throw error;
    }
  }

  // Helper to determine if endpoint requires authentication
  private isProtectedEndpoint(endpoint: string): boolean {
    return endpoint.includes('/tasks') || endpoint.includes('/auth') && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/signup');
  }

  // Centralized error handling
  private handleError(method: string, endpoint: string, error: any): void {
    console.error(`API ${method} error for ${endpoint}:`, error);

    // Check if it's a network error
    if (error instanceof TypeError) {
      if (error.message.includes('fetch') || error.message.includes('network') || error.message.includes('Failed to fetch')) {
        throw new Error('Network error: Unable to connect to server. Please check your connection and ensure the server is running.');
      }
    }

    if (error instanceof Error) {
      throw error;
    }

    throw new Error(`Failed to ${method.toLowerCase()} data: ${error instanceof Error ? error.message : 'Network error'}`);
  }

  // Handle response and check for errors
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      if (response.status === 401) {
        // Unauthorized - remove invalid token
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth-token');
        }
        throw new Error('Unauthorized: Please log in again');
      } else if (response.status === 403) {
        throw new Error('Forbidden: You do not have permission to access this resource');
      } else if (response.status === 404) {
        throw new Error('Resource not found');
      } else {
        try {
          const errorData = await response.json();
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        } catch (e) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }
    }

    if (response.status === 204) {
      return {} as T;
    }

    try {
      return await response.json();
    } catch (e) {
      return response.text() as unknown as T;
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

// Specific API functions for task-related endpoints
export const taskApi = {
  // Get all tasks for current user
  getTasks: () => apiClient.get<Task[]>('/tasks'),

  // Create a new task
  createTask: (taskData: { title: string; description?: string; completed?: boolean }) =>
    apiClient.post('/tasks', taskData),

  // Get a specific task
  getTask: (taskId: string) => apiClient.get(`/tasks/${taskId}`),

  // Fixed: Update a task with consistent authentication
  updateTask: (taskId: string, taskData: any) =>
    apiClient.put(`/tasks/${taskId}`, taskData),

  // Delete a task
  deleteTask: (taskId: string) => apiClient.delete(`/tasks/${taskId}`),
};
```

## 3️⃣ CORS Fix (Backend)

Here's the exact backend CORS configuration required in `backend/src/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.auth import router as auth_router
from .api.task import router as task_router
from .core.database import create_db_and_tables
from .models import User, Task  # Import models to register with SQLModel metadata


def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Todo API with Authentication",
        description="A secure todo application API with JWT-based authentication and user isolation",
        version="1.0.0"
    )

    # Add CORS middleware with explicit configuration for PUT requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",    # Next.js default
            "http://localhost:3001",    # Next.js alternative
            "http://localhost:8000",    # Self-origin for testing
            "http://127.0.0.1:3000",    # Alternative localhost format
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly include PUT and OPTIONS
        allow_headers=[
            "Authorization",            # Critical for JWT tokens
            "Content-Type",             # Standard content type
            "X-Requested-With",         # Common header
            "Accept",
            "Origin",
            "Cache-Control",
            "X-Requested-With",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
        ],
    )

    # Include API routers
    app.include_router(auth_router)
    app.include_router(task_router)

    # Create database tables on startup
    @app.on_event("startup")
    def on_startup():
        create_db_and_tables()

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 4️⃣ Complete Code Examples

### Updated Edit Handler (`handleToggleTask`)

```typescript
const handleToggleTask = async (taskId: string, completed: boolean) => {
  try {
    console.log('Debug: handleToggleTask called with taskId:', taskId);

    // Validate inputs
    if (!taskId || taskId === 'undefined' || taskId === '') {
      throw new Error('Invalid task ID provided');
    }

    // Verify token exists before making request
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth-token') : null;
    if (!token) {
      throw new Error('No authentication token available. Please log in again.');
    }

    console.log('Debug: Making PUT request to update task');

    const updatedTask = await taskApi.updateTask(taskId, {
      completed: !completed
    });

    console.log('Debug: Task updated successfully:', updatedTask);

    // Update local state optimistically
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === taskId ? { ...updatedTask } : task
      )
    );
  } catch (err: any) {
    console.error('Error updating task:', err);

    // Handle specific error types
    if (err.message?.includes('Unauthorized') ||
        err.message?.includes('Please log in again') ||
        err.message?.includes('Not authenticated')) {
      // Force logout and redirect to login
      await logout();
      return;
    }

    // Handle network errors specifically
    if (err.message?.includes('Network error') ||
        err.message?.includes('Unable to connect') ||
        err.message?.includes('Failed to fetch')) {
      setError('Unable to connect to server. Please check your connection and try again.');
    } else {
      setError(err.message || 'Failed to update task');
    }
  }
};
```

The key fixes implemented:

1. **Consistent Authentication Logic**: All HTTP methods (GET, POST, PUT, DELETE) now have the same authentication check logic
2. **Proper CORS Configuration**: Explicitly allows PUT and OPTIONS methods with Authorization header
3. **Robust Error Handling**: Better error classification and messaging
4. **Token Validation**: Checks for token existence before making requests

This solution addresses the root cause where PUT requests were failing due to inconsistent authentication handling and improper CORS configuration, ensuring that PUT requests work reliably in the Next.js App Router environment.

## Outcome

- ✅ Impact: Fixed PUT authentication network error in Next.js + Backend
- 🧪 Tests: Verified CORS configuration and authentication header consistency
- 📁 Files: Updated api.ts, main.py, and page.tsx with complete solutions
- 🔁 Next prompts: Could implement token refresh mechanisms
- 🧠 Reflection: Inconsistent auth validation caused CORS preflight failures

## Evaluation notes (flywheel)

- Failure modes observed: CORS preflight failure masking actual 401 errors
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add token refresh on expiration