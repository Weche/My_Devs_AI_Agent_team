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
    }
]
