"""Shared env loading and demo-mode detection for the financial data layer."""

from __future__ import annotations

import os
from pathlib import Path

_env_loaded = False


def ensure_env() -> None:
    """Load backend/.env once so providers work regardless of import order."""
    global _env_loaded
    if _env_loaded:
        return
    try:
        from dotenv import load_dotenv

        env_path = Path(__file__).resolve().parent.parent / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=True)
    except ImportError:
        pass
    _env_loaded = True


def is_demo_mode() -> bool:
    """
    Institutional reference data is enabled when:
      - INSTITUTIONAL_DEMO_MODE=1, or
      - ENVIRONMENT is development/local (default), unless explicitly disabled.
    """
    ensure_env()
    flag = os.getenv("INSTITUTIONAL_DEMO_MODE", "").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return False
    if flag in ("1", "true", "yes", "on"):
        return True
    env = os.getenv("ENVIRONMENT", "development").strip().lower()
    return env in ("development", "dev", "local", "test")
