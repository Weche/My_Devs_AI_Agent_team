"""Context Manager - Handles JSON-based conversation history for agents"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any


class ContextManager:
    """Manages agent conversation context using daily JSON logs"""

    def __init__(self, base_path: str = "data/agent_context"):
        """
        Initialize context manager

        Args:
            base_path: Base directory for context storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, agent_name: str, project_name: str, date: datetime) -> Path:
        """
        Get file path for a specific agent/project/date

        Args:
            agent_name: Name of the agent (e.g., 'pm_agent')
            project_name: Name of the project (e.g., 'binance_trading')
            date: Date for the log file

        Returns:
            Path to the JSON file
        """
        date_str = date.strftime("%Y-%m-%d")
        file_path = self.base_path / agent_name / project_name / f"{date_str}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        return file_path

    def save_interaction(
        self,
        agent_name: str,
        project_name: str,
        conversation: Dict[str, Any],
        decision: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Save an interaction to the daily log

        Args:
            agent_name: Name of the agent
            project_name: Name of the project
            conversation: Conversation data (timestamp, role, content, tokens, cost)
            decision: Optional decision made during this interaction
        """
        date = datetime.now()
        file_path = self._get_file_path(agent_name, project_name, date)

        # Load existing data or create new
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {
                "date": date.strftime("%Y-%m-%d"),
                "agent": agent_name,
                "project": project_name,
                "conversations": [],
                "decisions_made": [],
                "total_tokens": 0,
                "total_cost_usd": 0.0,
            }

        # Add conversation
        data["conversations"].append(conversation)
        data["total_tokens"] += conversation.get("tokens", 0)
        data["total_cost_usd"] += conversation.get("cost_usd", 0.0)

        # Add decision if provided
        if decision:
            data["decisions_made"].append(decision)

        # Save updated data
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_recent_context(
        self,
        agent_name: str,
        project_name: str,
        days: int = 7,
        max_tokens: int = 1000,
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Load recent conversations within token budget

        Args:
            agent_name: Name of the agent
            project_name: Name of the project
            days: Number of days to look back
            max_tokens: Maximum tokens to load

        Returns:
            Tuple of (conversations list, total tokens)
        """
        contexts = []
        total_tokens = 0

        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            file_path = self._get_file_path(agent_name, project_name, date)

            if not file_path.exists():
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Add conversations until token limit
                for conv in reversed(data["conversations"]):
                    conv_tokens = conv.get("tokens", 0)
                    if total_tokens + conv_tokens > max_tokens:
                        break
                    contexts.insert(0, conv)
                    total_tokens += conv_tokens

                if total_tokens >= max_tokens:
                    break

            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load context from {file_path}: {e}")
                continue

        return contexts, total_tokens

    def get_recent_decisions(
        self,
        agent_name: str,
        project_name: str,
        days: int = 7,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get recent decisions made by an agent

        Args:
            agent_name: Name of the agent
            project_name: Name of the project
            days: Number of days to look back
            limit: Maximum number of decisions to return

        Returns:
            List of recent decisions
        """
        decisions = []

        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            file_path = self._get_file_path(agent_name, project_name, date)

            if not file_path.exists():
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                decisions.extend(data.get("decisions_made", []))

                if len(decisions) >= limit:
                    break

            except (json.JSONDecodeError, IOError):
                continue

        return decisions[:limit]

    def get_daily_summary(
        self, agent_name: str, project_name: str, date: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get summary for a specific day

        Args:
            agent_name: Name of the agent
            project_name: Name of the project
            date: Date to get summary for (default: today)

        Returns:
            Daily summary or None if not found
        """
        if date is None:
            date = datetime.now()

        file_path = self._get_file_path(agent_name, project_name, date)

        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def format_context_for_prompt(
        self, conversations: List[Dict[str, Any]], max_length: int = 2000
    ) -> str:
        """
        Format conversations into a compact string for prompts

        Args:
            conversations: List of conversation dicts
            max_length: Maximum character length

        Returns:
            Formatted context string
        """
        if not conversations:
            return "No recent context available."

        lines = []
        total_length = 0

        for conv in conversations:
            timestamp = conv.get("timestamp", "")
            role = conv.get("role", "")
            content = conv.get("content", "")

            # Format: [time] role: content
            line = f"[{timestamp}] {role}: {content}"

            if total_length + len(line) > max_length:
                break

            lines.append(line)
            total_length += len(line)

        return "\n".join(lines)

    def cleanup_old_logs(self, days_to_keep: int = 30) -> int:
        """
        Delete logs older than specified days

        Args:
            days_to_keep: Number of days to keep

        Returns:
            Number of files deleted
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0

        for agent_dir in self.base_path.iterdir():
            if not agent_dir.is_dir():
                continue

            for project_dir in agent_dir.iterdir():
                if not project_dir.is_dir():
                    continue

                for file_path in project_dir.glob("*.json"):
                    try:
                        # Parse date from filename
                        date_str = file_path.stem
                        file_date = datetime.strptime(date_str, "%Y-%m-%d")

                        if file_date < cutoff_date:
                            file_path.unlink()
                            deleted_count += 1

                    except (ValueError, OSError):
                        continue

        return deleted_count
