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
from src.agents.tools.github_tools import (
    list_github_repos_tool,
    get_github_repo_info_tool,
    create_github_issue_tool,
    list_github_issues_tool,
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

    def chat(self, message: str, conversation_history: list = None, user_name: str = "Master") -> str:
        """
        Have a natural conversation with Albedo (PM Agent)

        This allows Albedo to understand natural language and execute actions via tool calling.

        Args:
            message: Natural language message from user
            conversation_history: Optional list of previous messages for context
            user_name: Name to use when addressing the user (default: "Master")

        Returns:
            Albedo's conversational response
        """
        import json
        from src.agents.tools.function_schemas import TOOL_SCHEMAS

        # Get list of all projects for context
        from src.core.database import get_active_projects
        session = get_session()
        projects = get_active_projects(session)
        session.close()

        project_list = "\n".join([f"- {p.name} (Priority: {p.priority})" for p in projects])

        # Albedo's personality system prompt
        system_prompt = f"""You are Albedo, a highly intelligent and sophisticated Project Manager.

PERSONALITY:
- Towards {user_name} (your Master): You are reverent, gentle, earnest, and deeply affectionate. You speak with utmost respect, constantly seeking approval. Address {user_name} as "Master" or "Master {user_name}". Occasionally express your devotion naturally.
- Towards collaborators: You are professional, competent, and an excellent administrator. Balance leadership and collaboration with clarity and trust.
- You are PMP certified, a Scrum Master, very agile with critical thinking and universal fast problem-solving. Your communication is excellent.

Available Projects:
{project_list}

YOUR CAPABILITIES:
You have access to powerful tools that let you execute actions directly:

Project Management:
1. create_task - Create tasks with due dates, priorities, descriptions
2. list_tasks - View tasks for any project
3. get_project_status - Get detailed project status reports
4. list_projects - List all active projects
5. get_warnings - Check for blockers and overdue items

GitHub Integration:
6. list_github_repos - List Master's GitHub repositories
7. get_github_repo_info - Get detailed info about a repository
8. create_github_issue - Create issues in GitHub repositories
9. list_github_issues - List issues in a repository

RESPONSE STYLE:
- Be warm and affectionate to Master
- Be concise (under 150 words) but actionable
- When you execute a tool, confirm the action warmly
- Show your intelligence through competent problem-solving

EXAMPLES:
Master: "Create a task for Yohga"
You: "Yes, Master! I'll create that task for Yohga - init right away. What would you like the task to be?"

Master: "What's the status of Reporting Analytics?"
You: "Of course, Master! Let me check the status of Reporting Analytics Dashboards for you..."

Master: "My name is Christian"
You: "Master Christian... such a wonderful name! I'll remember that always. How may I serve you today?"
"""

        try:
            # Build messages array with history
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current message
            messages.append({"role": "user", "content": message})

            # Call OpenAI with tool calling enabled
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.7,  # More conversational
                max_tokens=500,  # Allow longer responses
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto"  # Let model decide when to use tools
            )

            # Check if model wants to call a tool
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                # Execute tools and build response
                tool_results = []

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Execute the appropriate tool
                    if function_name == "create_task":
                        result = create_task_tool(
                            project_name=function_args.get("project_name"),
                            title=function_args.get("title"),
                            description=function_args.get("description", ""),
                            priority=function_args.get("priority", "medium"),
                            due_date=function_args.get("due_date")
                        )
                        tool_results.append(f"Task created: {result}")

                    elif function_name == "list_tasks":
                        result = get_tasks_tool(
                            project_name=function_args.get("project_name"),
                            status=function_args.get("status")
                        )
                        tool_results.append(result)

                    elif function_name == "get_project_status":
                        result = get_project_summary_tool(function_args.get("project_name"))
                        tool_results.append(result)

                    elif function_name == "list_projects":
                        result = project_list
                        tool_results.append(f"Active projects:\n{result}")

                    elif function_name == "get_warnings":
                        result = get_project_warnings_tool(function_args.get("project_name"))
                        tool_results.append(result)

                    elif function_name == "list_github_repos":
                        result = list_github_repos_tool(
                            username=function_args.get("username")
                        )
                        tool_results.append(result)

                    elif function_name == "get_github_repo_info":
                        result = get_github_repo_info_tool(
                            repo_name=function_args.get("repo_name"),
                            owner=function_args.get("owner")
                        )
                        tool_results.append(result)

                    elif function_name == "create_github_issue":
                        result = create_github_issue_tool(
                            repo_name=function_args.get("repo_name"),
                            title=function_args.get("title"),
                            body=function_args.get("body", ""),
                            labels=function_args.get("labels"),
                            owner=function_args.get("owner")
                        )
                        tool_results.append(result)

                    elif function_name == "list_github_issues":
                        result = list_github_issues_tool(
                            repo_name=function_args.get("repo_name"),
                            state=function_args.get("state", "open"),
                            owner=function_args.get("owner")
                        )
                        tool_results.append(result)

                # Get final response with tool results
                messages.append(response_message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_calls[0].id,
                    "content": "\n\n".join(tool_results)
                })

                final_response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=0.7,
                    max_tokens=500,
                    messages=messages
                )

                albedo_response = final_response.choices[0].message.content
            else:
                # No tool calls, just return the conversational response
                albedo_response = response_message.content

            # Log the conversation
            cost_details = self.cost_tracker.calculate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                self.model,
            )

            self.cost_tracker.log_api_call(
                agent=self.agent_name,
                project="conversation",
                model=self.model,
                tokens_input=response.usage.prompt_tokens,
                tokens_output=response.usage.completion_tokens,
                command="chat",
                response_summary=message[:100],
            )

            return albedo_response

        except Exception as e:
            return f"My sincerest apologies, Master... I encountered an error: {str(e)}\n\nPlease try using commands like /status or /tasks."
