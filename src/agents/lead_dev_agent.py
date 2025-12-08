"""Lead Technical Dev Agent - Technical guidance and decision tracking

This agent represents Claude (Lead Developer) working with the CEO.
Maintains technical context and architectural decisions across sessions.
"""

import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

from openai import OpenAI

from src.agents.base_agent import BaseAgent
from src.core.database import get_session, get_project_by_name

load_dotenv()


class LeadDevAgent(BaseAgent):
    """Lead Technical Developer Agent - provides technical guidance and tracks decisions"""

    def __init__(self):
        super().__init__("lead_technical_dev")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_technical_advice(
        self, project_name: str, question: str, include_context_days: int = 7
    ) -> str:
        """
        Get technical advice for a project question

        Args:
            project_name: Name of the project
            question: Technical question to answer
            include_context_days: Days of context to include (default: 7)

        Returns:
            Technical advice response
        """
        # Validate project exists
        session = get_session()
        project = get_project_by_name(session, project_name)
        session.close()

        if not project:
            return f"Error: Project '{project_name}' not found"

        # Load recent technical context
        recent_context = self.get_recent_context(
            project_name, days=include_context_days, max_tokens=800
        )

        # Build prompt with technical focus
        prompt = f"""You are the Lead Technical Developer for {project_name}.

Your role:
- Provide technical guidance on architecture, implementation, and tooling
- Track technical decisions and their reasoning
- Ensure continuity across development sessions
- Focus on scalable, budget-friendly solutions

Recent technical discussions:
{recent_context if recent_context else "No recent context available."}

Current question:
{question}

Provide a clear, actionable technical response (max 200 words). Include:
1. Direct answer to the question
2. Technical reasoning/trade-offs
3. Recommended approach
4. Any relevant warnings or considerations

Be pragmatic and detail-oriented."""

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

            advice_text = response.choices[0].message.content
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
                command="technical_advice",
                response_summary=question[:100],
            )

            # Log interaction with full context
            self.log_interaction(
                project_name,
                f"Technical question: {question}",
                advice_text,
                tokens_used,
                cost_details["total_cost_usd"],
            )

            return advice_text

        except Exception as e:
            return f"Error getting technical advice: {str(e)}"

    def track_decision(
        self, project_name: str, decision: str, reasoning: str
    ) -> str:
        """
        Track a technical decision for future reference

        Args:
            project_name: Name of the project
            decision: The technical decision made
            reasoning: Why this decision was made

        Returns:
            Confirmation message
        """
        # Log decision to context (no OpenAI call needed)
        decision_log = f"TECHNICAL DECISION: {decision}\n\nREASONING: {reasoning}"

        self.context_manager.save_interaction(
            self.agent_name,
            project_name,
            {
                "timestamp": datetime.now().isoformat(),
                "role": "system",
                "content": decision_log,
                "tokens": 0,
                "decision": True,  # Mark as decision for future filtering
            },
        )

        return f"[OK] Tracked technical decision for {project_name}:\n{decision}"

    def review_architecture(
        self, project_name: str, requirement: str
    ) -> str:
        """
        Review architecture for a new requirement

        Args:
            project_name: Name of the project
            requirement: New feature/requirement to architect

        Returns:
            Architecture recommendation
        """
        # Validate project exists
        session = get_session()
        project = get_project_by_name(session, project_name)
        session.close()

        if not project:
            return f"Error: Project '{project_name}' not found"

        # Load recent context and past decisions
        recent_context = self.get_recent_context(
            project_name, days=14, max_tokens=1000
        )

        # Build architectural review prompt
        prompt = f"""You are the Lead Technical Developer reviewing architecture for {project_name}.

Past technical context and decisions:
{recent_context if recent_context else "No previous technical context."}

New requirement to architect:
{requirement}

Provide architectural guidance (max 250 words) including:
1. Recommended approach/pattern
2. Key technical components needed
3. Trade-offs and alternatives considered
4. Budget/performance implications
5. Integration with existing architecture

Focus on scalable, maintainable, cost-effective solutions."""

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

            architecture_text = response.choices[0].message.content
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
                command="architecture_review",
                response_summary=requirement[:100],
            )

            # Log interaction
            self.log_interaction(
                project_name,
                f"Architecture review: {requirement}",
                architecture_text,
                tokens_used,
                cost_details["total_cost_usd"],
            )

            return architecture_text

        except Exception as e:
            return f"Error reviewing architecture: {str(e)}"

    def get_context_summary(
        self, project_name: str, days: int = 30
    ) -> str:
        """
        Get summary of recent technical work and decisions

        Args:
            project_name: Name of the project
            days: Number of days to summarize

        Returns:
            Summary of technical context
        """
        conversations, total_tokens = self.context_manager.load_recent_context(
            self.agent_name, project_name, days=days, max_tokens=2000
        )

        if not conversations:
            return f"No technical context found for {project_name} in the last {days} days."

        # Format summary
        summary_lines = [
            f"Technical Context Summary for {project_name}",
            f"Last {days} days ({len(conversations)} interactions, ~{total_tokens} tokens)",
            "",
            "Recent interactions:",
        ]

        for conv in conversations[-10:]:  # Last 10 interactions
            timestamp = conv.get("timestamp", "Unknown time")
            role = conv.get("role", "unknown")
            content = conv.get("content", "")[:100]  # First 100 chars

            summary_lines.append(f"  [{timestamp}] {role}: {content}...")

        return "\n".join(summary_lines)
