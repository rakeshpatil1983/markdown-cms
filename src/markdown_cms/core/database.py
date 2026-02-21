"""Database initialization and management."""

import os
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import get_config
from .models import Base

# Global session maker
_SessionLocal: Optional[sessionmaker] = None
_engine: Optional[Engine] = None


def get_database_url() -> str:
    """Get database URL from config or environment."""
    # Check environment variable first
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # Use config path
    config = get_config()
    db_path = config.project_path / "cms.db"

    # Ensure database directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return f"sqlite:///{db_path}"


def get_engine() -> Engine:
    """Get or create database engine."""
    global _engine

    if _engine is None:
        database_url = get_database_url()

        # SQLite-specific settings
        if database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}

            # For in-memory databases, use StaticPool to keep the database alive
            if ":memory:" in database_url:
                _engine = create_engine(
                    database_url,
                    connect_args=connect_args,
                    poolclass=StaticPool,
                    echo=False,
                )
            else:
                _engine = create_engine(
                    database_url,
                    connect_args=connect_args,
                    echo=False,
                )

            # Enable foreign keys for SQLite
            @event.listens_for(_engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        else:
            _engine = create_engine(database_url, echo=False)

    return _engine


def get_session_maker() -> sessionmaker:
    """Get or create session maker."""
    global _SessionLocal

    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )

    return _SessionLocal


def get_db() -> Session:
    """
    Get a database session.

    Usage:
        db = get_db()
        try:
            # Use db session
            user = db.query(User).first()
        finally:
            db.close()

    Or use as context manager:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    SessionLocal = get_session_maker()
    return SessionLocal()


class get_db_context:
    """Context manager for database sessions."""

    def __enter__(self) -> Session:
        """Enter context and return session."""
        self.db = get_db()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and close session."""
        if exc_type is not None:
            self.db.rollback()
        self.db.close()


def init_db():
    """Initialize database - create all tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print(f"[+] Database initialized at: {get_database_url()}")


def drop_db():
    """Drop all tables - USE WITH CAUTION!"""
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    print("[+] Database tables dropped")


def reset_db():
    """Reset database - drop and recreate all tables."""
    drop_db()
    init_db()
    print("[+] Database reset complete")


def seed_db():
    """Seed database with initial data (no default users - setup on first access)."""

    from .models import DataSource, User, UserRole

    with get_db_context() as db:
        # Check if any admin user exists
        admin_exists = db.query(User).filter_by(role=UserRole.ADMIN).first()

        if not admin_exists:
            print("[*] No admin user found. First login will require setup.")
            print("[*] Visit /admin to create the initial admin account.")
        else:
            print("[+] Admin user already exists")

        # Create sample data sources
        sample_sources = [
            {
                "name": "users_all",
                "description": "Get all users",
                "function_path": "markdown_cms.core.queries.get_all_users",
                "requires_auth": True,
                "allowed_roles": "admin",
            },
            {
                "name": "users_active",
                "description": "Get active users only",
                "function_path": "markdown_cms.core.queries.get_active_users",
                "requires_auth": True,
                "allowed_roles": "admin,editor",
            },
            {
                "name": "content_published",
                "description": "Get all published content",
                "function_path": "markdown_cms.core.queries.get_published_content",
                "requires_auth": False,
                "allowed_roles": "",
            },
        ]

        for source_data in sample_sources:
            existing = db.query(DataSource).filter_by(name=source_data["name"]).first()
            if not existing:
                source = DataSource(**source_data)
                db.add(source)
                print(f"[+] Created data source: {source_data['name']}")

        db.commit()
        print("[+] Database seeded successfully")


def check_db_exists() -> bool:
    """Check if database file exists."""
    db_url = get_database_url()
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        return Path(db_path).exists()
    return True  # For non-SQLite, assume exists


def get_db_info() -> dict:
    """Get database information."""
    db_url = get_database_url()
    engine = get_engine()

    info = {
        "url": db_url,
        "driver": engine.driver,
        "exists": check_db_exists(),
    }

    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        path_obj = Path(db_path)
        if path_obj.exists():
            info["size"] = path_obj.stat().st_size
            info["path"] = str(path_obj.absolute())

    return info
