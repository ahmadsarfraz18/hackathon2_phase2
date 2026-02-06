# Authentication System Documentation

## Overview
This document describes the authentication system implemented for the Todo application. The system uses JWT-based stateless authentication with Better Auth for the frontend and FastAPI backend integration.

## Architecture
- **Frontend**: Next.js 16+ with Better Auth for user management
- **Backend**: FastAPI with JWT token verification
- **Database**: Neon PostgreSQL for user storage
- **Security**: Stateless JWT tokens with user isolation

## Components

### 1. Better Auth Configuration (frontend/src/auth.ts)
- JWT plugin enabled with 7-day expiration
- Email/password authentication
- Secure token handling

### 2. JWT Service (backend/src/services/auth.py)
- Token creation with user_id and email claims
- Token verification with expiration and signature checks
- Password hashing utilities

### 3. Security Utilities (backend/src/core/security.py)
- JWT validation middleware
- Secret key management
- Token expiration handling

### 4. User Model (backend/src/models/user.py)
- User authentication fields
- Password hash storage
- Email verification status

### 5. Authentication API (backend/src/api/auth.py)
- Signup endpoint with validation
- Login endpoint with JWT issuance
- Token refresh (placeholder implementation)

### 6. Task API with User Isolation (backend/src/api/task.py)
- User-specific task filtering
- Cross-user access prevention
- Proper 401/403 error responses

## Security Features

### JWT Token Structure
```json
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "exp": 1234567890
}
```

### User Isolation
- All task endpoints filter by authenticated user's ID
- Cross-user access attempts return 404 (not 403 to prevent enumeration)
- Authentication required for all protected endpoints

### Error Handling
- 401 Unauthorized: Missing or invalid tokens
- 404 Not Found: Access to resources owned by other users
- Proper validation of email format and password strength

## API Endpoints

### Authentication Endpoints
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - Authenticate and get JWT token
- `GET /auth/me` - Get current user info (requires valid token)

### Task Endpoints
- `GET /tasks` - Get all tasks for current user
- `POST /tasks` - Create new task for current user
- `GET /tasks/{id}` - Get specific task (must belong to user)
- `PUT /tasks/{id}` - Update specific task (must belong to user)
- `DELETE /tasks/{id}` - Delete specific task (must belong to user)

## Frontend Integration

### Authentication Hook (frontend/src/hooks/useAuth.ts)
- Manages user session state
- Handles login, signup, and logout
- Error handling and state management

### API Utilities (frontend/src/lib/api.ts)
- Automatic JWT token attachment to requests
- Error handling for 401/403 responses
- Session management

### Token Management (frontend/src/lib/authManager.ts)
- Token expiration monitoring
- Automatic refresh scheduling
- Secure storage utilities

## Environment Variables

### Required Variables
- `BETTER_AUTH_SECRET` - Secret key for JWT signing (should be long and random)
- `BETTER_AUTH_URL` - Base URL for Better Auth (e.g., http://localhost:3000)
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_EXPIRATION` - Token expiration time in seconds (default: 604800 for 7 days)

## Setup Instructions

1. Set environment variables in `.env` file (use `.env.example` as template)
2. Run database migrations (if applicable)
3. Start the backend server
4. Start the frontend application
5. Users can now signup/login and access their tasks

## Testing

The authentication system includes comprehensive tests:
- Contract tests for API endpoints
- Integration tests for signup/login flows
- Security tests for token validation and user isolation
- Error handling tests for various failure scenarios

## Security Considerations

- JWT tokens are stateless and validated using secret key
- User passwords are hashed using bcrypt
- All API endpoints enforce user isolation
- Token expiration prevents long-term access from compromised tokens
- Cross-user access attempts are prevented at the database level