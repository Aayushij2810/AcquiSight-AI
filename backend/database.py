"""Database configuration (PostgreSQL via SQLAlchemy).

For production usage:
  1. Set DATABASE_URL in your .env file.
  2. Run `alembic upgrade head` to create tables.
  3. Replace the in-memory _history list in main.py with SQLAlchemy session calls.
"""
from __future__ import annotations

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://acquisight:acquisight@localhost:5432/acquisight")

engine       = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class DealRecord(Base):
    """Persisted screening result."""
    __tablename__ = "deal_records"

    id               = Column(Integer, primary_key=True, index=True)
    company_name     = Column(String, index=True)
    industry         = Column(String)
    investment_score = Column(Float)
    risk_score       = Column(Float)
    recommendation   = Column(String)
    enterprise_value = Column(Float)
    raw_result       = Column(JSON)
    created_at       = Column(DateTime, default=datetime.utcnow)


def create_tables():
    """Create all tables (call on startup in production)."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yield a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
