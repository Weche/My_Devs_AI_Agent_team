"""Command-line interface for project management"""

import sys
import click
from rich.console import Console
from rich.table import Table
from datetime import datetime

from src.agents.pm_agent import PMAgent
from src.core.cost_tracker import CostTracker
from src.core.database import get_session, get_project_by_name, get_tasks_by_project

console = Console()


@click.group()
def cli():
    """My Devs AI Agent Team - CLI Interface"""
    pass


@cli.command()
@click.argument("project_name")
def status(project_name):
    """Get project status"""
    console.print(f"\n[bold cyan]Getting status for project: {project_name}[/bold cyan]\n")

    pm_agent = PMAgent()
    result = pm_agent.get_status(project_name)

    console.print(result)
    console.print()


@cli.command()
@click.argument("project_name")
@click.argument("task_title")
@click.option("--description", "-d", default="", help="Task description")
@click.option(
    "--priority",
    "-p",
    default="medium",
    type=click.Choice(["critical", "high", "medium", "low"]),
    help="Task priority",
)
def create(project_name, task_title, description, priority):
    """Create a new task"""
    console.print(f"\n[bold cyan]Creating task in {project_name}[/bold cyan]\n")

    pm_agent = PMAgent()
    result = pm_agent.create_task(project_name, task_title, description, priority)

    console.print(result)
    console.print()


@cli.command()
@click.argument("project_name")
@click.option(
    "--status",
    "-s",
    default=None,
    type=click.Choice(["todo", "in_progress", "blocked", "review", "done"]),
    help="Filter by status",
)
def tasks(project_name, status):
    """List tasks for a project"""
    console.print(f"\n[bold cyan]Tasks for {project_name}[/bold cyan]\n")

    session = get_session()
    project = get_project_by_name(session, project_name)

    if not project:
        console.print(f"[red]Error: Project '{project_name}' not found[/red]\n")
        session.close()
        return

    task_list = get_tasks_by_project(session, project.id, status=status)
    session.close()

    if not task_list:
        console.print(f"No tasks found.\n")
        return

    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Status", width=12)
    table.add_column("Priority", width=10)
    table.add_column("Title", width=50)
    table.add_column("Assigned To", width=15)

    for task in task_list:
        # Color code status
        status_color = {
            "todo": "yellow",
            "in_progress": "cyan",
            "blocked": "red",
            "review": "magenta",
            "done": "green",
        }.get(task.status, "white")

        table.add_row(
            str(task.id),
            f"[{status_color}]{task.status}[/{status_color}]",
            task.priority,
            task.title[:47] + "..." if len(task.title) > 50 else task.title,
            task.assigned_to or "-",
        )

    console.print(table)
    console.print()


@cli.command()
@click.argument("project_name")
def warnings(project_name):
    """Show warnings for a project"""
    console.print(f"\n[bold cyan]Warnings for {project_name}[/bold cyan]\n")

    pm_agent = PMAgent()
    result = pm_agent.get_warnings(project_name)

    console.print(result)
    console.print()


@cli.command()
@click.argument("period", type=click.Choice(["today", "month"]))
def costs(period):
    """View cost tracking information"""
    cost_tracker = CostTracker()

    if period == "today":
        console.print("\n[bold cyan]Today's Costs[/bold cyan]\n")
        cost_tracker.print_daily_report()
    elif period == "month":
        console.print("\n[bold cyan]Monthly Cost Summary[/bold cyan]\n")
        summary = cost_tracker.get_monthly_summary()

        console.print(f"Month: {summary['month']}")
        console.print(f"Total Calls: {summary['total_calls']}")
        console.print(f"Total Tokens: {summary['total_tokens']:,}")
        console.print(f"Total Cost: ${summary['total_cost_usd']:.4f}")
        console.print(f"Budget: ${summary['budget_limit']:.2f}")
        console.print(f"Used: {summary['budget_used_percent']:.1f}%")

        if summary.get("by_agent"):
            console.print("\n[bold]By Agent:[/bold]")
            for agent, stats in summary["by_agent"].items():
                console.print(f"  • {agent}: ${stats['cost_usd']:.4f} ({stats['calls']} calls)")

        if summary.get("by_project"):
            console.print("\n[bold]By Project:[/bold]")
            for project, stats in summary["by_project"].items():
                console.print(f"  • {project}: ${stats['cost_usd']:.4f} ({stats['calls']} calls)")

        console.print()


@cli.command()
def projects():
    """List all active projects"""
    from src.core.database import get_active_projects, Task

    console.print("\n[bold cyan]Active Projects[/bold cyan]\n")

    session = get_session()
    project_list = get_active_projects(session)

    if not project_list:
        console.print("No active projects found.\n")
        session.close()
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", width=25)
    table.add_column("Tasks", width=10)
    table.add_column("Priority", width=10)
    table.add_column("Created", width=20)

    for project in project_list:
        task_count = session.query(Task).filter(Task.project_id == project.id).count()

        table.add_row(
            project.name,
            str(task_count),
            str(project.priority),
            project.created_at.strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)
    console.print()
    session.close()


@cli.command()
def version():
    """Show version information"""
    console.print("\n[bold cyan]My Devs AI Agent Team[/bold cyan]")
    console.print("Version: 0.1.0 (Milestone 1)")
    console.print("Lead Dev: Claude")
    console.print("CEO: Christian Orquera\n")


if __name__ == "__main__":
    cli()
