"""Redis, MongoDB and the full scan pipeline (needs docker compose up)."""

from logistic_and_shipment_tracking_backend.cache import (
    get_package_status,
    set_package_status,
)
from logistic_and_shipment_tracking_backend.scan_log import (
    get_scan_logs,
    log_raw_scan,
)
from logistic_and_shipment_tracking_backend.service import handle_scan

from .conftest import World, run_sql


def test_redis_stores_latest_status() -> None:
    set_package_status("TEST-CACHE", "In Transit", "Kigali, RW")

    assert get_package_status("TEST-CACHE") == {
        "status": "In Transit",
        "location": "Kigali, RW",
    }
    assert get_package_status("TEST-NEVER-SEEN") is None


def test_mongo_keeps_raw_scans(world: World) -> None:
    log_raw_scan("scanner-7", world.package_id, world.loc_a, "Picked Up")

    logs = get_scan_logs(world.package_id)

    assert len(logs) == 1
    assert logs[0]["scanner_id"] == "scanner-7"
    assert logs[0]["status"] == "Picked Up"


def test_handle_scan_updates_all_three_stores(world: World) -> None:
    tracking_id = handle_scan("scanner-1", world.package_id, world.loc_a, "In Transit")

    rows = run_sql(
        "SELECT current_status FROM packages WHERE id = %s", (world.package_id,)
    )
    assert rows[0][0] == "In Transit"
    assert get_package_status(tracking_id) == {
        "status": "In Transit",
        "location": "Alpha, TS",
    }
    assert len(get_scan_logs(world.package_id)) == 1
