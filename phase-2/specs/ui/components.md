# UI Specification: Components

**Feature Branch**: `004-ui-system`
**Created**: 2026-01-08

## Core Components

### 1. Layout & Shell
- **Navbar**: App logo, Profile/Logout dropdown, Theme toggle.
- **SideNav**: Filters (All, Completed, Pending), Categories.
- **AppLayout**: Persistent component wrapping protected pages.

### 2. Task Interface
- **TaskCard**: Displays title, status, priority, and actions (edit, delete, toggle).
- **TaskList**: Grid or list of TaskCards with empty state support.
- **AddTaskForm**: Inline input or modal for creating new tasks.
- **PriorityBadge**: Color-coded indicator for task priority.

### 3. Authentication
- **LoginForm**: Standard credentials form with Better Auth integration.
- **SignupForm**: New user registration with validation.
- **AuthGuard**: Wrapper for protected routes (redirects to login if unauthenticated).

## Styling
- **Framework**: Tailwind CSS.
- **Theme**: Dark/Light mode support (Radix UI / Shancn).
- **Responsiveness**: Mobile-first grid (1 column on mobile, 2-3 on desktop).

---
*Created by nextjs_ui_builder*
