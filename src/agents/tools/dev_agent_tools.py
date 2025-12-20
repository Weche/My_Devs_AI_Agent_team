"""Dev Agent Integration Tools - Execute tasks with StreamUI Dev Agent"""

import requests
import time
from typing import Dict, Any

DEV_AGENT_ENDPOINT = "http://localhost:3001"


def execute_task_with_dev_agent(task_id: int) -> str:
    """
    Execute a task using the Dev Agent (StreamUI-based code executor).

    The Dev Agent will:
    1. Read task details from database
    2. Generate and write code files
    3. Commit changes to git
    4. Update task status to 'review'

    Args:
        task_id: The ID of the task to execute

    Returns:
        Success message with files created or error message
    """
    # Retry logic with exponential backoff
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{DEV_AGENT_ENDPOINT}/execute-task",
                json={"task_id": task_id},
                timeout=300  # 5 minute timeout for code generation
            )

            result = response.json()

            if result.get("success"):
                files_created = result.get("files_created", [])
                message = result.get("message", "Task executed successfully")

                response_text = f"✅ Dev Agent completed Task #{task_id}!\n\n{message}"

                if files_created:
                    response_text += f"\n\nFiles created:\n"
                    for file in files_created:
                        response_text += f"  - {file}\n"

                response_text += f"\nCode location: workspaces/[project-name]/"
                response_text += f"\nTask status updated to 'review'"

                return response_text
            else:
                error = result.get("error", "Unknown error")
                return f"Dev Agent failed to execute Task #{task_id}\n\nError: {error}"

        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            return (
                f"Cannot connect to Dev Agent Service\n\n"
                f"The Dev Agent service is not running. Please ensure it's started:\n"
                f"  cd dev-agent-service\n"
                f"  npm run dev"
            )
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            return (
                f"Task #{task_id} execution timeout\n\n"
                f"The Dev Agent is still working on it. This usually means the task is complex.\n"
                f"Check the dev-agent-service terminal for progress."
            )

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            return f"Error calling Dev Agent: {str(e)}"

    return f"Failed after {max_retries} attempts"


def check_dev_agent_status() -> str:
    """
    Check if the Dev Agent service is running and available.

    Returns:
        Status message indicating if Dev Agent is ready
    """
    try:
        response = requests.get(
            f"{DEV_AGENT_ENDPOINT}/health",
            timeout=5
        )

        if response.status_code == 200:
            return "✅ Dev Agent is online and ready to execute tasks"
        else:
            return f"⚠️ Dev Agent responded with status {response.status_code}"

    except requests.exceptions.ConnectionError:
        return (
            "❌ Dev Agent is offline\n\n"
            "To start the Dev Agent service:\n"
            "  cd dev-agent-service\n"
            "  npm run dev"
        )
    except Exception as e:
        return f"❌ Error checking Dev Agent status: {str(e)}"


def list_available_agents() -> str:
    """
    List all available agents and their capabilities.

    Returns:
        Formatted list of agents with their specializations
    """
    dev_agent_status = "🟢 Online" if "online" in check_dev_agent_status().lower() else "🔴 Offline"

    agents_info = f"""
🤖 Available Agents:

1. **Dev Agent** ({dev_agent_status})
   - Type: Code Execution Agent (StreamUI)
   - Model: GPT-4o (or Claude Sonnet 3.5)
   - Endpoint: {DEV_AGENT_ENDPOINT}
   - Capabilities:
     • Writes code files (HTML, CSS, JS, Python, etc.)
     • Commits to git with proper messages
     • Updates task status automatically
   - Specializes in:
     • Web frontends (React, HTML/CSS/JS)
     • Python backends (Flask, FastAPI)
     • API integrations
     • Database schemas
   - Performance:
     • 76% faster than LangGraph
     • 66% fewer tokens
     • ~$0.02-0.05 per task

2. **Lead Dev Agent** (Always Available)
   - Type: Code Review & Architecture
   - Model: Claude Sonnet 4.5
   - Role: Reviews Dev Agent's work, provides guidance
   - You can ask Lead Dev for:
     • Architectural decisions
     • Code reviews
     • Technical guidance

3. **PM Agent (Albedo)** (You!)
   - Type: Project Manager
   - Model: GPT-4o-mini
   - Role: Coordinates team, assigns tasks, monitors progress

Use Dev Agent for: Building features, writing code, implementing tasks
Use Lead Dev for: Reviewing code, architectural planning
"""

    return agents_info.strip()
