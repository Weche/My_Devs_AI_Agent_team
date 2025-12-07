"""Base agent class with common functionality"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from src.core.context_manager import ContextManager
from src.core.cost_tracker import CostTracker

load_dotenv()


class BaseAgent:
    """Base class for all AI agents"""

    def __init__(
        self,
        agent_name: str,
        config_path: str = "config/agents.yaml",
    ):
        """
        Initialize base agent

        Args:
            agent_name: Name of the agent (must match key in agents.yaml)
            config_path: Path to agents configuration file
        """
        self.agent_name = agent_name
        self.config = self._load_config(config_path)
        self.context_manager = ContextManager()
        self.cost_tracker = CostTracker()

        # Agent-specific config
        self.role = self.config.get("role", "AI Agent")
        self.goal = self.config.get("goal", "")
        self.backstory = self.config.get("backstory", "")
        self.model = self.config.get("model", "gpt-4o-mini")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 300)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration from YAML"""
        full_path = Path(config_path)

        if not full_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(full_path, "r", encoding="utf-8") as f:
            all_configs = yaml.safe_load(f)

        agent_config = all_configs.get("agents", {}).get(self.agent_name)

        if not agent_config:
            raise ValueError(f"Agent '{self.agent_name}' not found in config")

        return agent_config

    def log_interaction(
        self,
        project_name: str,
        user_input: str,
        response: str,
        tokens_used: int,
        cost_usd: float,
    ) -> None:
        """
        Log interaction to context manager and cost tracker

        Args:
            project_name: Name of the project
            user_input: User's input/command
            response: Agent's response
            tokens_used: Total tokens used
            cost_usd: Total cost in USD
        """
        # Log to context manager
        conversation = {
            "timestamp": self._get_timestamp(),
            "role": "user",
            "content": user_input,
            "tokens": tokens_used // 2,  # Approximate
        }
        self.context_manager.save_interaction(
            self.agent_name, project_name, conversation
        )

        conversation = {
            "timestamp": self._get_timestamp(),
            "role": "assistant",
            "content": response[:500],  # Truncate for storage
            "tokens": tokens_used // 2,  # Approximate
            "cost_usd": cost_usd,
        }
        self.context_manager.save_interaction(
            self.agent_name, project_name, conversation
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime

        return datetime.now().isoformat()

    def get_recent_context(
        self, project_name: str, days: int = 3, max_tokens: int = 500
    ) -> str:
        """
        Get recent context for a project

        Args:
            project_name: Name of the project
            days: Number of days to look back
            max_tokens: Maximum tokens to load

        Returns:
            Formatted context string
        """
        conversations, _ = self.context_manager.load_recent_context(
            self.agent_name, project_name, days, max_tokens
        )

        return self.context_manager.format_context_for_prompt(conversations)

    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.agent_name}', model='{self.model}')>"
