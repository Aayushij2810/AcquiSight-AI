"""
AcquiSight AI — FastAPI Backend
AI-Powered Private Equity Deal Screening Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from database import init_db
from routers import screen, memo, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: initialise the database tables."""
    init_db()
    yield


app = FastAPI(
    title="AcquiSight AI",
    description="AI-Powered Private Equity Deal Screening & Investment Intelligence API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the React dev server and production origin
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(screen.router, prefix="/api", tags=["Deal Screening"])
app.include_router(memo.router, prefix="/api", tags=["Investment Memo"])
app.include_router(history.router, prefix="/api", tags=["Deal History"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "AcquiSight AI Backend"}
