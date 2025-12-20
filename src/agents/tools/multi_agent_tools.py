"""Multi-Agent Management - Intelligent routing to specialized Dev Agents"""

import requests
import time
from typing import Optional, Dict, List
from src.core.database import get_session, get_task_by_id


# Dev Agent endpoints
DEV_AGENTS = {
    "frontend": {
        "endpoint": "http://localhost:3001",
        "name": "Frontend Agent",
        "specialty": "HTML/CSS/JS/React/UI/UX",
        "keywords": [
            'frontend', 'ui', 'ux', 'html', 'css', 'javascript', 'typescript',
            'react', 'vue', 'angular', 'component', 'interface', 'layout',
            'styling', 'responsive', 'tailwind', 'scss', 'sass'
        ]
    },
    "backend": {
        "endpoint": "http://localhost:3002",
        "name": "Backend Agent",
        "specialty": "Python/Node.js/APIs/Server",
        "keywords": [
            'backend', 'api', 'server', 'endpoint', 'python', 'nodejs', 'express',
            'fastapi', 'flask', 'django', 'rest', 'graphql', 'microservice',
            'authentication', 'authorization', 'middleware'
        ]
    },
    "database": {
        "endpoint": "http://localhost:3003",
        "name": "Database Agent",
        "specialty": "SQL/PostgreSQL/MongoDB/Data",
        "keywords": [
            'database', 'sql', 'postgresql', 'mysql', 'mongodb', 'schema',
            'migration', 'query', 'orm', 'data', 'storage', 'sqlite', 'index'
        ]
    }
}


def detect_agent_specialty(task_title: str, task_description: str) -> str:
    """
    Detect which specialized agent should handle the task.

    Args:
        task_title: Task title
        task_description: Task description

    Returns:
        Agent key ('frontend', 'backend', 'database', or 'general')
    """
    combined = f"{task_title.lower()} {(task_description or '').lower()}"

    # Score each agent based on keyword matches
    scores = {}
    for agent_key, agent_info in DEV_AGENTS.items():
        score = sum(1 for keyword in agent_info['keywords'] if keyword in combined)
        scores[agent_key] = score

    # Return agent with highest score
    best_agent = max(scores, key=scores.get)
    best_score = scores[best_agent]

    # If no clear match, return 'general'
    if best_score == 0:
        return 'general'

    return best_agent


def execute_with_specialist_agent(task_id: int, agent_key: Optional[str] = None) -> str:
    """
    Execute task with appropriate specialist agent.

    Args:
        task_id: Task ID to execute
        agent_key: Optional specific agent ('frontend', 'backend', 'database')
                  If None, auto-detects based on task content

    Returns:
        Execution result message
    """
    session = get_session()
    task = get_task_by_id(session, task_id)
    session.close()

    if not task:
        return f"❌ Task #{task_id} not found"

    # Auto-detect agent if not specified
    if not agent_key:
        agent_key = detect_agent_specialty(task.title, task.description or "")

    # If general, use first available agent (round-robin)
    if agent_key == 'general':
        agent_key = 'frontend'  # Default to frontend for general tasks

    # Get agent info
    if agent_key not in DEV_AGENTS:
        return f"❌ Unknown agent: {agent_key}"

    agent_info = DEV_AGENTS[agent_key]
    endpoint = agent_info['endpoint']
    agent_name = agent_info['name']

    # Retry logic with exponential backoff
    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            # Execute task on specialist agent
            response = requests.post(
                f"{endpoint}/execute-task",
                json={"task_id": task_id},
                timeout=300  # 5 minute timeout
            )

            result = response.json()

            if result.get("success"):
                files_created = result.get("files_created", [])
                response_text = f"✅ {agent_name} completed Task #{task_id}!\n\n"
                response_text += f"Specialty: {agent_info['specialty']}\n\n"

                if files_created:
                    response_text += f"Files created:\n"
                    for file in files_created:
                        response_text += f"  - {file}\n"

                return response_text
            else:
                error = result.get("error", "Unknown error")
                return f"Error: {agent_name} failed: {error}"

        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            return f"Cannot connect to {agent_name} at {endpoint}\n" \
                   f"Make sure the agent is running: cd dev-agents/{agent_key}-agent && npm run dev"

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            return f"Timeout: {agent_name} timed out after 5 minutes"

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            return f"Error executing with {agent_name}: {str(e)}"

    return f"Failed after {max_retries} attempts"


def check_agent_status(agent_key: str) -> Dict:
    """
    Check if a specific agent is online.

    Args:
        agent_key: Agent key ('frontend', 'backend', 'database')

    Returns:
        Status dict with 'online' boolean and 'message' string
    """
    if agent_key not in DEV_AGENTS:
        return {"online": False, "message": f"Unknown agent: {agent_key}"}

    agent_info = DEV_AGENTS[agent_key]
    endpoint = agent_info['endpoint']
    agent_name = agent_info['name']

    try:
        response = requests.get(f"{endpoint}/health", timeout=2)
        if response.status_code == 200:
            return {
                "online": True,
                "message": f"✅ {agent_name} is online at {endpoint}"
            }
        else:
            return {
                "online": False,
                "message": f"⚠️ {agent_name} returned status {response.status_code}"
            }
    except requests.exceptions.ConnectionError:
        return {
            "online": False,
            "message": f"❌ {agent_name} is offline (no response at {endpoint})"
        }
    except Exception as e:
        return {
            "online": False,
            "message": f"❌ Error checking {agent_name}: {str(e)}"
        }


def check_all_agents_status() -> str:
    """
    Check status of all Dev Agents.

    Returns:
        Formatted status report
    """
    status_report = "🤖 **Dev Agent Team Status:**\n\n"

    for agent_key, agent_info in DEV_AGENTS.items():
        status = check_agent_status(agent_key)
        emoji = "🟢" if status["online"] else "🔴"
        status_report += f"{emoji} **{agent_info['name']}** (Port {agent_info['endpoint'].split(':')[-1]})\n"
        status_report += f"   Specialty: {agent_info['specialty']}\n"
        status_report += f"   Status: {status['message']}\n\n"

    return status_report


def get_agent_recommendations(task_id: int) -> str:
    """
    Get recommendations for which agent should handle a task.

    Args:
        task_id: Task ID to analyze

    Returns:
        Recommendation message
    """
    session = get_session()
    task = get_task_by_id(session, task_id)
    session.close()

    if not task:
        return f"❌ Task #{task_id} not found"

    # Detect best agent
    agent_key = detect_agent_specialty(task.title, task.description or "")

    if agent_key == 'general':
        return f"📋 Task #{task_id}: {task.title}\n\n" \
               f"🤔 No specific specialty detected. Recommendations:\n" \
               f"- Frontend Agent: If it involves UI/UX\n" \
               f"- Backend Agent: If it involves APIs/servers\n" \
               f"- Database Agent: If it involves data/schemas\n\n" \
               f"Defaulting to Frontend Agent for execution."

    agent_info = DEV_AGENTS[agent_key]

    return f"📋 Task #{task_id}: {task.title}\n\n" \
           f"✅ Recommended: **{agent_info['name']}**\n" \
           f"Specialty: {agent_info['specialty']}\n\n" \
           f"Detected keywords: {', '.join([kw for kw in agent_info['keywords'] if kw in f'{task.title.lower()} {(task.description or "").lower()}'][:5])}\n\n" \
           f"Ready to assign!"


def distribute_tasks_intelligently(task_ids: List[int]) -> str:
    """
    Distribute multiple tasks across specialist agents intelligently.

    Args:
        task_ids: List of task IDs to distribute

    Returns:
        Distribution report
    """
    if not task_ids:
        return "❌ No task IDs provided"

    # Categorize tasks by agent
    distribution = {
        'frontend': [],
        'backend': [],
        'database': [],
        'general': []
    }

    session = get_session()
    for task_id in task_ids:
        task = get_task_by_id(session, task_id)
        if task:
            agent_key = detect_agent_specialty(task.title, task.description or "")
            distribution[agent_key].append(task_id)
    session.close()

    # Build distribution report
    report = "🎯 **Intelligent Task Distribution:**\n\n"

    for agent_key in ['frontend', 'backend', 'database', 'general']:
        task_list = distribution[agent_key]
        if task_list:
            agent_name = DEV_AGENTS.get(agent_key, {}).get('name', 'General Agent')
            report += f"**{agent_name}** ({len(task_list)} tasks):\n"
            for task_id in task_list:
                report += f"  • Task #{task_id}\n"
            report += "\n"

    total_tasks = sum(len(tasks) for tasks in distribution.values())
    report += f"**Total:** {total_tasks} tasks distributed across {len([k for k, v in distribution.items() if v])} agents\n\n"
    report += "Ready to execute in parallel! 🚀"

    return report
