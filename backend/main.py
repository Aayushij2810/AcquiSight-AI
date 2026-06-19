"""AcquiSight AI — FastAPI entry-point."""
from __future__ import annotations

import logging
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_tables
from routers.history import router as history_router
from routers.memo import router as memo_router
from routers.screen import router as screen_router

load_dotenv()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AcquiSight AI",
    description="AI-Powered Private Equity Deal Screening API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(screen_router, prefix="/api", tags=["screen"])
app.include_router(memo_router, prefix="/api", tags=["memo"])
app.include_router(history_router, prefix="/api", tags=["history"])


@app.on_event("startup")
def on_startup() -> None:
    try:
        create_tables()
    except Exception as exc:
        logger.warning("Could not initialize database tables: %s", exc)


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
