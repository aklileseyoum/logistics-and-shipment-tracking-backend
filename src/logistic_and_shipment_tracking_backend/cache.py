"""Redis: the latest status of each package, for fast reads."""

import json
import os
from typing import Any

import redis

_client: Any = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6380")),
    decode_responses=True,
)


def status_key(tracking_id: str) -> str:
    """Key format required by the brief: package:<tracking_id>:status."""
    return f"package:{tracking_id}:status"


def set_package_status(tracking_id: str, status: str, location: str) -> None:
    """Overwrite the latest status. No expiry: PostgreSQL stays the source of truth."""
    value = json.dumps({"status": status, "location": location})
    _client.set(status_key(tracking_id), value)


def get_package_status(tracking_id: str) -> dict[str, str] | None:
    """Return {"status": ..., "location": ...}, or None if never cached."""
    raw = _client.get(status_key(tracking_id))
    return json.loads(raw) if raw else None
