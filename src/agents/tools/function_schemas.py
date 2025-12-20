"""OpenAI function schemas for Albedo's tool calling"""

# Tool schemas for OpenAI function calling
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task in a project with optional due date, description, and priority",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "The name of the project (e.g., 'Yohga - init', 'Veggies list')"
                    },
                    "title": {
                        "type": "string",
                        "description": "The task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Task priority level"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in ISO format (YYYY-MM-DDTHH:MM:SS) or natural language"
                    }
                },
                "required": ["project_name", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for a specific project",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "The name of the project"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["todo", "in_progress", "blocked", "review", "done"],
                        "description": "Optional status filter"
                    }
                },
                "required": ["project_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_status",
            "description": "Get detailed status report for a project including progress and warnings",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "The name of the project"
                    }
                },
                "required": ["project_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_projects",
            "description": "List all active projects with their priorities",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_warnings",
            "description": "Get warnings for a project (overdue tasks, blockers, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "The name of the project"
                    }
                },
                "required": ["project_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_github_repos",
            "description": "List GitHub repositories for authenticated user or specified username",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "GitHub username (optional, defaults to authenticated user)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_github_repo_info",
            "description": "Get detailed information about a GitHub repository including recent commits and issues",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "Name of the repository"
                    },
                    "owner": {
                        "type": "string",
                        "description": "Owner of the repo (optional, defaults to authenticated user)"
                    }
                },
                "required": ["repo_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_github_issue",
            "description": "Create an issue in a GitHub repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "Name of the repository"
                    },
                    "title": {
                        "type": "string",
                        "description": "Issue title"
                    },
                    "body": {
                        "type": "string",
                        "description": "Issue description/body"
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of label names"
                    },
                    "owner": {
                        "type": "string",
                        "description": "Owner of the repo (optional, defaults to authenticated user)"
                    }
                },
                "required": ["repo_name", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_github_issues",
            "description": "List issues in a GitHub repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "Name of the repository"
                    },
                    "state": {
                        "type": "string",
                        "enum": ["open", "closed", "all"],
                        "description": "Issue state filter"
                    },
                    "owner": {
                        "type": "string",
                        "description": "Owner of the repo (optional, defaults to authenticated user)"
                    }
                },
                "required": ["repo_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_github_repo",
            "description": "Create a new GitHub repository for a project",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "Name of the repository (e.g., 'veggies-list', 'yohga-app')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Repository description"
                    },
                    "private": {
                        "type": "boolean",
                        "description": "Whether the repository should be private (default: false for public)"
                    },
                    "auto_init": {
                        "type": "boolean",
                        "description": "Initialize with README file (default: true)"
                    }
                },
                "required": ["repo_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_task_with_dev_agent",
            "description": "Assign a task to the Dev Agent for autonomous code execution. Dev Agent will write code, commit to git, and update task status. Use this for any task that requires writing code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to execute"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_dev_agent_status",
            "description": "Check if the Dev Agent service is online and ready to execute tasks",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_available_agents",
            "description": "List all available agents (Dev Agent, Lead Dev Agent) and their capabilities",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "store_memory",
            "description": "Store important information in long-term memory (preferences, decisions, facts, context). Use this to remember Master's preferences, important project decisions, or key facts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The information to remember"
                    },
                    "memory_type": {
                        "type": "string",
                        "enum": ["preference", "decision", "fact", "context"],
                        "description": "Type of memory"
                    },
                    "importance": {
                        "type": "integer",
                        "description": "Importance level 1-10 (10 = critical)",
                        "minimum": 1,
                        "maximum": 10
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Associated project name (optional)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for categorization"
                    }
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recall_memories",
            "description": "Retrieve relevant memories from long-term storage. Use this to remember Master's preferences, past decisions, or important context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (optional)"
                    },
                    "memory_type": {
                        "type": "string",
                        "enum": ["preference", "decision", "fact", "context"],
                        "description": "Filter by memory type (optional)"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Filter by project (optional)"
                    },
                    "min_importance": {
                        "type": "integer",
                        "description": "Minimum importance level (default: 5)",
                        "minimum": 1,
                        "maximum": 10
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of memories to retrieve (default: 5)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_memory_stats",
            "description": "Get statistics about stored memories",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]
