"""Initialize database schema and create necessary directories"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import create_db_engine, create_all_tables, Base


def create_directories():
    """Create necessary data directories"""
    directories = [
        "data",
        "data/database",
        "data/agent_context",
        "data/agent_context/ceo_agent",
        "data/agent_context/pm_agent",
        "data/agent_context/lead_technical_dev",
        "data/logs",
        "data/logs/costs",
    ]

    base_path = Path(__file__).parent.parent
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created directory: {dir_path}")


def initialize_database():
    """Initialize database schema"""
    print("\n" + "=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)

    # Create directories
    print("\n[Step 1/3] Creating data directories...")
    create_directories()

    # Create database engine
    print("\n[Step 2/3] Connecting to database...")
    engine = create_db_engine(echo=False)
    print(f"[OK] Connected to database: {engine.url}")

    # Create all tables
    print("\n[Step 3/3] Creating database schema...")
    create_all_tables(engine)

    # Verify tables created
    from sqlalchemy import inspect

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"\n[OK] Created {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")

    print("\n" + "=" * 60)
    print("DATABASE INITIALIZATION COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Copy .env.example to .env")
    print("  2. Add your OpenAI API key to .env")
    print("  3. Run: python scripts/seed_data.py")
    print("  4. Start using CLI: python -m src.cli.main")
    print()


if __name__ == "__main__":
    try:
        initialize_database()
    except Exception as e:
        print(f"\n[ERROR] Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
