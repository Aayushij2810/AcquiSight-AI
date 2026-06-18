"""
PostgreSQL connection and ORM setup via SQLAlchemy 2.x.
"""

import os
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://acquisight_user:change_me@localhost:5432/acquisight",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ScreenedDeal(Base):
    """Persisted record of every screened deal."""
    __tablename__ = "screened_deals"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(200), nullable=False, index=True)
    industry = Column(String(100), nullable=False)
    country = Column(String(100))
    revenue = Column(Float)
    ebitda = Column(Float)
    growth_rate = Column(Float)
    debt = Column(Float)
    cash = Column(Float)
    ebitda_margin = Column(Float)
    enterprise_value = Column(Float)
    investment_score = Column(Integer)
    risk_score = Column(Integer)
    recommendation = Column(String(100))
    scores_json = Column(JSON)       # stores DimensionScores as dict
    comps_json = Column(JSON)        # stores CompsResult as dict
    memo_text = Column(Text, nullable=True)
    screened_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def get_db():
    """FastAPI dependency — yield a DB session then close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables if they do not exist yet."""
    Base.metadata.create_all(bind=engine)
