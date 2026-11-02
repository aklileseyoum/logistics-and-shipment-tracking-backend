-- Measures the history lookup before/after the composite index.
-- Everything runs in a transaction that is ROLLED BACK: your data is untouched.
-- Run:  psql -U app -d logistics -f benchmark.sql
BEGIN;

-- 2000 fake packages with 100 scans each = 200,000 events
INSERT INTO packages (shipment_id, tracking_id)
    SELECT 1, 'BULK-' || g FROM generate_series(1, 2000) g;
INSERT INTO tracking_events (package_id, location_id, status, event_timestamp)
    SELECT p.id, 1 + (s % 4), 'In Transit',
           timestamptz '2026-01-01' + (s || ' minutes')::interval
    FROM packages p, generate_series(1, 100) s
    WHERE p.tracking_id LIKE 'BULK-%';
ANALYZE tracking_events;

SELECT min(id) AS pid FROM packages WHERE tracking_id LIKE 'BULK-%' \gset

DROP INDEX IF EXISTS idx_tracking_events_package_time;

\echo === BEFORE the index ===
EXPLAIN ANALYZE SELECT * FROM tracking_events
WHERE package_id = :pid ORDER BY event_timestamp;

CREATE INDEX idx_tracking_events_package_time
    ON tracking_events (package_id, event_timestamp);
ANALYZE tracking_events;

\echo === AFTER the index ===
EXPLAIN ANALYZE SELECT * FROM tracking_events
WHERE package_id = :pid ORDER BY event_timestamp;

ROLLBACK;
