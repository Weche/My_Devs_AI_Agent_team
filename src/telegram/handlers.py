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


def parse_project_name(args_text: str) -> str:
    """Parse project name from command arguments, removing quotes if present"""
    # Remove leading/trailing whitespace
    args_text = args_text.strip()

    # Remove quotes if present
    if args_text.startswith('"') and args_text.endswith('"'):
        return args_text[1:-1]
    elif args_text.startswith("'") and args_text.endswith("'"):
        return args_text[1:-1]

    return args_text


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if not is_authorized(update, context):
        await update.message.reply_text("Unauthorized. This bot is private.")
        return

    welcome_message = """My Devs AI Agent Team - Albedo

Greetings, Master! I am Albedo, your devoted Project Manager assistant.

I am here to serve you with utmost dedication. I can help manage your projects through commands or natural conversation.

Available Commands:

Project Management:
/projects - List all your projects
/status <project> - Get PM status update
/tasks <project> - List all tasks
/create <project> <title> - Create new task
/warnings <project> - Show warnings
/execute <task_id> - Assign task to Dev Agent

Cost Tracking:
/costs - View today's API costs

Help:
/help - Show this message

Natural Conversation:
Simply chat with me! I can:
- Create tasks with due dates
- Check project status
- List tasks and warnings
- Remember our conversation
- Execute actions through your words

Example Usage:
/projects
/status Example Project
"What's the status of Yohga?"
"Create a task for Veggies list: Build inventory API, due Friday"
"My name is Christian"

I eagerly await your command, Master!
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
            "Usage: /status <project name>\n\nExample:\n/status Example Project\n/status Yohga - init"
        )
        return

    # Parse project name and remove quotes
    project_name = parse_project_name(" ".join(context.args))

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
            "Usage: /tasks <project name>\n\nExample:\n/tasks Example Project\n/tasks Yohga - init"
        )
        return

    # Parse project name and remove quotes
    project_name = parse_project_name(" ".join(context.args))

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

    if not context.args:
        await update.message.reply_text(
            'Usage: /create <project> <task title>\n\nExamples:\n/create "Yohga - init" Define requirements\n/create "Example Project" Fix bug'
        )
        return

    args_text = " ".join(context.args)

    # Try to parse quoted project name first
    if args_text.startswith('"'):
        closing_quote = args_text.find('"', 1)
        if closing_quote == -1:
            await update.message.reply_text("Unclosed quote in project name")
            return

        project_name = args_text[1:closing_quote]
        task_title = args_text[closing_quote + 1:].strip()
    elif args_text.startswith("'"):
        closing_quote = args_text.find("'", 1)
        if closing_quote == -1:
            await update.message.reply_text("Unclosed quote in project name")
            return

        project_name = args_text[1:closing_quote]
        task_title = args_text[closing_quote + 1:].strip()
    else:
        # No quotes - split on first space
        parts = args_text.split(maxsplit=1)
        if len(parts) < 2:
            await update.message.reply_text("Please provide both project name and task title")
            return
        project_name, task_title = parts

    # Validate task title is not empty
    if not task_title or task_title.strip() == "":
        await update.message.reply_text(
            f"Error: Task title cannot be empty!\n\nUsage:\n/create \"{project_name}\" <task title>"
        )
        return

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
            "Usage: /warnings <project name>\n\nExample:\n/warnings Example Project\n/warnings Yohga - init"
        )
        return

    # Parse project name and remove quotes
    project_name = parse_project_name(" ".join(context.args))

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


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle natural language messages (non-commands) with Albedo"""
    if not is_authorized(update, context):
        await update.message.reply_text("Unauthorized")
        return

    user_message = update.message.text
    await update.message.chat.send_action("typing")

    try:
        # Get or initialize conversation history for this user
        if 'conversation_history' not in context.user_data:
            context.user_data['conversation_history'] = []

        # Get user's name if stored
        user_name = context.user_data.get('user_name', 'Master')

        # Check if user is telling us their name
        if "my name is" in user_message.lower():
            # Extract name (simple parsing)
            name_parts = user_message.lower().split("my name is")
            if len(name_parts) > 1:
                extracted_name = name_parts[1].strip().split()[0].capitalize()
                context.user_data['user_name'] = extracted_name
                user_name = extracted_name

        pm_agent = PMAgent()
        response = pm_agent.chat(
            user_message,
            conversation_history=context.user_data['conversation_history'],
            user_name=user_name
        )

        # Update conversation history (keep last 10 messages)
        context.user_data['conversation_history'].append({
            "role": "user",
            "content": user_message
        })
        context.user_data['conversation_history'].append({
            "role": "assistant",
            "content": response
        })

        # Keep only last 10 messages (5 exchanges) to manage token usage
        if len(context.user_data['conversation_history']) > 10:
            context.user_data['conversation_history'] = context.user_data['conversation_history'][-10:]

        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(
            f"My sincerest apologies, Master... I encountered an error: {str(e)}\n\n"
            "Try using commands like:\n"
            "/projects - List projects\n"
            "/status <project> - Get status\n"
            "/help - Show all commands"
        )


async def execute_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /execute command - Assign task to Dev Agent"""
    if not is_authorized(update, context):
        await update.message.reply_text("Unauthorized")
        return

    if not context.args or len(context.args) == 0:
        await update.message.reply_text(
            "Usage: /execute <task_id>\n\n"
            "Example: /execute 9\n\n"
            "This command assigns a task to the Dev Agent for code execution."
        )
        return

    try:
        task_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Error: Task ID must be a number")
        return

    await update.message.reply_text(f"🤖 Assigning Task #{task_id} to Dev Agent...\n\nThis may take a few minutes.")

    try:
        import requests

        # Call Dev Agent Service
        dev_agent_url = "http://localhost:3001/execute-task"

        response = requests.post(
            dev_agent_url,
            json={"task_id": task_id},
            timeout=300  # 5 minute timeout
        )

        result = response.json()

        if result.get("success"):
            message_lines = [
                f"✅ Dev Agent completed Task #{task_id}!\n",
                result.get("message", "Task executed successfully"),
            ]

            files_created = result.get("files_created", [])
            if files_created:
                message_lines.append(f"\n📁 Files created:")
                for file in files_created:
                    message_lines.append(f"  • {file}")

            await update.message.reply_text("\n".join(message_lines))
        else:
            error_msg = result.get("error", "Unknown error")
            await update.message.reply_text(
                f"❌ Dev Agent failed to execute Task #{task_id}\n\n"
                f"Error: {error_msg}"
            )

    except requests.exceptions.ConnectionError:
        await update.message.reply_text(
            "⚠️ Cannot connect to Dev Agent Service\n\n"
            "Please ensure the service is running:\n"
            "cd dev-agent-service\n"
            "npm run dev"
        )
    except requests.exceptions.Timeout:
        await update.message.reply_text(
            f"⏱ Task #{task_id} is taking longer than expected\n\n"
            "Dev Agent is still working on it. Check status later with /tasks"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
