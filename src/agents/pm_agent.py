"""PM Agent - Project Manager for task management and status updates"""

import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

from openai import OpenAI

from src.agents.base_agent import BaseAgent
from src.agents.tools.task_tools import (
    create_task_tool,
    get_tasks_tool,
    get_task_details_tool,
)
from src.agents.tools.query_tools import (
    get_project_summary_tool,
    get_project_warnings_tool,
    get_blocked_tasks_tool,
)
from src.core.database import get_session, get_project_by_name

load_dotenv()


class PMAgent(BaseAgent):
    """Project Manager Agent - handles task management and reporting"""

    def __init__(self):
        super().__init__("pm_agent")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_status(self, project_name: str) -> str:
        """
        Generate status update for a project

        Args:
            project_name: Name of the project

        Returns:
            Status update text
        """
        # Validate project exists
        session = get_session()
        project = get_project_by_name(session, project_name)
        session.close()

        if not project:
            return f"Error: Project '{project_name}' not found"

        # Gather context
        summary = get_project_summary_tool(project_name)
        warnings = get_project_warnings_tool(project_name)
        blocked = get_blocked_tasks_tool(project_name)

        # Build prompt
        prompt = f"""You are a Project Manager providing a status update.

Project: {project_name}

Current Status:
{summary}

Warnings:
{warnings}

Blocked Tasks:
{blocked}

Provide a concise status update (max 150 words) including:
1. Overall progress summary
2. Critical issues/blockers (if any)
3. Top 3 next actions

Use bullet points. Be direct and actionable."""

        # Call OpenAI
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a {self.role}. {self.backstory}",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            status_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Calculate cost
            cost_details = self.cost_tracker.calculate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                self.model,
            )

            # Log to cost tracker
            self.cost_tracker.log_api_call(
                agent=self.agent_name,
                project=project_name,
                model=self.model,
                tokens_input=response.usage.prompt_tokens,
                tokens_output=response.usage.completion_tokens,
                command="status",
                response_summary=status_text[:100],
            )

            # Log interaction
            self.log_interaction(
                project_name,
                f"Get status for {project_name}",
                status_text,
                tokens_used,
                cost_details["total_cost_usd"],
            )

            return status_text

        except Exception as e:
            return f"Error generating status: {str(e)}"

    def create_task(
        self,
        project_name: str,
        task_title: str,
        description: str = "",
        priority: str = "medium",
    ) -> str:
        """
        Create a new task

        Args:
            project_name: Name of the project
            task_title: Task title
            description: Task description
            priority: Priority level

        Returns:
            Success or error message
        """
        result = create_task_tool(
            project_name=project_name,
            title=task_title,
            description=description,
            priority=priority,
        )

        # Log interaction (no OpenAI call for simple CRUD)
        self.context_manager.save_interaction(
            self.agent_name,
            project_name,
            {
                "timestamp": datetime.now().isoformat(),
                "role": "user",
                "content": f"Create task: {task_title}",
                "tokens": 0,
            },
        )

        self.context_manager.save_interaction(
            self.agent_name,
            project_name,
            {
                "timestamp": datetime.now().isoformat(),
                "role": "assistant",
                "content": result,
                "tokens": 0,
                "cost_usd": 0.0,
            },
        )

        return result

    def list_tasks(
        self, project_name: str, status: Optional[str] = None
    ) -> str:
        """
        List tasks for a project

        Args:
            project_name: Name of the project
            status: Filter by status (optional)

        Returns:
            Formatted task list
        """
        result = get_tasks_tool(project_name=project_name, status=status)

        # Log interaction
        self.context_manager.save_interaction(
            self.agent_name,
            project_name,
            {
                "timestamp": datetime.now().isoformat(),
                "role": "user",
                "content": f"List tasks (status={status})",
                "tokens": 0,
            },
        )

        return result

    def get_warnings(self, project_name: str) -> str:
        """
        Get warnings for a project

        Args:
            project_name: Name of the project

        Returns:
            Warnings text
        """
        return get_project_warnings_tool(project_name)

    def generate_report(self, project_name: str, report_type: str = "daily") -> str:
        """
        Generate a report for a project

        Args:
            project_name: Name of the project
            report_type: Type of report (daily, weekly, monthly)

        Returns:
            Report text
        """
        # For Milestone 1, use simple status
        # Can be enhanced in Milestone 3
        return self.get_status(project_name)
