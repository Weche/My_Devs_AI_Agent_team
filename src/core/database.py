"""Database models and SQLAlchemy configuration"""

import os
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

#  ============================================================================
#  DATABASE MODELS
#  ============================================================================


class Project(Base):
    """Project model - represents a project (e.g., Binance Trading, Cookie Store)"""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    status = Column(
        String(50),
        nullable=False,
        default="active",
        # Check constraint: status in ('active', 'paused', 'completed', 'archived')
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    budget = Column(Float, nullable=True)
    priority = Column(Integer, nullable=False, default=5)  # 1-10 scale

    # Relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    agent_assignments = relationship(
        "AgentProjectAssignment", back_populates="project", cascade="all, delete-orphan"
    )
    interactions = relationship(
        "Interaction", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"


class Task(Base):
    """Task model - represents a task within a project"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        String(50),
        nullable=False,
        default="todo",
        # Check: status in ('todo', 'in_progress', 'blocked', 'review', 'done')
    )
    priority = Column(
        String(50),
        nullable=False,
        default="medium",
        # Check: priority in ('critical', 'high', 'medium', 'low')
    )
    assigned_to = Column(String(100), nullable=True)  # Agent role name
    created_by = Column(String(100), nullable=True)  # Who created (CEO, Agent, etc.)
    due_date = Column(DateTime, nullable=True)
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at = Column(DateTime, nullable=True)
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    subtasks = relationship("Task", backref="parent_task", remote_side=[id])

    # Indexes
    __table_args__ = (
        Index("idx_tasks_project_status", "project_id", "status"),
        Index("idx_tasks_assigned_status", "assigned_to", "status"),
        Index("idx_tasks_due_date", "due_date"),
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title[:30]}...', status='{self.status}')>"


class Agent(Base):
    """Agent model - represents an AI agent (PM, CEO, Dev, etc.)"""

    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    role = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    backstory = Column(Text, nullable=True)
    goal = Column(Text, nullable=True)
    tools = Column(Text, nullable=True)  # JSON array as string
    model = Column(String(50), nullable=False, default="gpt-4o-mini")
    temperature = Column(Float, nullable=False, default=0.7)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    project_assignments = relationship(
        "AgentProjectAssignment", back_populates="agent", cascade="all, delete-orphan"
    )
    interactions = relationship(
        "Interaction", back_populates="agent", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', role='{self.role}')>"


class AgentProjectAssignment(Base):
    """Assignment of agents to projects"""

    __tablename__ = "agent_project_assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="project_assignments")
    project = relationship("Project", back_populates="agent_assignments")

    # Unique constraint
    __table_args__ = (Index("idx_unique_agent_project", "agent_id", "project_id", unique=True),)

    def __repr__(self):
        return f"<AgentProjectAssignment(agent_id={self.agent_id}, project_id={self.project_id})>"


class Interaction(Base):
    """Interaction log - tracks every interaction with agents"""

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    interaction_type = Column(
        String(50),
        nullable=False,
        # Check: interaction_type in ('telegram', 'cli', 'system', 'agent')
    )
    user_id = Column(String(100), nullable=True)  # Telegram user ID or 'system'
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    command = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    agent = relationship("Agent", back_populates="interactions")
    project = relationship("Project", back_populates="interactions")

    # Index
    __table_args__ = (Index("idx_interactions_created_at", "created_at"),)

    def __repr__(self):
        return f"<Interaction(id={self.id}, type='{self.interaction_type}', command='{self.command}')>"


#  ============================================================================
#  DATABASE ENGINE AND SESSION
#  ============================================================================


def get_database_url() -> str:
    """Get database URL from environment or use default"""
    return os.getenv("DATABASE_URL", "sqlite:///data/database/pm_system.db")


def create_db_engine(url: Optional[str] = None, echo: bool = False):
    """Create SQLAlchemy engine"""
    db_url = url or get_database_url()

    # Enable WAL mode for SQLite (better concurrency)
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args = {
            "check_same_thread": False,
            "timeout": 30,
        }

    engine = create_engine(db_url, echo=echo, connect_args=connect_args)

    # Enable WAL mode
    if db_url.startswith("sqlite"):
        with engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
            conn.commit()

    return engine


def get_session_factory(engine):
    """Create session factory"""
    return sessionmaker(bind=engine, expire_on_commit=False)


def get_session(engine=None) -> Session:
    """Get database session"""
    if engine is None:
        engine = create_db_engine()
    SessionFactory = get_session_factory(engine)
    return SessionFactory()


#  ============================================================================
#  HELPER FUNCTIONS
#  ============================================================================


def create_all_tables(engine=None):
    """Create all database tables"""
    if engine is None:
        engine = create_db_engine()
    Base.metadata.create_all(engine)


def drop_all_tables(engine=None):
    """Drop all database tables (use with caution!)"""
    if engine is None:
        engine = create_db_engine()
    Base.metadata.drop_all(engine)


def get_project_by_name(session: Session, name: str) -> Optional[Project]:
    """Get project by name"""
    return session.query(Project).filter(Project.name == name).first()


def get_project_by_id(session: Session, project_id: int) -> Optional[Project]:
    """Get project by ID"""
    return session.query(Project).filter(Project.id == project_id).first()


def get_tasks_by_project(
    session: Session,
    project_id: int,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
) -> list[Task]:
    """Get tasks for a project with optional filters"""
    query = session.query(Task).filter(Task.project_id == project_id)

    if status:
        query = query.filter(Task.status == status)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    return query.order_by(Task.created_at.desc()).all()


def get_agent_by_name(session: Session, name: str) -> Optional[Agent]:
    """Get agent by name"""
    return session.query(Agent).filter(Agent.name == name).first()


def get_active_projects(session: Session) -> list[Project]:
    """Get all active projects"""
    return session.query(Project).filter(Project.status == "active").all()


def get_project_task_counts(session: Session, project_id: int) -> dict:
    """Get count of tasks by status for a project"""
    tasks = session.query(Task.status, func.count(Task.id)).filter(
        Task.project_id == project_id
    ).group_by(Task.status).all()

    return {status: count for status, count in tasks}


# Import func for aggregations
from sqlalchemy import func
