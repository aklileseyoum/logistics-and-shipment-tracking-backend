"""One incoming scan: audit log -> PostgreSQL transaction -> Redis."""

from .cache import set_package_status
from .scan_log import log_raw_scan
from .tracking import get_location_label, process_tracking_scan


def handle_scan(scanner_id: str, package_id: int, location_id: int, status: str) -> str:
    """Process a scan from a warehouse/driver and return the tracking_id."""
    # 1. MongoDB first: the audit log must keep even scans that later fail.
    log_raw_scan(scanner_id, package_id, location_id, status)
    # 2. PostgreSQL: one atomic transaction (event + current status).
    tracking_id = process_tracking_scan(package_id, location_id, status)
    # 3. Redis LAST: only after the commit, so the cache never shows a status
    #    that PostgreSQL rolled back.
    set_package_status(tracking_id, status, get_location_label(location_id))
    return tracking_id
