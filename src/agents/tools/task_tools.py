"""Task management tools for CrewAI agents"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from src.core.database import (
    get_session,
    get_project_by_name,
    get_tasks_by_project,
    Task,
)


def create_task_tool(
    project_name: str,
    title: str,
    description: str = "",
    priority: str = "medium",
    assigned_to: Optional[str] = None,
    due_date: Optional[str] = None,
) -> str:
    """
    Create a new task for a project.

    Args:
        project_name: Name of the project
        title: Task title
        description: Task description (optional)
        priority: Priority level (critical, high, medium, low)
        assigned_to: Agent to assign task to (optional)
        due_date: Due date in ISO format or natural language (optional)

    Returns:
        Success message with task ID
    """
    from dateutil import parser

    session = get_session()

    try:
        # Get project
        project = get_project_by_name(session, project_name)
        if not project:
            return f"Error: Project '{project_name}' not found"

        # Auto-assign priority based on keywords if not specified
        if priority == "medium" and title:
            title_lower = title.lower()
            if any(word in title_lower for word in ["critical", "urgent", "asap", "emergency"]):
                priority = "critical"
            elif any(word in title_lower for word in ["important", "high", "priority"]):
                priority = "high"
            elif any(word in title_lower for word in ["fix", "bug", "error", "issue"]):
                priority = "high"
            elif any(word in title_lower for word in ["low", "minor", "someday"]):
                priority = "low"

        # Parse due date if provided
        parsed_due_date = None
        if due_date:
            try:
                # Try parsing natural language dates like "next Saturday", "Friday", etc.
                parsed_due_date = parser.parse(due_date, fuzzy=True)
            except:
                # If parsing fails, leave as None
                pass

        # Create task
        task = Task(
            project_id=project.id,
            title=title,
            description=description,
            priority=priority,
            assigned_to=assigned_to,
            created_by="pm_agent",
            status="todo",
            due_date=parsed_due_date,
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        due_str = f", due: {parsed_due_date.strftime('%Y-%m-%d')}" if parsed_due_date else ""
        return f"✓ Created task #{task.id}: {title} (priority: {priority}{due_str})"

    except Exception as e:
        session.rollback()
        return f"Error creating task: {str(e)}"
    finally:
        session.close()


def update_task_status_tool(task_id: int, new_status: str) -> str:
    """
    Update the status of a task.

    Args:
        task_id: ID of the task
        new_status: New status (todo, in_progress, blocked, review, done)

    Returns:
        Success or error message
    """
    session = get_session()

    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            return f"Error: Task #{task_id} not found"

        old_status = task.status
        task.status = new_status
        task.updated_at = datetime.utcnow()

        if new_status == "done" and not task.completed_at:
            task.completed_at = datetime.utcnow()

        session.commit()

        return f"✓ Updated task #{task_id} status: {old_status} → {new_status}"

    except Exception as e:
        session.rollback()
        return f"Error updating task: {str(e)}"
    finally:
        session.close()


def get_tasks_tool(
    project_name: str,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
) -> str:
    """
    Get tasks for a project with optional filters.

    Args:
        project_name: Name of the project
        status: Filter by status (optional)
        assigned_to: Filter by assignee (optional)

    Returns:
        Formatted list of tasks
    """
    session = get_session()

    try:
        project = get_project_by_name(session, project_name)
        if not project:
            return f"Error: Project '{project_name}' not found"

        tasks = get_tasks_by_project(session, project.id, status, assigned_to)

        if not tasks:
            return f"No tasks found for project '{project_name}'"

        # Format tasks
        lines = [f"Tasks for {project_name}:"]
        for task in tasks:
            lines.append(
                f"  #{task.id} [{task.status}] ({task.priority}) {task.title}"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"Error fetching tasks: {str(e)}"
    finally:
        session.close()


def get_task_details_tool(task_id: int) -> str:
    """
    Get detailed information about a specific task.

    Args:
        task_id: ID of the task

    Returns:
        Detailed task information
    """
    session = get_session()

    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            return f"Error: Task #{task_id} not found"

        details = [
            f"Task #{task.id}: {task.title}",
            f"  Status: {task.status}",
            f"  Priority: {task.priority}",
            f"  Assigned to: {task.assigned_to or 'Unassigned'}",
            f"  Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"  Description: {task.description or 'No description'}",
        ]

        return "\n".join(details)

    except Exception as e:
        return f"Error fetching task details: {str(e)}"
    finally:
        session.close()


def assign_task_tool(task_id: int, agent_name: str) -> str:
    """
    Assign a task to an agent.

    Args:
        task_id: ID of the task
        agent_name: Name of the agent to assign to

    Returns:
        Success or error message
    """
    session = get_session()

    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            return f"Error: Task #{task_id} not found"

        task.assigned_to = agent_name
        task.updated_at = datetime.utcnow()
        session.commit()

        return f"✓ Assigned task #{task_id} to {agent_name}"

    except Exception as e:
        session.rollback()
        return f"Error assigning task: {str(e)}"
    finally:
        session.close()
