"""Proactive Tools - Auto-assignment and suggestion tools for Albedo"""

from typing import Optional
from src.core.database import get_session, get_active_projects, Task
from src.agents.tools.task_tools import get_tasks_tool
from src.agents.tools.query_tools import get_project_warnings_tool
from src.agents.tools.multi_agent_tools import execute_with_specialist_agent


def auto_assign_task(task_id: int) -> str:
    """
    Intelligently assign a task to the appropriate specialist agent based on task content.

    Uses multi-agent system with Frontend, Backend, and Database specialists.

    Args:
        task_id: Task ID to assign

    Returns:
        Assignment result message
    """
    session = get_session()
    task = session.query(Task).filter(Task.id == task_id).first()
    session.close()

    if not task:
        return f"❌ Task #{task_id} not found"

    title_lower = task.title.lower()
    description_lower = (task.description or "").lower()
    combined = f"{title_lower} {description_lower}"

    # Architecture/review keywords → Lead Dev Agent (Claude/Human)
    architecture_keywords = [
        'review code', 'architecture', 'design plan', 'evaluate architecture',
        'refactor strategy', 'code review', 'technical design'
    ]

    # Check if it needs architectural review
    if any(kw in combined for kw in architecture_keywords):
        return f"🎯 Task #{task_id} requires Lead Dev Agent (architecture/review)\n" \
               f"Task: {task.title}\n" \
               f"This task needs human expertise for architectural decisions."

    # Otherwise, use specialist agent (auto-detects frontend/backend/database)
    result = execute_with_specialist_agent(task_id)
    return result


def suggest_next_actions(project_name: Optional[str] = None) -> str:
    """
    Analyze current state and suggest next actions proactively.

    Args:
        project_name: Optional specific project to analyze (default: all active projects)

    Returns:
        Suggested actions message
    """
    session = get_session()

    if project_name:
        from src.core.database import get_project_by_name
        project = get_project_by_name(session, project_name)
        projects = [project] if project else []
    else:
        projects = get_active_projects(session)

    session.close()

    if not projects:
        return "✅ No active projects found"

    suggestions = []

    for project in projects:
        # Get warnings (overdue, blocked tasks)
        warnings = get_project_warnings_tool(project.name)

        # Get TODO tasks
        todo_tasks = get_tasks_tool(project.name, status="todo")

        # Get in-progress tasks
        in_progress = get_tasks_tool(project.name, status="in_progress")

        project_suggestions = []

        # Check for warnings
        if "⚠️" in warnings or "Overdue" in warnings:
            project_suggestions.append("🚨 Overdue tasks need attention - suggest expediting")

        if "Blocked" in warnings:
            project_suggestions.append("🔒 Blocked tasks need investigation")

        # Check if no tasks in progress
        if "No tasks found" in in_progress or "0 tasks" in in_progress:
            if "Task #" in todo_tasks:  # Has TODO tasks
                project_suggestions.append("💡 No tasks in progress - suggest starting next priority task")

        # Check if tasks are piling up (more than 5 TODO tasks)
        if todo_tasks.count("Task #") > 5:
            project_suggestions.append("📋 Multiple TODO tasks - suggest batch assignment to Dev Agents")

        if project_suggestions:
            suggestions.append(f"\n**{project.name}** (Priority: {project.priority}):")
            for suggestion in project_suggestions:
                suggestions.append(f"  • {suggestion}")

    if not suggestions:
        return "✅ All projects on track! No urgent actions needed."

    result = "🎯 **Proactive Suggestions:**\n"
    result += "\n".join(suggestions)
    result += "\n\nShall I take action on any of these, Master?"

    return result


def batch_assign_tasks(task_ids: list[int]) -> str:
    """
    Assign multiple tasks to Dev Agents in batch.

    Args:
        task_ids: List of task IDs to assign

    Returns:
        Batch assignment results
    """
    if not task_ids:
        return "❌ No task IDs provided"

    results = []
    successful = 0
    failed = 0

    for task_id in task_ids:
        try:
            result = auto_assign_task(task_id)

            if "✅" in result or "🎯" in result:
                successful += 1
                # Summarize instead of full output
                results.append(f"✅ Task #{task_id} assigned")
            else:
                failed += 1
                results.append(f"❌ Task #{task_id} failed: {result[:50]}")
        except Exception as e:
            failed += 1
            results.append(f"❌ Task #{task_id} error: {str(e)[:50]}")

    summary = f"📦 **Batch Assignment Complete**\n\n"
    summary += f"Success: {successful}/{len(task_ids)} tasks assigned\n"

    if failed > 0:
        summary += f"Failed: {failed}\n"

    summary += "\n**Details:**\n"
    summary += "\n".join(results)

    return summary
