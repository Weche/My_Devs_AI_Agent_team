"""Cost Tracker - Transparent tracking of all OpenAI API costs"""

import json
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


# Pricing per 1M tokens (as of December 2024)
PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
}


class CostTracker:
    """Tracks API costs with detailed logging and budget alerts"""

    def __init__(
        self,
        base_path: str = "data/logs/costs",
        daily_budget: float = 1.00,
        monthly_budget: float = 20.00,
    ):
        """
        Initialize cost tracker

        Args:
            base_path: Directory for cost logs
            daily_budget: Daily budget alert threshold
            monthly_budget: Monthly budget limit
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget

    def calculate_cost(
        self, tokens_input: int, tokens_output: int, model: str
    ) -> Dict[str, float]:
        """
        Calculate cost for an API call

        Args:
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens
            model: Model name (e.g., 'gpt-4o-mini')

        Returns:
            Dict with cost breakdown
        """
        pricing = PRICING.get(model, PRICING["gpt-4o-mini"])

        cost_input = (tokens_input / 1_000_000) * pricing["input"]
        cost_output = (tokens_output / 1_000_000) * pricing["output"]
        total_cost = cost_input + cost_output

        return {
            "cost_input_usd": round(cost_input, 7),
            "cost_output_usd": round(cost_output, 7),
            "total_cost_usd": round(total_cost, 7),
        }

    def _get_daily_log_path(self, date: Optional[datetime] = None) -> Path:
        """Get path to daily cost log"""
        if date is None:
            date = datetime.now()
        date_str = date.strftime("%Y-%m-%d")
        return self.base_path / f"{date_str}.json"

    def log_api_call(
        self,
        agent: str,
        project: str,
        model: str,
        tokens_input: int,
        tokens_output: int,
        command: str,
        response_summary: str = "",
    ) -> Dict[str, Any]:
        """
        Log a single API call with full details

        Args:
            agent: Agent name (e.g., 'pm_agent')
            project: Project name (e.g., 'example_project')
            model: Model used
            tokens_input: Input tokens
            tokens_output: Output tokens
            command: Command that triggered the call
            response_summary: Brief summary of response

        Returns:
            API call record
        """
        # Calculate costs
        costs = self.calculate_cost(tokens_input, tokens_output, model)

        # Create API call record
        api_call = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "project": project,
            "model": model,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            **costs,
            "command": command,
            "response_summary": response_summary[:200],  # Truncate if too long
        }

        # Load or create daily log
        log_path = self._get_daily_log_path()
        if log_path.exists():
            with open(log_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = self._create_empty_daily_log()

        # Append API call
        data["api_calls"].append(api_call)

        # Update daily summary
        self._update_daily_summary(data, agent, project, model, tokens_input + tokens_output, costs["total_cost_usd"])

        # Check budget alerts
        alerts = self._check_budget_alerts(data)
        data["alerts"] = alerts

        # Save updated log
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return api_call

    def _create_empty_daily_log(self) -> Dict[str, Any]:
        """Create empty daily log structure"""
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "api_calls": [],
            "daily_summary": {
                "total_calls": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "by_agent": {},
                "by_model": {},
                "by_project": {},
            },
            "monthly_projection": 0.0,
            "budget_status": {
                "daily_limit": self.daily_budget,
                "daily_used": 0.0,
                "daily_remaining": self.daily_budget,
                "monthly_limit": self.monthly_budget,
                "monthly_used": 0.0,
                "monthly_remaining": self.monthly_budget,
            },
            "alerts": [],
        }

    def _update_daily_summary(
        self,
        data: Dict[str, Any],
        agent: str,
        project: str,
        model: str,
        tokens: int,
        cost: float,
    ) -> None:
        """Update daily summary statistics"""
        summary = data["daily_summary"]

        # Update totals
        summary["total_calls"] += 1
        summary["total_tokens"] += tokens
        summary["total_cost_usd"] = round(summary["total_cost_usd"] + cost, 7)

        # Update by agent
        if agent not in summary["by_agent"]:
            summary["by_agent"][agent] = {"calls": 0, "tokens": 0, "cost_usd": 0.0}
        summary["by_agent"][agent]["calls"] += 1
        summary["by_agent"][agent]["tokens"] += tokens
        summary["by_agent"][agent]["cost_usd"] = round(
            summary["by_agent"][agent]["cost_usd"] + cost, 7
        )

        # Update by model
        if model not in summary["by_model"]:
            summary["by_model"][model] = {"calls": 0, "tokens": 0, "cost_usd": 0.0}
        summary["by_model"][model]["calls"] += 1
        summary["by_model"][model]["tokens"] += tokens
        summary["by_model"][model]["cost_usd"] = round(
            summary["by_model"][model]["cost_usd"] + cost, 7
        )

        # Update by project
        if project not in summary["by_project"]:
            summary["by_project"][project] = {"calls": 0, "tokens": 0, "cost_usd": 0.0}
        summary["by_project"][project]["calls"] += 1
        summary["by_project"][project]["tokens"] += tokens
        summary["by_project"][project]["cost_usd"] = round(
            summary["by_project"][project]["cost_usd"] + cost, 7
        )

        # Update budget status
        daily_used = summary["total_cost_usd"]
        data["budget_status"]["daily_used"] = daily_used
        data["budget_status"]["daily_remaining"] = round(
            self.daily_budget - daily_used, 7
        )

        # Calculate monthly usage and projection
        monthly_used = self._get_monthly_cost()
        data["budget_status"]["monthly_used"] = monthly_used
        data["budget_status"]["monthly_remaining"] = round(
            self.monthly_budget - monthly_used, 7
        )

        # Project monthly cost (simple average)
        day_of_month = datetime.now().day
        if day_of_month > 0:
            data["monthly_projection"] = round((monthly_used / day_of_month) * 30, 2)

    def _check_budget_alerts(self, data: Dict[str, Any]) -> List[str]:
        """Check if budget thresholds are exceeded"""
        alerts = []
        daily_used = data["budget_status"]["daily_used"]
        monthly_used = data["budget_status"]["monthly_used"]

        # Daily budget alert
        if daily_used > self.daily_budget:
            alerts.append(
                f"⚠️  Daily budget exceeded: ${daily_used:.2f} / ${self.daily_budget:.2f}"
            )
        elif daily_used > self.daily_budget * 0.8:
            alerts.append(
                f"⚠️  Daily budget 80% used: ${daily_used:.2f} / ${self.daily_budget:.2f}"
            )

        # Monthly budget alert
        if monthly_used > self.monthly_budget:
            alerts.append(
                f"🚨 Monthly budget exceeded: ${monthly_used:.2f} / ${self.monthly_budget:.2f}"
            )
        elif monthly_used > self.monthly_budget * 0.8:
            alerts.append(
                f"⚠️  Monthly budget 80% used: ${monthly_used:.2f} / ${self.monthly_budget:.2f}"
            )

        return alerts

    def _get_monthly_cost(self) -> float:
        """Calculate total cost for current month"""
        total_cost = 0.0
        current_month = datetime.now().strftime("%Y-%m")

        for file_path in self.base_path.glob("*.json"):
            if file_path.stem.startswith(current_month):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        total_cost += data["daily_summary"]["total_cost_usd"]
                except (json.JSONDecodeError, KeyError, IOError):
                    continue

        return round(total_cost, 7)

    def get_daily_summary(self, date: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
        """Get summary for a specific day"""
        log_path = self._get_daily_log_path(date)
        if not log_path.exists():
            return None

        try:
            with open(log_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def get_monthly_summary(self) -> Dict[str, Any]:
        """Get summary for current month"""
        current_month = datetime.now().strftime("%Y-%m")
        total_calls = 0
        total_tokens = 0
        total_cost = 0.0
        by_agent = {}
        by_project = {}

        for file_path in self.base_path.glob(f"{current_month}-*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    summary = data["daily_summary"]

                    total_calls += summary["total_calls"]
                    total_tokens += summary["total_tokens"]
                    total_cost += summary["total_cost_usd"]

                    # Aggregate by agent
                    for agent, stats in summary.get("by_agent", {}).items():
                        if agent not in by_agent:
                            by_agent[agent] = {"calls": 0, "tokens": 0, "cost_usd": 0.0}
                        by_agent[agent]["calls"] += stats["calls"]
                        by_agent[agent]["tokens"] += stats["tokens"]
                        by_agent[agent]["cost_usd"] += stats["cost_usd"]

                    # Aggregate by project
                    for project, stats in summary.get("by_project", {}).items():
                        if project not in by_project:
                            by_project[project] = {"calls": 0, "tokens": 0, "cost_usd": 0.0}
                        by_project[project]["calls"] += stats["calls"]
                        by_project[project]["tokens"] += stats["tokens"]
                        by_project[project]["cost_usd"] += stats["cost_usd"]

            except (json.JSONDecodeError, IOError):
                continue

        return {
            "month": current_month,
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 7),
            "by_agent": by_agent,
            "by_project": by_project,
            "budget_limit": self.monthly_budget,
            "budget_used_percent": round((total_cost / self.monthly_budget) * 100, 2)
            if self.monthly_budget > 0
            else 0,
        }

    def export_to_csv(self, output_path: Optional[str] = None, days: int = 30) -> str:
        """
        Export cost data to CSV for analysis

        Args:
            output_path: Output file path (default: data/logs/costs/export_YYYY-MM-DD.csv)
            days: Number of days to export

        Returns:
            Path to exported CSV file
        """
        if output_path is None:
            output_path = str(
                self.base_path / f"export_{datetime.now().strftime('%Y-%m-%d')}.csv"
            )

        rows = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            log_path = self._get_daily_log_path(date)

            if not log_path.exists():
                continue

            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for call in data.get("api_calls", []):
                    rows.append(
                        {
                            "timestamp": call["timestamp"],
                            "agent": call["agent"],
                            "project": call["project"],
                            "model": call["model"],
                            "tokens_in": call["tokens_input"],
                            "tokens_out": call["tokens_output"],
                            "cost_usd": call["total_cost_usd"],
                            "command": call["command"],
                        }
                    )
            except (json.JSONDecodeError, IOError):
                continue

        # Write CSV
        if rows:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "timestamp",
                        "agent",
                        "project",
                        "model",
                        "tokens_in",
                        "tokens_out",
                        "cost_usd",
                        "command",
                    ],
                )
                writer.writeheader()
                writer.writerows(rows)

        return output_path

    def print_daily_report(self, date: Optional[datetime] = None) -> None:
        """Print formatted daily cost report"""
        summary = self.get_daily_summary(date)
        if not summary:
            print("No data available for this date.")
            return

        print("\n" + "=" * 60)
        print(f"DAILY COST REPORT - {summary['date']}")
        print("=" * 60)

        # Overall stats
        daily_sum = summary["daily_summary"]
        print(f"\n📊 Total: {daily_sum['total_calls']} API calls")
        print(f"🎯 Tokens: {daily_sum['total_tokens']:,}")
        print(f"💰 Cost: ${daily_sum['total_cost_usd']:.4f}")

        # By agent
        if daily_sum.get("by_agent"):
            print("\n📋 By Agent:")
            for agent, stats in daily_sum["by_agent"].items():
                print(f"  • {agent}: ${stats['cost_usd']:.4f} ({stats['calls']} calls)")

        # By project
        if daily_sum.get("by_project"):
            print("\n📁 By Project:")
            for project, stats in daily_sum["by_project"].items():
                print(f"  • {project}: ${stats['cost_usd']:.4f} ({stats['calls']} calls)")

        # Budget status
        budget = summary["budget_status"]
        print("\n💳 Budget Status:")
        print(f"  Daily: ${budget['daily_used']:.2f} / ${budget['daily_limit']:.2f}")
        print(f"  Monthly: ${budget['monthly_used']:.2f} / ${budget['monthly_limit']:.2f}")

        # Alerts
        if summary.get("alerts"):
            print("\n⚠️  Alerts:")
            for alert in summary["alerts"]:
                print(f"  {alert}")

        print("=" * 60 + "\n")
