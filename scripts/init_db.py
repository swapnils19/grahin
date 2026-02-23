#!/usr/bin/env python3
"""
Initialize database with tables and create initial migration
"""
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from alembic.config import Config
from alembic import command
from app.core.database import engine
from app.models import Base


def create_database():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def create_initial_migration():
    """Create initial Alembic migration"""
    print("Creating initial migration...")
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
    print("Initial migration created successfully!")


if __name__ == "__main__":
    create_database()
    create_initial_migration()
