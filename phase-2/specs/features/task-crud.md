# Feature Specification: Task CRUD

**Feature Branch**: `005-task-crud`
**Created**: 2026-01-08

## Description
Core task management functionality including creating, reading, updating, and deleting tasks, with strict user-level partitioning.

## User Scenarios

### Scenario 1: Create Task
- **Action**: User inputs a title and optional description.
- **Outcome**: Task is created in the database and linked to the user's ID.

### Scenario 2: List Tasks
- **Action**: User views their dashboard.
- **Outcome**: Only tasks belonging to the current user are listed.

### Scenario 3: Complete Task
- **Action**: User toggles the completion checkbox.
- **Outcome**: `is_completed` status is updated in the database.

### Scenario 4: Delete Task
- **Action**: User clicks delete.
- **Outcome**: The specific task record is removed.

## Requirements
- **FR-001**: Every task MUST have a non-empty title.
- **FR-002**: Every task MUST be associated with the authenticated `user_id`.
- **FR-003**: Bulk actions (e.g., mark all as completed) should be supported.

---
*Managed by spec_kit_manager*
