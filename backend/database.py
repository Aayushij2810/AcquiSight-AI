"""Database configuration (PostgreSQL via SQLAlchemy)."""
from __future__ import annotations

import os
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://acquisight:acquisight@localhost:5432/acquisight",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class ScreenedDeal(Base):
    """Persisted screening result."""

    __tablename__ = "screened_deals"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    industry = Column(String)
    country = Column(String)
    revenue = Column(Float)
    ebitda = Column(Float)
    growth_rate = Column(Float)
    debt = Column(Float)
    cash = Column(Float)
    ebitda_margin = Column(Float)
    enterprise_value = Column(Float)
    investment_score = Column(Integer)
    risk_score = Column(Integer)
    recommendation = Column(String)
    scores_json = Column(JSON)
    comps_json = Column(JSON)
    screened_at = Column(DateTime, default=datetime.utcnow)


class InvestmentOpportunity(Base):
    """Portfolio pipeline opportunity."""

    __tablename__ = "investment_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    industry = Column(String, index=True)
    revenue = Column(Float)
    ebitda = Column(Float)
    growth_rate = Column(Float)
    debt = Column(Float)
    cash = Column(Float)
    investment_score = Column(Integer)
    risk_score = Column(Integer)
    recommendation = Column(String)
    enterprise_value = Column(Float)
    priority_score = Column(Float, index=True)
    date_added = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String, default="Screening", index=True)
    notes = Column(Text, default="")
    watchlist = Column(Boolean, default=False, index=True)
    ic_decision = Column(String, default="Pending")
    screen_result_json = Column(JSON)
    memo_json = Column(JSON, nullable=True)


def create_tables() -> None:
    """Create all tables (call on startup in production)."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: yield a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
