"""Telegram command handlers"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from telegram import Update
from telegram.ext import ContextTypes

from src.agents.pm_agent import PMAgent
from src.core.cost_tracker import CostTracker
from src.core.database import get_session, get_project_by_name, get_active_projects


def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is authorized"""
    authorized_users = context.bot_data.get("authorized_users", [])

    # If no authorized users set, allow everyone (not recommended for production)
    if not authorized_users:
        return True

    user_id = update.effective_user.id
    return user_id in authorized_users


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if not is_authorized(update, context):
        await update.message.reply_text("Unauthorized. This bot is private.")
        return

    welcome_message = """My Devs AI Agent Team

Welcome! I'm your AI-powered project management assistant.

Available Commands:

Project Management:
/status <project> - Get project status
/tasks <project> - List all tasks
/create <project> <title> - Create new task
/warnings <project> - Show warnings
/projects - List all projects

Cost Tracking:
/costs - View today's API costs

Help:
/help - Show this message

Example Usage:
/projects
/status Example Project
/tasks Yohga - init
/create "Veggies list" Setup database

Let's manage your projects!
"""
    await update.message.reply_text(welcome_message)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    if not is_authorized(update, context):
        await update.message.reply_text("Unauthorized")
        return

    await start_handler(update, context)


async def projects_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /projects command"""
    if not is_authorized(update, context):
        await update.message.reply_text("Unauthorized")
        return

    await update.message.reply_text("Loading projects...")

    try:
        session = get_session()
        projects = get_active_projects(session)
        session.close()

        if not projects:
            await update.message.reply_text("No active projects found.")
            return

        message_lines = ["Active Projects:\n"]
        for project in projects:
            message_lines.append(f"- {project.name} (Priority: {project.priority})")

        message = "\n".join(message_lines)
        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    if not is_authorized(update, context):
        await update.message.reply_text("Unauthorized")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /status <project name>\n\nExample:\n/status Example Project"
        )
        return

    project_name = " ".join(context.args)

    await update.message.reply_text(f"Getting status for {project_name}...")

    try:
        pm_agent = PMAgent()
        result = pm_agent.get_status(project_name)

        response = f"Status: {project_name}\n\n{result}"
        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def tasks_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tasks command"""
    if not is_authorized(update, context):
        await update.message.reply_text("Unauthorized")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /tasks <project name>\n\nExample:\n/tasks Example Project"
        )
        return

    project_name = " ".join(context.args)

    await update.message.reply_text(f"Loading tasks for {project_name}...")

    try:
        from src.core.database import get_tasks_by_project

        session = get_session()
        project = get_project_by_name(session, project_name)

        if not project:
            await update.message.reply_text(f"Project '{project_name}' not found")
            session.close()
            return

        tasks = get_tasks_by_project(session, project.id)
        session.close()

        if not tasks:
            await update.message.reply_text(f"No tasks found for {project_name}")
            return

        message_lines = [f"Tasks: {project_name}\n"]

        status_emoji = {
            "todo": "[TODO]",
            "in_progress": "[IN PROGRESS]",
            "blocked": "[BLOCKED]",
            "review": "[REVIEW]",
            "done": "[DONE]"
        }

        for task in tasks[:15]:
            emoji = status_emoji.get(task.status, "")
            priority_mark = " [!]" if task.priority in ["critical", "high"] else ""
            message_lines.append(
                f"{emoji} #{task.id} {task.title}{priority_mark}"
            )

        if len(tasks) > 15:
            message_lines.append(f"\n... and {len(tasks) - 15} more tasks")

        message = "\n".join(message_lines)
        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def create_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /create command"""
    if not is_authorized(update, context):
        await update.message.reply_text("Unauthorized")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            'Usage: /create <project> <task title>\n\nExample:\n/create "Example Project" Setup development environment'
        )
        return

    args_text = " ".join(context.args)

    if args_text.startswith('"'):
        closing_quote = args_text.find('"', 1)
        if closing_quote == -1:
            await update.message.reply_text("Unclosed quote in project name")
            return

        project_name = args_text[1:closing_quote]
        task_title = args_text[closing_quote + 1:].strip()
    else:
        parts = args_text.split(maxsplit=1)
        if len(parts) < 2:
            await update.message.reply_text("Please provide both project name and task title")
            return
        project_name, task_title = parts

    await update.message.reply_text(f"Creating task in {project_name}...")

    try:
        pm_agent = PMAgent()
        result = pm_agent.create_task(project_name, task_title)

        await update.message.reply_text(f"Success: {result}")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def warnings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /warnings command"""
    if not is_authorized(update, context):
        await update.message.reply_text("Unauthorized")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /warnings <project name>\n\nExample:\n/warnings Example Project"
        )
        return

    project_name = " ".join(context.args)

    await update.message.reply_text(f"Checking warnings for {project_name}...")

    try:
        pm_agent = PMAgent()
        result = pm_agent.get_warnings(project_name)

        response = f"Warnings: {project_name}\n\n{result}"
        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def costs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /costs command"""
    if not is_authorized(update, context):
        await update.message.reply_text("Unauthorized")
        return

    await update.message.reply_text("Loading cost information...")

    try:
        cost_tracker = CostTracker()
        summary = cost_tracker.get_daily_summary()

        if not summary or summary.get("total_cost_usd", 0) == 0:
            await update.message.reply_text("No costs recorded today.")
            return

        message_lines = [
            "Today's Costs\n",
            f"Total Calls: {summary.get('total_calls', 0)}",
            f"Total Tokens: {summary.get('total_tokens', 0):,}",
            f"Total Cost: ${summary.get('total_cost_usd', 0):.4f}",
        ]

        by_agent = summary.get("by_agent", {})
        if by_agent:
            message_lines.append("\nBy Agent:")
            for agent, stats in by_agent.items():
                message_lines.append(f"- {agent}: ${stats.get('cost_usd', 0):.4f}")

        budget_status = summary.get("budget_status", {})
        if budget_status:
            daily_limit = budget_status.get("daily_limit", 1.0)
            daily_used = budget_status.get("daily_used", 0)
            percent = (daily_used / daily_limit * 100) if daily_limit > 0 else 0

            message_lines.append(f"\nBudget: {percent:.1f}% of ${daily_limit:.2f}")

        message = "\n".join(message_lines)
        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
