"""Transactional tracking logic (PostgreSQL)."""

from typing import Any

from .db import get_connection, release_connection


def process_tracking_scan(package_id: int, location_id: int, status: str) -> str:
    """Record one scan atomically and return the package's tracking_id."""
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tracking_events (package_id, location_id, status)"
                " VALUES (%s, %s, %s)",
                (package_id, location_id, status),
            )
            cur.execute(
                "UPDATE packages SET current_status = %s WHERE id = %s"
                " RETURNING tracking_id",
                (status, package_id),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"unknown package {package_id}")
            return str(row[0])
    finally:
        release_connection(conn)


def get_package_history(package_id: int) -> list[tuple[Any, ...]]:
    """Return (status, city, event_timestamp, since_previous), oldest first."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                WITH history AS (
                    SELECT te.status, l.city, te.event_timestamp
                    FROM tracking_events te
                    JOIN locations l ON l.id = te.location_id
                    WHERE te.package_id = %s
                )
                SELECT status, city, event_timestamp,
                       event_timestamp
                         - LAG(event_timestamp) OVER (ORDER BY event_timestamp)
                         AS since_previous
                FROM history
                ORDER BY event_timestamp
                """,
                (package_id,),
            )
            return cur.fetchall()
    finally:
        release_connection(conn)


def get_location_label(location_id: int) -> str:
    """Return "City, ST" for a location (the format the Redis value needs)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT city, state FROM locations WHERE id = %s", (location_id,)
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"unknown location {location_id}")
            return f"{row[0]}, {row[1]}"
    finally:
        release_connection(conn)
