"""Create new projects in the system"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import (
    get_session,
    Project,
    Agent,
    AgentProjectAssignment,
)


def create_projects(projects_data):
    """
    Create multiple projects and assign agents

    Args:
        projects_data: List of dicts with project info
    """
    session = get_session()

    print("\n" + "=" * 60)
    print("CREATING NEW PROJECTS")
    print("=" * 60)

    try:
        # Get PM Agent and Lead Dev Agent
        print("\n[1/3] Loading agents...")
        pm_agent = session.query(Agent).filter(Agent.name == "pm_agent").first()
        lead_dev_agent = (
            session.query(Agent).filter(Agent.name == "lead_technical_dev").first()
        )

        if not pm_agent or not lead_dev_agent:
            print("[ERROR] Required agents not found in database!")
            print("Please run: python scripts/seed_data.py first")
            sys.exit(1)

        print(f"  [OK] Found agents: {pm_agent.name}, {lead_dev_agent.name}")

        # Create projects
        print(f"\n[2/3] Creating {len(projects_data)} projects...")

        created_projects = []

        for project_data in projects_data:
            project = Project(
                name=project_data["name"],
                description=project_data.get("description", ""),
                status=project_data.get("status", "active"),
                priority=project_data.get("priority", 5),
                budget=project_data.get("budget"),
            )
            session.add(project)
            session.commit()
            session.refresh(project)

            print(f"  [OK] Created project: {project.name} (ID: {project.id})")
            created_projects.append(project)

        # Assign agents to all projects
        print(f"\n[3/3] Assigning agents to projects...")

        for project in created_projects:
            # Assign PM Agent
            pm_assignment = AgentProjectAssignment(
                agent_id=pm_agent.id, project_id=project.id
            )
            session.add(pm_assignment)

            # Assign Lead Dev Agent
            dev_assignment = AgentProjectAssignment(
                agent_id=lead_dev_agent.id, project_id=project.id
            )
            session.add(dev_assignment)

            print(f"  [OK] Assigned agents to: {project.name}")

        session.commit()

        # Create agent context directories
        print("\nCreating agent context directories...")
        base_path = Path(__file__).parent.parent / "data" / "agent_context"

        for agent_name in ["pm_agent", "lead_technical_dev"]:
            for project in created_projects:
                # Convert project name to safe directory name
                project_dir = project.name.lower().replace(" ", "_").replace("-", "_")
                dir_path = base_path / agent_name / project_dir
                dir_path.mkdir(parents=True, exist_ok=True)

        print("  [OK] Created context directories")

        print("\n" + "=" * 60)
        print("PROJECT CREATION COMPLETE!")
        print("=" * 60)

        print(f"\nCreated {len(created_projects)} new projects:")
        for project in created_projects:
            print(f"  • {project.name} (Priority: {project.priority}, Status: {project.status})")

        print("\nNext steps:")
        print("  1. View all projects: python -m src.cli.main projects")
        print("  2. Create tasks: python -m src.cli.main create '<Project Name>' 'Task title'")
        print("  3. Get status: python -m src.cli.main status '<Project Name>'")
        print()

    except Exception as e:
        session.rollback()
        print(f"\n[ERROR] Error during project creation: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    # Define the 3 new projects
    new_projects = [
        {
            "name": "Yohga - init",
            "description": "Yohga initialization and setup project",
            "status": "active",
            "priority": 6,  # Slightly higher than default
            "budget": None,
        },
        {
            "name": "Veggies list",
            "description": "Vegetable inventory and tracking system",
            "status": "active",
            "priority": 5,
            "budget": None,
        },
        {
            "name": "Reporting Analytics Dashboards",
            "description": "Analytics and reporting dashboard system for business insights",
            "status": "active",
            "priority": 7,  # Higher priority for analytics
            "budget": None,
        },
    ]

    create_projects(new_projects)
