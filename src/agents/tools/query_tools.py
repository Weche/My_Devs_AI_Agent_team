"""Query tools for project and task information"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.database import (
    get_session,
    get_project_by_name,
    get_active_projects,
    Project,
    Task,
)


def get_project_summary_tool(project_name: str) -> str:
    """
    Get a summary of tasks by status for a project.

    Args:
        project_name: Name of the project

    Returns:
        Summary of task counts by status
    """
    session = get_session()

    try:
        project = get_project_by_name(session, project_name)
        if not project:
            return f"Error: Project '{project_name}' not found"

        # Get task counts by status
        task_counts = (
            session.query(Task.status, func.count(Task.id))
            .filter(Task.project_id == project.id)
            .group_by(Task.status)
            .all()
        )

        total_tasks = sum(count for _, count in task_counts)

        if total_tasks == 0:
            return f"Project '{project_name}' has no tasks yet."

        # Format summary
        summary = [f"Project: {project_name}"]
        summary.append(f"Total tasks: {total_tasks}")
        summary.append("\nBy status:")

        for status, count in task_counts:
            percentage = (count / total_tasks) * 100
            summary.append(f"  • {status}: {count} ({percentage:.0f}%)")

        return "\n".join(summary)

    except Exception as e:
        return f"Error getting project summary: {str(e)}"
    finally:
        session.close()


def get_project_warnings_tool(project_name: str) -> str:
    """
    Get warnings for a project (overdue tasks, blocked tasks > 3 days, etc.).

    Args:
        project_name: Name of the project

    Returns:
        List of warnings
    """
    session = get_session()

    try:
        project = get_project_by_name(session, project_name)
        if not project:
            return f"Error: Project '{project_name}' not found"

        warnings = []

        # Check overdue tasks
        now = datetime.utcnow()
        overdue_tasks = (
            session.query(Task)
            .filter(
                Task.project_id == project.id,
                Task.due_date < now,
                Task.status != "done",
            )
            .all()
        )

        if overdue_tasks:
            warnings.append(f"⚠️  {len(overdue_tasks)} overdue task(s):")
            for task in overdue_tasks[:5]:  # Show max 5
                days_overdue = (now - task.due_date).days
                warnings.append(f"  • #{task.id}: {task.title} ({days_overdue} days overdue)")

        # Check blocked tasks > 3 days
        three_days_ago = now - timedelta(days=3)
        blocked_tasks = (
            session.query(Task)
            .filter(
                Task.project_id == project.id,
                Task.status == "blocked",
                Task.updated_at < three_days_ago,
            )
            .all()
        )

        if blocked_tasks:
            warnings.append(f"\n⚠️  {len(blocked_tasks)} task(s) blocked > 3 days:")
            for task in blocked_tasks[:5]:
                days_blocked = (now - task.updated_at).days
                warnings.append(f"  • #{task.id}: {task.title} ({days_blocked} days)")

        # Check unassigned high priority tasks
        unassigned_high = (
            session.query(Task)
            .filter(
                Task.project_id == project.id,
                Task.assigned_to == None,
                Task.priority.in_(["critical", "high"]),
                Task.status == "todo",
            )
            .all()
        )

        if unassigned_high:
            warnings.append(f"\n⚠️  {len(unassigned_high)} unassigned high-priority task(s):")
            for task in unassigned_high[:5]:
                warnings.append(f"  • #{task.id}: {task.title} ({task.priority})")

        if not warnings:
            return f"✓ No warnings for project '{project_name}'"

        return "\n".join(warnings)

    except Exception as e:
        return f"Error getting warnings: {str(e)}"
    finally:
        session.close()


def get_all_projects_tool() -> str:
    """
    Get a list of all active projects.

    Returns:
        List of active projects with basic info
    """
    session = get_session()

    try:
        projects = get_active_projects(session)

        if not projects:
            return "No active projects found."

        lines = ["Active Projects:"]
        for project in projects:
            task_count = session.query(Task).filter(Task.project_id == project.id).count()
            lines.append(
                f"  • {project.name} ({task_count} tasks, priority: {project.priority})"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"Error getting projects: {str(e)}"
    finally:
        session.close()


def get_blocked_tasks_tool(project_name: str) -> str:
    """
    Get all blocked tasks for a project.

    Args:
        project_name: Name of the project

    Returns:
        List of blocked tasks
    """
    session = get_session()

    try:
        project = get_project_by_name(session, project_name)
        if not project:
            return f"Error: Project '{project_name}' not found"

        blocked_tasks = (
            session.query(Task)
            .filter(Task.project_id == project.id, Task.status == "blocked")
            .order_by(Task.updated_at.asc())
            .all()
        )

        if not blocked_tasks:
            return f"No blocked tasks in project '{project_name}'"

        lines = [f"Blocked tasks in {project_name}:"]
        for task in blocked_tasks:
            days_blocked = (datetime.utcnow() - task.updated_at).days
            lines.append(
                f"  #{task.id} [{task.priority}] {task.title} (blocked {days_blocked} days)"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"Error getting blocked tasks: {str(e)}"
    finally:
        session.close()


def get_overdue_tasks_tool(project_name: str) -> str:
    """
    Get all overdue tasks for a project.

    Args:
        project_name: Name of the project

    Returns:
        List of overdue tasks
    """
    session = get_session()

    try:
        project = get_project_by_name(session, project_name)
        if not project:
            return f"Error: Project '{project_name}' not found"

        now = datetime.utcnow()
        overdue_tasks = (
            session.query(Task)
            .filter(
                Task.project_id == project.id,
                Task.due_date < now,
                Task.status != "done",
            )
            .order_by(Task.due_date.asc())
            .all()
        )

        if not overdue_tasks:
            return f"No overdue tasks in project '{project_name}'"

        lines = [f"Overdue tasks in {project_name}:"]
        for task in overdue_tasks:
            days_overdue = (now - task.due_date).days
            lines.append(
                f"  #{task.id} [{task.priority}] {task.title} ({days_overdue} days overdue)"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"Error getting overdue tasks: {str(e)}"
    finally:
        session.close()
