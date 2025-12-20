"""Agent Management - Create and manage new specialized agents dynamically"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional


def create_new_agent(
    agent_name: str,
    specialty: str,
    port: int,
    keywords: list[str],
    description: str,
    request_approval: bool = True
) -> str:
    """
    Create a new specialized agent dynamically.

    Args:
        agent_name: Name of the agent (e.g., "Testing Agent")
        specialty: Agent specialty (e.g., "testing", "devops", "security")
        port: Port number for the agent (e.g., 3004, 3005)
        keywords: List of keywords for auto-detection
        description: Description of agent's expertise
        request_approval: Whether to request Master's approval first

    Returns:
        Result message with approval request or creation confirmation
    """
    # Validate port
    if port < 3001 or port > 3010:
        return f"Error: Port must be between 3001-3010. Got: {port}"

    # Check if port already in use
    existing_agents = get_all_agents()
    for agent in existing_agents:
        if agent.get("port") == port:
            return f"Error: Port {port} already in use by {agent.get('name')}"

    # Request approval from Master
    if request_approval:
        return f"""
**New Agent Creation Request**

Master Christian, I'd like to create a new specialized agent:

**Agent Details:**
- Name: {agent_name}
- Specialty: {specialty}
- Port: {port}
- Keywords: {', '.join(keywords)}
- Description: {description}

**What it will do:**
This agent will handle tasks containing keywords: {', '.join(keywords[:5])}

**Benefits:**
- More specialized expertise for {specialty} tasks
- Parallel execution with other agents
- Better code quality for this domain

**Approval needed:**
Please confirm if I should create this agent by saying:
"Yes, create the {agent_name}"

Or decline with:
"No, don't create it"
"""

    # If approval granted, create the agent
    try:
        agent_dir_name = f"{specialty.lower()}-agent"
        base_dir = Path(__file__).parent.parent.parent.parent / "dev-agents"
        agent_dir = base_dir / agent_dir_name

        # Check if already exists
        if agent_dir.exists():
            return f"Error: Agent directory {agent_dir_name} already exists"

        # Copy from frontend-agent template
        template_dir = base_dir / "frontend-agent"
        if not template_dir.exists():
            return "Error: Frontend agent template not found"

        # Copy template
        shutil.copytree(template_dir, agent_dir)

        # Update package.json
        package_json_path = agent_dir / "package.json"
        with open(package_json_path, 'r') as f:
            package_data = json.load(f)

        package_data["name"] = f"{specialty.lower()}-dev-agent"
        package_data["description"] = f"{agent_name} - {description}"

        with open(package_json_path, 'w') as f:
            json.dump(package_data, f, indent=2)

        # Create .env.example
        env_content = f"""# {agent_name} Configuration (Port {port})
PORT={port}
AGENT_NAME={agent_name}
AGENT_SPECIALTY={specialty.lower()}

# AI Provider (use OpenAI by default)
OPENAI_API_KEY=your_openai_api_key_here
# USE_ANTHROPIC=true  # Uncomment to use Claude instead
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Workspace directory (relative to project root)
WORKSPACE_DIR=../../workspaces
PROJECT_WORKSPACE=workspace  # Will be set per-task dynamically

# Database path (relative to project root)
DATABASE_PATH=../../data/database/pm_system.db

# GitHub (optional - for git push)
GITHUB_USER=your_github_username
GITHUB_TOKEN=your_github_token

# Specialty Keywords ({specialty.capitalize()})
SPECIALTY_KEYWORDS={','.join(keywords)}
"""

        env_path = agent_dir / ".env.example"
        with open(env_path, 'w') as f:
            f.write(env_content)

        # Update agent.ts with specialized prompt
        agent_ts_path = agent_dir / "src" / "agent.ts"
        with open(agent_ts_path, 'r') as f:
            agent_ts = f.read()

        # Replace agent name and specialty in the prompt
        agent_ts = agent_ts.replace(
            'Frontend Dev Agent',
            agent_name
        )
        agent_ts = agent_ts.replace(
            'frontend',
            specialty.lower()
        )
        agent_ts = agent_ts.replace(
            'Frontend Specialist',
            f'{specialty.capitalize()} Specialist'
        )

        # Add custom description
        custom_prompt = f"""
Your specialty: {specialty.upper()} development
- {description}
- Expert in: {', '.join(keywords[:10])}
- Focus on best practices for {specialty} tasks
"""

        agent_ts = agent_ts.replace(
            'Your specialty: FRONTEND development',
            custom_prompt
        )

        with open(agent_ts_path, 'w') as f:
            f.write(agent_ts)

        # Register agent in multi_agent_tools.py
        register_agent_in_config(agent_name, specialty, port, keywords, description)

        return f"""
✅ **{agent_name} Created Successfully!**

**Location:** dev-agents/{agent_dir_name}/
**Port:** {port}
**Specialty:** {specialty}

**Next Steps:**
1. Copy .env file:
   ```
   cp dev-agents/{agent_dir_name}/.env.example dev-agents/{agent_dir_name}/.env
   ```

2. Add your OpenAI API key to the .env file

3. Install dependencies:
   ```
   cd dev-agents/{agent_dir_name}
   npm install
   ```

4. Start the agent:
   ```
   npm run dev
   ```

Or restart the orchestrator to include this new agent automatically!

The agent is now registered and will handle tasks with keywords: {', '.join(keywords[:5])}
"""

    except Exception as e:
        return f"Error creating agent: {str(e)}"


def register_agent_in_config(
    agent_name: str,
    specialty: str,
    port: int,
    keywords: list[str],
    description: str
) -> None:
    """
    Register new agent in multi_agent_tools.py configuration.
    """
    # Note: In production, this would update the DEV_AGENTS dict in multi_agent_tools.py
    # For now, we'll create a JSON config file that gets loaded at runtime
    config_path = Path(__file__).parent / "agent_config.json"

    if config_path.exists():
        with open(config_path, 'r') as f:
            agents = json.load(f)
    else:
        agents = {}

    agents[specialty.lower()] = {
        "endpoint": f"http://localhost:{port}",
        "name": agent_name,
        "specialty": description,
        "keywords": keywords
    }

    with open(config_path, 'w') as f:
        json.dump(agents, f, indent=2)


def get_all_agents() -> list[dict]:
    """
    Get list of all registered agents.

    Returns:
        List of agent configurations
    """
    # Get from multi_agent_tools.py
    from src.agents.tools.multi_agent_tools import DEV_AGENTS

    agents = []
    for key, info in DEV_AGENTS.items():
        agents.append({
            "key": key,
            "name": info["name"],
            "port": int(info["endpoint"].split(":")[-1]),
            "specialty": info["specialty"],
            "keywords": info.get("keywords", [])
        })

    # Add dynamically created agents from config
    config_path = Path(__file__).parent / "agent_config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            dynamic_agents = json.load(f)

        for key, info in dynamic_agents.items():
            if key not in DEV_AGENTS:  # Don't duplicate
                agents.append({
                    "key": key,
                    "name": info["name"],
                    "port": int(info["endpoint"].split(":")[-1]),
                    "specialty": info["specialty"],
                    "keywords": info.get("keywords", [])
                })

    return agents


def suggest_new_agent(task_pattern: str) -> str:
    """
    Suggest creating a new agent based on recurring task patterns.

    Args:
        task_pattern: Description of recurring task type

    Returns:
        Suggestion message
    """
    suggestions = {
        "testing": {
            "name": "Testing Agent",
            "specialty": "testing",
            "port": 3004,
            "keywords": ["test", "unittest", "pytest", "jest", "testing", "qa", "e2e", "integration"],
            "description": "Automated testing expert - unit tests, integration tests, E2E tests"
        },
        "devops": {
            "name": "DevOps Agent",
            "specialty": "devops",
            "port": 3005,
            "keywords": ["docker", "kubernetes", "ci/cd", "deploy", "infrastructure", "terraform", "ansible"],
            "description": "DevOps specialist - Docker, Kubernetes, CI/CD, infrastructure as code"
        },
        "security": {
            "name": "Security Agent",
            "specialty": "security",
            "port": 3006,
            "keywords": ["security", "auth", "encryption", "vulnerability", "owasp", "penetration"],
            "description": "Security specialist - authentication, authorization, vulnerability scanning"
        },
        "mobile": {
            "name": "Mobile Agent",
            "specialty": "mobile",
            "port": 3007,
            "keywords": ["mobile", "react-native", "flutter", "ios", "android", "app"],
            "description": "Mobile development expert - React Native, Flutter, iOS, Android"
        }
    }

    pattern_lower = task_pattern.lower()
    for key, config in suggestions.items():
        if any(keyword in pattern_lower for keyword in config["keywords"][:3]):
            return f"""
**Agent Suggestion**

Master, I notice you have {task_pattern} tasks. I suggest creating a specialized agent:

**{config['name']}**
- Specialty: {config['specialty']}
- Port: {config['port']}
- Handles: {', '.join(config['keywords'][:5])}

This would give you better expertise for these tasks!

Would you like me to create this agent?
"""

    return "No agent suggestions at this time."
