"""MongoDB: raw scanner event logs, kept for auditing."""

import os
from datetime import UTC, datetime
from typing import Any

from pymongo import MongoClient

_client: Any = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27018"))
_logs: Any = _client["logistics"]["scan_logs"]


def log_raw_scan(
    scanner_id: str,
    package_id: int,
    location_id: int,
    status: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Store the scan exactly as received and return the log id as text."""
    result = _logs.insert_one(
        {
            "scanner_id": scanner_id,
            "package_id": package_id,
            "location_id": location_id,
            "status": status,
            "metadata": metadata or {},
            "received_at": datetime.now(UTC),
        }
    )
    return str(result.inserted_id)


def get_scan_logs(package_id: int) -> list[dict[str, Any]]:
    """All raw scans of a package, oldest first (without Mongo's _id)."""
    return list(
        _logs.find({"package_id": package_id}, {"_id": 0}).sort("received_at", 1)
    )
