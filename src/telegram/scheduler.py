"""Scheduler for proactive updates and notifications"""

import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from telegram.ext import ContextTypes

from src.agents.pm_agent import PMAgent
from src.core.database import get_session, get_active_projects, get_tasks_by_project
from src.core.github_tracker import GitHubTracker

load_dotenv()


class AlbedoScheduler:
    """Handles scheduled tasks and proactive updates"""

    def __init__(self, bot: Bot, authorized_user_id: int):
        """
        Initialize the scheduler

        Args:
            bot: Telegram Bot instance
            authorized_user_id: Chat ID to send updates to
        """
        self.bot = bot
        self.authorized_user_id = authorized_user_id
        self.scheduler = AsyncIOScheduler(timezone="America/Santiago")

    def start(self):
        """Start the scheduler"""
        # Daily standup at 9:00 AM Santiago time
        self.scheduler.add_job(
            self.send_daily_standup,
            CronTrigger(hour=9, minute=0, timezone="America/Santiago"),
            id="daily_standup",
            name="Daily Standup Update",
            replace_existing=True
        )

        # Check for due tasks every hour
        self.scheduler.add_job(
            self.check_due_tasks,
            CronTrigger(minute=0, timezone="America/Santiago"),
            id="check_due_tasks",
            name="Check Due Tasks",
            replace_existing=True
        )

        # Weekly project review on Monday at 9:00 AM
        self.scheduler.add_job(
            self.send_weekly_review,
            CronTrigger(day_of_week="mon", hour=9, minute=0, timezone="America/Santiago"),
            id="weekly_review",
            name="Weekly Project Review",
            replace_existing=True
        )

        # Check GitHub repos for updates every 30 minutes
        self.scheduler.add_job(
            self.check_github_updates,
            CronTrigger(minute="*/30", timezone="America/Santiago"),
            id="github_updates",
            name="Check GitHub Updates",
            replace_existing=True
        )

        # Proactive task monitoring - auto-assign high-priority tasks every 2 hours
        self.scheduler.add_job(
            self.proactive_task_monitoring,
            CronTrigger(hour="*/2", timezone="America/Santiago"),
            id="proactive_monitoring",
            name="Proactive Task Monitoring",
            replace_existing=True
        )

        # Suggest next actions twice daily (10 AM and 3 PM)
        self.scheduler.add_job(
            self.suggest_actions_periodically,
            CronTrigger(hour="10,15", minute=0, timezone="America/Santiago"),
            id="suggest_actions",
            name="Suggest Next Actions",
            replace_existing=True
        )

        self.scheduler.start()

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()

    async def send_daily_standup(self):
        """Send daily project status summary"""
        try:
            pm_agent = PMAgent()
            session = get_session()
            projects = get_active_projects(session)

            if not projects:
                session.close()
                return

            message_lines = ["Good morning, Master Christian! Here's your daily standup:\n"]

            # Check each project for important updates
            for project in projects:
                # Get tasks due today or overdue
                tasks = get_tasks_by_project(session, project.id)

                urgent_tasks = []
                for task in tasks:
                    if task.due_date and task.status not in ["done", "review"]:
                        days_until_due = (task.due_date - datetime.utcnow()).days

                        if days_until_due < 0:
                            urgent_tasks.append(f"⚠️ OVERDUE: Task #{task.id} - {task.title}")
                        elif days_until_due == 0:
                            urgent_tasks.append(f"⏰ DUE TODAY: Task #{task.id} - {task.title}")
                        elif days_until_due <= 2:
                            urgent_tasks.append(f"📅 Due in {days_until_due} days: Task #{task.id} - {task.title}")

                # Get warnings
                warnings = pm_agent.get_warnings(project.name)

                # Only include project if there are updates
                if urgent_tasks or "No warnings" not in warnings:
                    message_lines.append(f"\n{project.name} (Priority: {project.priority}):")

                    if urgent_tasks:
                        for task_info in urgent_tasks[:3]:  # Limit to 3 tasks per project
                            message_lines.append(f"  {task_info}")

                    if warnings and "No warnings" not in warnings:
                        message_lines.append(f"  {warnings}")

            session.close()

            # Only send if there are updates
            if len(message_lines) > 1:
                message_lines.append("\nHave a productive day, Master! 💼")
                message = "\n".join(message_lines)
                await self.bot.send_message(chat_id=self.authorized_user_id, text=message)
            else:
                # Send a simple good morning if no urgent items
                await self.bot.send_message(
                    chat_id=self.authorized_user_id,
                    text="Good morning, Master Christian! All projects are on track. No urgent tasks today. Have a wonderful day! ✨"
                )

        except Exception as e:
            # Log error but don't crash
            print(f"Error in daily standup: {str(e)}")

    async def check_due_tasks(self):
        """Check for tasks due in the next hour"""
        try:
            session = get_session()
            projects = get_active_projects(session)

            for project in projects:
                tasks = get_tasks_by_project(session, project.id)

                for task in tasks:
                    if task.due_date and task.status not in ["done", "review"]:
                        hours_until_due = (task.due_date - datetime.utcnow()).total_seconds() / 3600

                        # Alert if task is due in 1-2 hours
                        if 1 <= hours_until_due <= 2:
                            message = (
                                f"⏰ Reminder, Master!\n\n"
                                f"Task #{task.id} in {project.name} is due in about {int(hours_until_due)} hour(s):\n"
                                f"  {task.title}\n\n"
                                f"Priority: {task.priority}"
                            )
                            await self.bot.send_message(chat_id=self.authorized_user_id, text=message)

            session.close()

        except Exception as e:
            print(f"Error checking due tasks: {str(e)}")

    async def send_weekly_review(self):
        """Send weekly project review on Monday mornings"""
        try:
            pm_agent = PMAgent()
            session = get_session()
            projects = get_active_projects(session)

            if not projects:
                session.close()
                return

            message_lines = ["Good morning, Master Christian! Here's your weekly project review:\n"]

            for project in projects:
                # Get project status
                status = pm_agent.get_status(project.name)

                # Get task counts
                tasks = get_tasks_by_project(session, project.id)
                todo_count = sum(1 for t in tasks if t.status == "todo")
                in_progress_count = sum(1 for t in tasks if t.status == "in_progress")
                done_count = sum(1 for t in tasks if t.status == "done")

                message_lines.append(f"\n{project.name}:")
                message_lines.append(f"  Tasks: {done_count} done, {in_progress_count} in progress, {todo_count} todo")
                message_lines.append(f"  {status[:200]}")  # Truncate to keep message reasonable

            session.close()

            message_lines.append("\nLet's make this week count, Master! 💪")
            message = "\n".join(message_lines)

            await self.bot.send_message(chat_id=self.authorized_user_id, text=message)

        except Exception as e:
            print(f"Error in weekly review: {str(e)}")

    async def check_github_updates(self):
        """Check all GitHub repos for new commits and notify user"""
        try:
            tracker = GitHubTracker()
            repos = tracker.get_all_repos()

            for repo in repos:
                update = tracker.check_updates(repo)

                # If new commits detected
                if update and "error" not in update:
                    message = tracker.format_update_message(update)
                    await self.bot.send_message(
                        chat_id=self.authorized_user_id,
                        text=message
                    )

                    # If commit mentions task IDs, notify about them
                    if update.get("task_ids"):
                        task_info = f"\n\n💡 This commit mentions tasks: {', '.join(['#' + tid for tid in update['task_ids']])}"
                        await self.bot.send_message(
                            chat_id=self.authorized_user_id,
                            text=task_info
                        )

        except Exception as e:
            # Log error but don't crash scheduler
            print(f"Error checking GitHub updates: {str(e)}")

    async def proactive_task_monitoring(self):
        """Proactively check for idle/overdue tasks and auto-assign"""
        from src.agents.tools.proactive_tools import suggest_next_actions, auto_assign_task
        from src.agents.tools.query_tools import get_project_warnings_tool

        try:
            session = get_session()
            projects = get_active_projects(session)

            for project in projects:
                # Get warnings (overdue/blocked tasks)
                warnings = get_project_warnings_tool(project.name)

                # Get TODO tasks
                tasks = get_tasks_by_project(session, project.id, status="todo")

                # Auto-assign overdue or high-priority TODO tasks
                for task in tasks[:3]:  # Limit to top 3 tasks
                    if task.priority in ["high", "critical"]:
                        try:
                            result = auto_assign_task(task.id)
                            if "Auto-assigned" in result or "completed" in result.lower():
                                await self.bot.send_message(
                                    chat_id=self.authorized_user_id,
                                    text=f"Proactive Assignment:\n\n{result}"
                                )
                        except Exception as e:
                            print(f"Error auto-assigning task {task.id}: {str(e)}")

                # Alert on warnings
                if "Overdue" in warnings or "Blocked" in warnings:
                    await self.bot.send_message(
                        chat_id=self.authorized_user_id,
                        text=f"Project Alert: {project.name}\n\n{warnings}"
                    )

            session.close()

        except Exception as e:
            print(f"Error in proactive task monitoring: {str(e)}")

    async def suggest_actions_periodically(self):
        """Periodically suggest next actions"""
        from src.agents.tools.proactive_tools import suggest_next_actions

        try:
            suggestions = suggest_next_actions()

            # Only send if there are actionable suggestions
            if suggestions and "No urgent actions" not in suggestions:
                await self.bot.send_message(
                    chat_id=self.authorized_user_id,
                    text=f"Proactive Suggestions:\n\n{suggestions}"
                )

        except Exception as e:
            print(f"Error suggesting actions: {str(e)}")


def setup_scheduler(bot: Bot, authorized_user_id: int) -> AlbedoScheduler:
    """
    Setup and start the scheduler

    Args:
        bot: Telegram Bot instance
        authorized_user_id: Chat ID to send updates to

    Returns:
        AlbedoScheduler instance
    """
    scheduler = AlbedoScheduler(bot, authorized_user_id)
    scheduler.start()
    return scheduler
