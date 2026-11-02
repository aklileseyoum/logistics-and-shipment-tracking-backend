"""Tests for the transactional scan processing and the history query."""

from datetime import timedelta

import psycopg2
import pytest

from logistic_and_shipment_tracking_backend.tracking import (
    get_package_history,
    process_tracking_scan,
)

from .conftest import World, run_sql


def count_events(package_id: int) -> int:
    rows = run_sql(
        "SELECT count(*) FROM tracking_events WHERE package_id = %s", (package_id,)
    )
    return int(rows[0][0])


def current_status(package_id: int) -> str:
    rows = run_sql("SELECT current_status FROM packages WHERE id = %s", (package_id,))
    return str(rows[0][0])


def test_scan_saves_event_and_updates_status(world: World) -> None:
    tracking_id = process_tracking_scan(world.package_id, world.loc_a, "In Transit")

    assert tracking_id == world.tracking_id
    assert count_events(world.package_id) == 1
    assert current_status(world.package_id) == "In Transit"


def test_scan_with_invalid_status_saves_nothing(world: World) -> None:
    with pytest.raises((ValueError, psycopg2.Error)):
        process_tracking_scan(world.package_id, world.loc_a, "Teleported")

    assert count_events(world.package_id) == 0
    assert current_status(world.package_id) == "Created"


def test_scan_of_unknown_package_saves_nothing(world: World) -> None:
    with pytest.raises((ValueError, psycopg2.Error)):
        process_tracking_scan(-1, world.loc_a, "In Transit")

    rows = run_sql(
        "SELECT count(*) FROM tracking_events WHERE location_id = %s", (world.loc_a,)
    )
    assert rows[0][0] == 0


def test_history_computes_time_between_scans(world: World) -> None:
    for status, loc, ts in (
        ("Created", world.loc_a, "2026-01-01 08:00:00+00"),
        ("Picked Up", world.loc_a, "2026-01-01 10:00:00+00"),
        ("In Transit", world.loc_b, "2026-01-01 10:30:00+00"),
    ):
        run_sql(
            "INSERT INTO tracking_events (package_id, location_id, status, "
            "event_timestamp) VALUES (%s, %s, %s, %s)",
            (world.package_id, loc, status, ts),
        )

    rows = get_package_history(world.package_id)

    assert [r[0] for r in rows] == ["Created", "Picked Up", "In Transit"]
    assert [r[1] for r in rows] == ["Alpha", "Alpha", "Beta"]
    assert [r[3] for r in rows] == [
        None,
        timedelta(hours=2),
        timedelta(minutes=30),
    ]
