"""
Runtime data-layer status — honest provider connection states for Settings UI.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from financial_data.config import is_demo_mode

# Updated on each successful gateway fetch.
_runtime: dict = {
    "active_provider_id": None,
    "active_provider_label": None,
    "last_successful_refresh": None,
    "last_query": None,
    "last_ticker": None,
    "provider_last_success": {},  # provider_id -> ISO timestamp
}


def record_successful_fetch(
    provider_id: str,
    provider_label: str,
    query: str,
    ticker: str,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    _runtime["active_provider_id"] = provider_id
    _runtime["active_provider_label"] = provider_label
    _runtime["last_successful_refresh"] = now
    _runtime["last_query"] = query
    _runtime["last_ticker"] = ticker
    _runtime["provider_last_success"][provider_id] = now


def _connection_state(provider_id: str, has_credentials: bool, is_public: bool) -> str:
    """
    connected  — actively usable (public feeds or credentialed enterprise)
    available  — enterprise connector ready, awaiting credentials
    not_connected — not configured / unavailable
    """
    if has_credentials:
        return "connected"
    if is_public and provider_id == "yahoo":
        return "connected"
    if provider_id in ("bloomberg", "factset", "capital_iq"):
        return "available"
    return "not_connected"


def _badge_label(state: str) -> str:
    return {
        "connected": "Connected",
        "available": "Available",
        "not_connected": "Not Connected",
    }.get(state, "Not Connected")


def _subtitle(provider_id: str, state: str) -> str:
    if state == "connected":
        if provider_id == "yahoo":
            return "Public market data feed active"
        if provider_id == "fmp":
            return "API credentials verified"
        return "Enterprise API credentials verified"
    if state == "available":
        return "Enterprise connector available — not connected"
    if provider_id == "fmp":
        return "Set FMP_API_KEY to enable"
    return "Awaiting configuration"


def build_provider_connections(providers) -> list[dict]:
    """Build honest per-provider connection status."""
    rows = []
    for p in providers:
        creds = p.has_credentials()
        is_public = p.provider_id in ("yahoo", "fmp")
        is_enterprise = p.provider_id in ("bloomberg", "factset", "capital_iq")
        state = _connection_state(p.provider_id, creds, is_public)

        rows.append({
            "provider_id": p.provider_id,
            "provider_label": p.provider_label,
            "priority": p.priority,
            "quality_weight": p.provider_quality_weight,
            "category": "enterprise" if is_enterprise else "public",
            "connection_state": state,
            "badge": _badge_label(state),
            "subtitle": _subtitle(p.provider_id, state),
            "has_credentials": creds,
            "credential_env_var": getattr(p, "credential_env_var", None),
            "last_successful_refresh": _runtime["provider_last_success"].get(p.provider_id),
        })
    return rows


def get_data_layer_status(providers) -> dict:
    """Full data-layer dashboard payload for Settings."""
    connections = build_provider_connections(providers)
    active_id = _runtime.get("active_provider_id")

    fallback = []
    for p in connections:
        if p["provider_id"] == active_id:
            continue
        if p["connection_state"] == "connected":
            fallback.append({
                "provider_id": p["provider_id"],
                "provider_label": p["provider_label"],
                "status": "ready",
            })
        elif p["connection_state"] == "available":
            fallback.append({
                "provider_id": p["provider_id"],
                "provider_label": p["provider_label"],
                "status": "awaiting_credentials",
            })
        else:
            fallback.append({
                "provider_id": p["provider_id"],
                "provider_label": p["provider_label"],
                "status": "not_connected",
            })

    return {
        "active_provider": {
            "provider_id": _runtime.get("active_provider_id"),
            "provider_label": _runtime.get("active_provider_label") or "None — no fetch yet",
        },
        "last_successful_refresh": _runtime.get("last_successful_refresh"),
        "last_query": _runtime.get("last_query"),
        "last_ticker": _runtime.get("last_ticker"),
        "demo_mode_enabled": is_demo_mode(),
        "demo_mode_note": (
            "Demo mode is on — enterprise connectors require API credentials to serve data. "
            "Public feeds (Yahoo Finance, FMP) supply live market data."
            if is_demo_mode()
            else None
        ),
        "fallback_providers": fallback,
        "providers": connections,
    }
