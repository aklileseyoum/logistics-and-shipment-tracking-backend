-- Load AFTER measuring the query without it (see sql/benchmark.sql).
CREATE INDEX idx_tracking_events_package_time
    ON tracking_events (package_id, event_timestamp);
