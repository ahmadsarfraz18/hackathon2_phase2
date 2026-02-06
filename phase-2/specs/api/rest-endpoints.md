# API Specification: REST Endpoints

**Feature Branch**: `003-api-contract`
**Created**: 2026-01-08
**Status**: Draft

## Overview
This document defines the RESTful API endpoints for the Todo Application backend. All endpoints are prefixed with `/api` and require JWT authentication.

## Global Requirements
- **Content-Type**: `application/json`
- **Authentication**: `Authorization: Bearer <JWT>`
- **Response Format**: Standard JSON responses.
- **Error Handling**: Standard HTTP status codes (400, 401, 403, 404, 500).

## Endpoints

### 1. Task Management

#### GET /api/tasks
List all tasks for the authenticated user.
- **Authentication Required**: Yes.
- **Query Parameters**:
  - `status`: (optional) `completed` or `pending`.
  - `priority`: (optional) integer 0-2.
- **Success Response**: `200 OK` with code `Array<Task>`.
- **Constraint**: Must only return tasks where `task.user_id == authenticated_user_id`.

#### POST /api/tasks
Create a new task.
- **Authentication Required**: Yes.
- **Request Body**:
  ```json
  {
    "title": "string",
    "description": "string",
    "priority": 1
  }
  ```
- **Success Response**: `201 Created` with the created `Task` object.
- **Logic**: Backend automatically assigns the `user_id` from the JWT.

#### GET /api/tasks/{task_id}
Get details of a specific task.
- **Authentication Required**: Yes.
- **Success Response**: `200 OK` with `Task`.
- **Error Response**: `404 Not Found` if task doesn't exist or belongs to another user.

#### PUT /api/tasks/{task_id}
Update an existing task.
- **Authentication Required**: Yes.
- **Request Body**: Partial `Task` update fields.
- **Success Response**: `200 OK` with updated `Task`.

#### DELETE /api/tasks/{task_id}
Delete a task.
- **Authentication Required**: Yes.
- **Success Response**: `204 No Content`.

### 2. User Info (Optional/Future)

#### GET /api/me
Get current authenticated user details extracted from JWT.
- **Authentication Required**: Yes.
- **Success Response**: `200 OK` with `{ "id": "uuid", "email": "email" }`.

## Error Schema
```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

---
*Created by fastapi_api_builder*
