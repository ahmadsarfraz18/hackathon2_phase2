from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from ..models.task import Task, TaskCreate, TaskUpdate, TaskRead
from ..models.user import User
from ..api.deps import get_current_user_from_token
from ..core.database import get_db


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[TaskRead])
async def get_tasks(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Get all tasks for the current user.

    Args:
        current_user: Authenticated user whose tasks to retrieve
        db: Database session dependency

    Returns:
        List of tasks belonging to the current user
    """
    # Query tasks filtered by the current user's ID
    statement = select(Task).where(Task.user_id == current_user.id)
    results = db.execute(statement).scalars().all()
    return results


@router.post("/", response_model=TaskRead)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Create a new task for the current user.

    Args:
        task: Task creation data
        current_user: Authenticated user creating the task
        db: Database session dependency

    Returns:
        Created task
    """
    # Ensure the task is assigned to the current user
    # Override any user_id that might have been provided in the request
    db_task = Task(
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=current_user.id,  # Force user_id to be the current user's ID
        due_date=task.due_date
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Get a specific task by ID.

    Args:
        task_id: ID of the task to retrieve
        current_user: Authenticated user requesting the task
        db: Database session dependency

    Returns:
        Task if it belongs to the current user

    Raises:
        HTTPException: If task doesn't exist or doesn't belong to the user
    """
    try:
        # Convert task_id string to UUID to match the database field type
        import uuid
        task_uuid = uuid.UUID(task_id)

        # Get the task and ensure it belongs to the current user
        statement = select(Task).where(Task.id == task_uuid).where(Task.user_id == current_user.id)
        result = db.execute(statement).scalar_one_or_none()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to current user"
            )

        return result
    except ValueError:
        # Invalid UUID format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Update a specific task by ID (full update).

    Args:
        task_id: ID of the task to update
        task_update: Task update data
        current_user: Authenticated user updating the task
        db: Database session dependency

    Returns:
        Updated task

    Raises:
        HTTPException: If task doesn't exist or doesn't belong to the user
    """
    try:
        # Convert task_id string to UUID to match the database field type
        import uuid
        task_uuid = uuid.UUID(task_id)

        # Get the task and ensure it belongs to the current user
        statement = select(Task).where(Task.id == task_uuid).where(Task.user_id == current_user.id)
        db_task = db.execute(statement).scalar_one_or_none()

        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to the current user"
            )

        # Update the task with the provided data
        for field, value in task_update.dict(exclude_unset=True).items():
            setattr(db_task, field, value)

        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except ValueError:
        # Invalid UUID format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )
    except Exception as e:
        # Log the error in a real application
        print(f"Update task error: {str(e)}")  # For debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )


@router.patch("/{task_id}", response_model=TaskRead)
async def partial_update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Partially update a specific task by ID.

    Args:
        task_id: ID of the task to update
        task_update: Task update data (only provided fields will be updated)
        current_user: Authenticated user updating the task
        db: Database session dependency

    Returns:
        Updated task

    Raises:
        HTTPException: If task doesn't exist or doesn't belong to the user
    """
    try:
        # Convert task_id string to UUID to match the database field type
        import uuid
        task_uuid = uuid.UUID(task_id)

        # Get the task and ensure it belongs to the current user
        statement = select(Task).where(Task.id == task_uuid).where(Task.user_id == current_user.id)
        db_task = db.execute(statement).scalar_one_or_none()

        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to the current user"
            )

        # Update only the fields that are provided in the request
        for field, value in task_update.dict(exclude_unset=True).items():
            setattr(db_task, field, value)

        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except ValueError:
        # Invalid UUID format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )
    except Exception as e:
        # Log the error in a real application
        print(f"Partial update task error: {str(e)}")  # For debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Delete a specific task by ID.

    Args:
        task_id: ID of the task to delete
        current_user: Authenticated user deleting the task
        db: Database session dependency

    Returns:
        Success message

    Raises:
        HTTPException: If task doesn't exist or doesn't belong to the user
    """
    try:
        # Convert task_id string to UUID to match the database field type
        import uuid
        task_uuid = uuid.UUID(task_id)

        # Get the task and ensure it belongs to the current user
        statement = select(Task).where(Task.id == task_uuid).where(Task.user_id == current_user.id)
        db_task = db.execute(statement).scalar_one_or_none()

        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to current user"
            )

        # Delete the task
        db.delete(db_task)
        db.commit()
        return {"message": "Task deleted successfully"}
    except ValueError:
        # Invalid UUID format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )