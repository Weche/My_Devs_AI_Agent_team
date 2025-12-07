"""Seed database with example data"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import (
    get_session,
    Project,
    Task,
    Agent,
    AgentProjectAssignment,
)


def seed_data():
    """Create example project, agents, and tasks"""
    session = get_session()

    print("\n" + "=" * 60)
    print("SEEDING DATABASE WITH EXAMPLE DATA")
    print("=" * 60)

    try:
        # Create Example Project
        print("\n[1/3] Creating projects...")

        example_project = Project(
            name="Example Project",
            description="Example project for testing the system",
            status="active",
            priority=5,
            budget=5000.0,
        )
        session.add(example_project)
        session.commit()
        session.refresh(example_project)
        print(f"  ✓ Created project: {example_project.name} (ID: {example_project.id})")

        # Create Agents
        print("\n[2/3] Creating agents...")

        pm_agent = Agent(
            name="pm_agent",
            role="Project Manager",
            description="Manages tasks and provides status updates",
            backstory="Experienced PM focused on delivering results",
            goal="Manage tasks and identify blockers",
            tools='["TaskQuery", "TaskCreate", "TaskUpdate"]',
            model="gpt-4o-mini",
            temperature=0.3,
            is_active=True,
        )
        session.add(pm_agent)

        lead_dev_agent = Agent(
            name="lead_technical_dev",
            role="Lead Technical Developer",
            description="Provides technical guidance and tracks decisions",
            backstory="Lead Developer partnering with CEO",
            goal="Provide technical guidance",
            tools='["TechnicalQuery", "ArchitectureAdvice"]',
            model="gpt-4o-mini",
            temperature=0.5,
            is_active=True,
        )
        session.add(lead_dev_agent)

        session.commit()
        session.refresh(pm_agent)
        session.refresh(lead_dev_agent)
        print(f"  ✓ Created agent: {pm_agent.name} (ID: {pm_agent.id})")
        print(f"  ✓ Created agent: {lead_dev_agent.name} (ID: {lead_dev_agent.id})")

        # Assign agents to project
        pm_assignment = AgentProjectAssignment(
            agent_id=pm_agent.id, project_id=example_project.id
        )
        dev_assignment = AgentProjectAssignment(
            agent_id=lead_dev_agent.id, project_id=example_project.id
        )
        session.add(pm_assignment)
        session.add(dev_assignment)
        session.commit()
        print(f"  ✓ Assigned agents to {example_project.name}")

        # Create sample tasks
        print("\n[3/3] Creating sample tasks...")

        tasks = [
            Task(
                project_id=example_project.id,
                title="Setup development environment",
                description="Install dependencies, configure IDE, setup database",
                status="done",
                priority="high",
                assigned_to="lead_technical_dev",
                created_by="ceo",
                completed_at=datetime.utcnow() - timedelta(days=2),
            ),
            Task(
                project_id=example_project.id,
                title="Implement PM Agent",
                description="Create PM Agent with task management capabilities",
                status="done",
                priority="critical",
                assigned_to="lead_technical_dev",
                created_by="ceo",
                completed_at=datetime.utcnow() - timedelta(days=1),
            ),
            Task(
                project_id=example_project.id,
                title="Create CLI interface",
                description="Build command-line interface for project management",
                status="in_progress",
                priority="high",
                assigned_to="lead_technical_dev",
                created_by="pm_agent",
            ),
            Task(
                project_id=example_project.id,
                title="Write documentation",
                description="Document setup process and usage examples",
                status="todo",
                priority="medium",
                assigned_to="lead_technical_dev",
                created_by="pm_agent",
            ),
            Task(
                project_id=example_project.id,
                title="Add cost tracking visualization",
                description="Create charts/graphs for cost analysis",
                status="todo",
                priority="low",
                created_by="pm_agent",
            ),
            Task(
                project_id=example_project.id,
                title="Test PM Agent with real project",
                description="Validate PM Agent works correctly with actual tasks",
                status="todo",
                priority="high",
                assigned_to="pm_agent",
                created_by="ceo",
                due_date=datetime.utcnow() + timedelta(days=3),
            ),
        ]

        for task in tasks:
            session.add(task)

        session.commit()
        print(f"  ✓ Created {len(tasks)} sample tasks")

        print("\n" + "=" * 60)
        print("SEEDING COMPLETE!")
        print("=" * 60)
        print("\nExample project ready:")
        print(f"  • Project: {example_project.name}")
        print(f"  • Agents: {pm_agent.name}, {lead_dev_agent.name}")
        print(f"  • Tasks: {len(tasks)} tasks created")
        print("\nTry these commands:")
        print("  python -m src.cli.main status 'Example Project'")
        print("  python -m src.cli.main tasks 'Example Project'")
        print("  python -m src.cli.main create 'Example Project' 'My new task'")
        print()

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error during seeding: {e}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    seed_data()
