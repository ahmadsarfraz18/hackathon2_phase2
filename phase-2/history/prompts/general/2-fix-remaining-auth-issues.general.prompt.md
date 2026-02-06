---
id: 2
title: Fix Remaining Authentication Issues
stage: general
date: 2026-02-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: Fix remaining authentication issues causing 'Uncaught (in promise) Object' errors
labels: ["authentication", "promise-error", "race-condition", "bug-fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/auth.ts
  - frontend/src/hooks/useAuth.tsx
  - frontend/src/app/dashboard/page.tsx
  - frontend/src/lib/api.ts
  - frontend/src/components/ErrorBoundary.tsx
  - frontend/src/app/login/page.tsx
tests: []
outcome: Fixed remaining authentication issues including promise errors and race conditions
evaluation: Resolved 'Uncaught (in promise) Object' errors and improved authentication flow stability
---

# Fix Remaining Authentication Issues

## Issue Summary
Addressed remaining authentication issues that were causing 'Uncaught (in promise) Object' errors and continued 'Access Denied' problems after login. The root causes included improper promise handling, race conditions in useEffect, and improper logout calls within async operations.

## Root Causes Identified
1. **Promise Handling in useEffect**: The dashboard's useEffect was calling async logout() inside a catch block, causing potential promise rejection issues
2. **Race Conditions**: Multiple state updates occurring simultaneously causing inconsistent auth states
3. **Improper Error Handling**: Generic object errors were not being properly caught and handled
4. **Dependency Array Issues**: Including logout function in useEffect dependencies was causing infinite re-renders
5. **Component Unmount Issues**: No cleanup for async operations causing state updates on unmounted components

## Fixes Implemented

### 1. Secure Promise Handling in Dashboard (`frontend/src/app/dashboard/page.tsx`)
- Added `isCancelled` flag to prevent state updates after component unmounts
- Removed `logout` from useEffect dependencies to prevent infinite re-renders
- Replaced `await logout()` with `setTimeout(() => logout(), 0)` to safely call logout after current call stack
- Added proper cleanup function in useEffect

### 2. Improved Error Handling in Auth Functions (`frontend/src/auth.ts`)
- Enhanced `useSession` function with proper 'unknown' type handling
- Added specific checks for generic object errors to prevent "Uncaught (in promise) Object" errors
- Improved error logging with more detailed information

### 3. Enhanced Auth Provider (`frontend/src/hooks/useAuth.tsx`)
- Added `isCancelled` flag to prevent state updates after component unmounts in session checking
- Added small delay after login to ensure token is properly stored in localStorage
- Added event listener for 'auth-expired' events to handle token expiration globally

### 4. Robust API Client (`frontend/src/lib/api.ts`)
- Updated unauthorized event handling to dispatch custom 'auth-expired' events
- Improved error handling for all HTTP methods
- Enhanced token cleanup on unauthorized responses

### 5. Enhanced Error Boundary (`frontend/src/components/ErrorBoundary.tsx`)
- Added specific handling for generic object errors
- Improved error logging for debugging purposes

### 6. Secure Logout Handling in All Task Operations
- Updated all task operations (add, toggle, delete, edit) to use `setTimeout` for logout calls
- Added proper error checking with optional chaining (`err?.message`)

### 7. Improved Login Flow (`frontend/src/app/login/page.tsx`)
- Changed navigation to use `window.location.href` instead of `router.push` for better state synchronization
- Added small delay to ensure auth state is properly updated before navigation

## Files Modified
- `frontend/src/app/dashboard/page.tsx`: Fixed promise handling and race conditions
- `frontend/src/auth.ts`: Enhanced error handling in useSession
- `frontend/src/hooks/useAuth.tsx`: Added cleanup and improved session checking
- `frontend/src/lib/api.ts`: Enhanced unauthorized event handling
- `frontend/src/components/ErrorBoundary.tsx`: Added generic object error handling
- `frontend/src/app/login/page.tsx`: Improved navigation after login

## Outcome
- Eliminated 'Uncaught (in promise) Object' errors
- Fixed race conditions in authentication state management
- Improved error handling for generic object errors
- Prevented infinite re-renders in useEffect
- Enhanced security with proper component unmount cleanup
- Improved user experience with reliable post-login navigation

## Testing
Manual testing confirmed that:
- No more 'Uncaught (in promise) Object' errors appear in console
- Dashboard properly loads after login without requiring refresh
- Proper error handling for all authentication scenarios
- Secure state management preventing updates on unmounted components
- Reliable logout handling across all operations