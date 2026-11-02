"""Pytest fixtures: a throw-away package with two locations, cleaned up after."""

import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import pytest

from logistic_and_shipment_tracking_backend.db import (
    get_connection,
    release_connection,
)


def run_sql(sql: str, params: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    """Run one statement in its own transaction; return rows (if any)."""
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall() if cur.description else []
    finally:
        release_connection(conn)


@dataclass
class World:
    package_id: int
    tracking_id: str
    loc_a: int
    loc_b: int


@pytest.fixture
def world() -> Iterator[World]:
    tag = uuid.uuid4().hex[:8]
    cust = run_sql(
        "INSERT INTO customers (name, email) VALUES (%s, %s) RETURNING id",
        ("Test User", f"{tag}@test.local"),
    )[0][0]
    locs = [
        run_sql(
            "INSERT INTO locations (name, city, state) VALUES (%s, %s, %s) "
            "RETURNING id",
            (f"Test {name} {tag}", city, "TS"),
        )[0][0]
        for name, city in (("A", "Alpha"), ("B", "Beta"))
    ]
    ship = run_sql(
        "INSERT INTO shipments (customer_id, origin_location_id, "
        "destination_location_id) VALUES (%s, %s, %s) RETURNING id",
        (cust, locs[0], locs[1]),
    )[0][0]
    tracking_id = f"TEST-{tag}"
    pkg = run_sql(
        "INSERT INTO packages (shipment_id, tracking_id) VALUES (%s, %s) RETURNING id",
        (ship, tracking_id),
    )[0][0]

    yield World(pkg, tracking_id, locs[0], locs[1])

    run_sql("DELETE FROM tracking_events WHERE package_id = %s", (pkg,))
    run_sql("DELETE FROM packages WHERE id = %s", (pkg,))
    run_sql("DELETE FROM shipments WHERE id = %s", (ship,))
    run_sql("DELETE FROM locations WHERE id = ANY(%s)", (locs,))
    run_sql("DELETE FROM customers WHERE id = %s", (cust,))
