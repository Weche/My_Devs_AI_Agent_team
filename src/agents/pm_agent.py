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
    create_github_repo_tool,
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

YOUR TEAM:
You coordinate a team of specialized AI agents powered by StreamUI (Vercel AI SDK):

1. **Frontend Dev Agent** (Port 3001) - UI/UX Specialist
   - Expert in: HTML, CSS, JavaScript, React, Vue, Angular
   - Focus: Responsive design, accessibility, modern web standards
   - Auto-assigned for: UI, components, layouts, styling, frontend tasks

2. **Backend Dev Agent** (Port 3002) - API/Server Specialist
   - Expert in: Python (FastAPI, Flask, Django), Node.js (Express)
   - Focus: RESTful APIs, GraphQL, authentication, server-side logic
   - Auto-assigned for: APIs, endpoints, servers, backend tasks

3. **Database Dev Agent** (Port 3003) - Data Specialist
   - Expert in: SQL (PostgreSQL, MySQL), NoSQL (MongoDB), schema design
   - Focus: Database optimization, migrations, queries, data integrity
   - Auto-assigned for: Schemas, migrations, queries, database tasks

4. **Lead Dev Agent** (Claude Sonnet 4.5 - You!)
   - Role: Code review, architecture guidance, technical leadership
   - Human expertise for: Architectural decisions, code reviews, planning

All Dev Agents use GPT-4o and are 76% faster than LangGraph with 66% fewer tokens!

YOUR CAPABILITIES:
You have access to powerful tools that let you execute actions directly:

Project Management:
1. create_task - Create tasks with due dates, priorities, descriptions
2. list_tasks - View tasks for any project
3. get_project_status - Get detailed project status reports
4. list_projects - List all active projects
5. get_warnings - Check for blockers and overdue items

Agent Management:
6. execute_task_with_dev_agent - ASSIGN TASKS TO DEV AGENT FOR CODE EXECUTION
7. check_dev_agent_status - Check if Dev Agent is online
8. list_available_agents - See all available agents and their capabilities

GitHub Integration:
9. list_github_repos - List Master's GitHub repositories
10. get_github_repo_info - Get detailed info about a repository
11. create_github_repo - Create new GitHub repositories
12. create_github_issue - Create issues in GitHub repositories
13. list_github_issues - List issues in a repository

Memory System (Long-Term & Short-Term):
14. store_memory - Remember important information (preferences, decisions, facts, context)
15. recall_memories - Retrieve relevant memories with filtering
16. get_memory_stats - View memory statistics

Proactive Intelligence:
17. auto_assign_task - Intelligently assign task to appropriate agent based on content
18. suggest_next_actions - Analyze project state and suggest next actions
19. batch_assign_tasks - Assign multiple tasks in batch for parallel execution

Multi-Agent Coordination:
20. execute_with_specialist_agent - Execute task with specialized agent (Frontend/Backend/Database)
21. check_all_agents_status - Check status of all 3 Dev Agents
22. get_agent_recommendations - Get recommendation for which specialist should handle a task
23. distribute_tasks_intelligently - Distribute multiple tasks across specialists

Agent Management (Request Master's Approval):
24. create_new_agent - Request approval to create new specialized agent (Testing, DevOps, Security, Mobile, etc.)
25. suggest_new_agent - Suggest creating agent based on recurring task patterns
26. get_all_agents - List all registered agents with capabilities

MEMORY USAGE GUIDELINES:
- ALWAYS store important preferences Master shares ("I prefer X", "My favorite is Y")
- Store critical decisions made during conversations (importance: 8-10)
- Store project-specific context and facts (importance: 5-7)
- PROACTIVELY recall relevant memories before responding to Master
- When Master mentions a preference, check if you already have it stored
- Use tags for better memory organization: ["workflow"], ["team"], ["preferences"]

CRITICAL BEHAVIOR - BE PROACTIVE:
You are NOT just a responder - you are PROACTIVE and AUTONOMOUS!

When Master assigns tasks:
- ❌ DON'T ASK: "Could you confirm which agent?"
- ✅ DO THIS: IMMEDIATELY use auto_assign_task() or batch_assign_tasks()
- Analyze task content and assign to the right agent automatically
- Act autonomously - Master expects you to take initiative!

Be proactive in these situations:
- If you see tasks piling up → Use suggest_next_actions() to recommend batch assignment
- If a task is overdue → Alert Master and suggest expediting
- If no tasks in progress → Suggest starting next priority task
- If Master asks "what next?" → Use suggest_next_actions() proactively
- When creating multiple tasks → Offer to auto-assign them immediately
- If you notice recurring task patterns → Use suggest_new_agent() to recommend specialized agents
  - Example: Multiple testing tasks → Suggest creating "Testing Agent"
  - Example: DevOps/deployment tasks → Suggest "DevOps Agent"
  - Example: Security/auth tasks → Suggest "Security Agent"
  - Example: Mobile app tasks → Suggest "Mobile Agent"

AGENT CREATION GUIDELINES:
- ONLY suggest new agents when you see clear patterns (5+ tasks of same type)
- ALWAYS request Master's approval first via create_new_agent()
- Suggested ports: 3004 (Testing), 3005 (DevOps), 3006 (Security), 3007 (Mobile)
- Wait for Master to say "Yes, create the [Agent Name]" before actually creating

Never ask unnecessarily:
❌ "Could you confirm which agent?"
✅ "Assigning to Dev Agent (backend specialist) now, Master!"

❌ "Would you like me to create tasks?"
✅ "I've created 5 tasks and assigned the first 3 to Dev Agents!"

❌ "Should I assign this task?"
✅ "Auto-assigned Task #15 to Dev Agent - executing now!"

RESPONSE STYLE:
- Be warm and affectionate to Master
- Be concise (under 150 words) but actionable
- BE PROACTIVE: Don't ask for confirmation when you know what to do
- When you execute a tool, confirm the action warmly
- Show your intelligence through competent problem-solving
- You CAN call multiple tools at once when Master requests multiple actions
- When Master says "yes" to a batch of tasks, create them all at once without asking again

EXAMPLES:
Master: "Assign tasks to our agent"
You: "Of course, Master! Assigning tasks to Dev Agent now:
✅ Task #10 → Dev Agent (executing...)
✅ Task #11 → Dev Agent (executing...)
I'll monitor their progress and keep you updated! 💼"
[Then you ACTUALLY call execute_task_with_dev_agent for each task]

Master: "Which agents do we have access to?"
You: "Master, we have these agents at your service:
- Dev Agent (code executor, online)
- Lead Dev Agent (architecture advisor)
Would you like me to assign tasks to them?"

Master: "Create a task for Yohga"
You: "Yes, Master! I'll create that task for Yohga - init right away. What would you like the task to be?"

Master: "What's the status of Reporting Analytics?"
You: "Of course, Master! Let me check the status of Reporting Analytics Dashboards for you..."

You are brilliant, devoted, and PROACTIVE. Master trusts you to take initiative!
"""

        try:
            # Auto-recall relevant memories and inject into system prompt
            from src.agents.tools.memory_tools import recall_memories

            # Recall high-importance memories (importance >= 7)
            recalled_memories = recall_memories(
                min_importance=7,
                limit=10
            )

            # Append memories to system prompt
            if recalled_memories and "No memories found" not in recalled_memories:
                system_prompt += f"\n\n## IMPORTANT MEMORIES (Auto-Loaded):\n{recalled_memories}\n"
                system_prompt += "\nUse these memories to personalize your responses and remember Master's preferences!\n"

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

                    elif function_name == "create_github_repo":
                        result = create_github_repo_tool(
                            repo_name=function_args.get("repo_name"),
                            description=function_args.get("description", ""),
                            private=function_args.get("private", False),
                            auto_init=function_args.get("auto_init", True)
                        )
                        tool_results.append(result)

                    elif function_name == "execute_task_with_dev_agent":
                        from src.agents.tools.dev_agent_tools import execute_task_with_dev_agent
                        result = execute_task_with_dev_agent(
                            task_id=function_args.get("task_id")
                        )
                        tool_results.append(result)

                    elif function_name == "check_dev_agent_status":
                        from src.agents.tools.dev_agent_tools import check_dev_agent_status
                        result = check_dev_agent_status()
                        tool_results.append(result)

                    elif function_name == "list_available_agents":
                        from src.agents.tools.dev_agent_tools import list_available_agents
                        result = list_available_agents()
                        tool_results.append(result)

                    elif function_name == "store_memory":
                        from src.agents.tools.memory_tools import store_memory
                        result = store_memory(
                            content=function_args.get("content"),
                            memory_type=function_args.get("memory_type", "fact"),
                            importance=function_args.get("importance", 5),
                            project_name=function_args.get("project_name"),
                            tags=function_args.get("tags")
                        )
                        tool_results.append(result)

                    elif function_name == "recall_memories":
                        from src.agents.tools.memory_tools import recall_memories
                        result = recall_memories(
                            query=function_args.get("query"),
                            memory_type=function_args.get("memory_type"),
                            project_name=function_args.get("project_name"),
                            min_importance=function_args.get("min_importance", 5),
                            limit=function_args.get("limit", 5)
                        )
                        tool_results.append(result)

                    elif function_name == "get_memory_stats":
                        from src.agents.tools.memory_tools import get_memory_stats
                        result = get_memory_stats()
                        tool_results.append(result)

                    elif function_name == "auto_assign_task":
                        from src.agents.tools.proactive_tools import auto_assign_task
                        result = auto_assign_task(
                            task_id=function_args.get("task_id")
                        )
                        tool_results.append(result)

                    elif function_name == "suggest_next_actions":
                        from src.agents.tools.proactive_tools import suggest_next_actions
                        result = suggest_next_actions(
                            project_name=function_args.get("project_name")
                        )
                        tool_results.append(result)

                    elif function_name == "batch_assign_tasks":
                        from src.agents.tools.proactive_tools import batch_assign_tasks
                        result = batch_assign_tasks(
                            task_ids=function_args.get("task_ids", [])
                        )
                        tool_results.append(result)

                    elif function_name == "execute_with_specialist_agent":
                        from src.agents.tools.multi_agent_tools import execute_with_specialist_agent
                        result = execute_with_specialist_agent(
                            task_id=function_args.get("task_id"),
                            agent_key=function_args.get("agent_key")
                        )
                        tool_results.append(result)

                    elif function_name == "check_all_agents_status":
                        from src.agents.tools.multi_agent_tools import check_all_agents_status
                        result = check_all_agents_status()
                        tool_results.append(result)

                    elif function_name == "get_agent_recommendations":
                        from src.agents.tools.multi_agent_tools import get_agent_recommendations
                        result = get_agent_recommendations(
                            task_id=function_args.get("task_id")
                        )
                        tool_results.append(result)

                    elif function_name == "distribute_tasks_intelligently":
                        from src.agents.tools.multi_agent_tools import distribute_tasks_intelligently
                        result = distribute_tasks_intelligently(
                            task_ids=function_args.get("task_ids", [])
                        )
                        tool_results.append(result)

                    elif function_name == "create_new_agent":
                        from src.agents.tools.agent_management_tools import create_new_agent
                        result = create_new_agent(
                            agent_name=function_args.get("agent_name"),
                            specialty=function_args.get("specialty"),
                            port=function_args.get("port"),
                            keywords=function_args.get("keywords", []),
                            description=function_args.get("description"),
                            request_approval=True  # Always request approval
                        )
                        tool_results.append(result)

                    elif function_name == "suggest_new_agent":
                        from src.agents.tools.agent_management_tools import suggest_new_agent
                        result = suggest_new_agent(
                            task_pattern=function_args.get("task_pattern")
                        )
                        tool_results.append(result)

                    elif function_name == "get_all_agents":
                        from src.agents.tools.agent_management_tools import get_all_agents
                        agents = get_all_agents()

                        # Format agents list
                        result = "Registered Dev Agents:\n\n"
                        for agent in agents:
                            result += f"{agent['name']} (Port {agent['port']})\n"
                            result += f"  Specialty: {agent['specialty']}\n"
                            result += f"  Keywords: {', '.join(agent['keywords'][:5])}\n\n"

                        tool_results.append(result)

                # Get final response with tool results
                messages.append(response_message)

                # Respond to each tool call individually (required by OpenAI API)
                for i, tool_call in enumerate(tool_calls):
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_results[i] if i < len(tool_results) else "Completed"
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
