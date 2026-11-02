
INSERT INTO customers (name, email) VALUES
    ('Amina Uwase', 'amina@example.com'),
    ('Brian Otieno', 'brian@example.com');

INSERT INTO locations (name, city, state) VALUES
    ('Kigali Central Hub',     'Kigali',  'RW'),
    ('Nairobi Warehouse',      'Nairobi', 'KE'),
    ('Mombasa Port Depot',     'Mombasa', 'KE'),
    ('Kampala Sorting Center', 'Kampala', 'UG');

INSERT INTO shipments (customer_id, origin_location_id, destination_location_id) VALUES
    (1, 1, 3),
    (2, 2, 1);

INSERT INTO packages (shipment_id, tracking_id, current_status, package_metadata) VALUES
    (1, 'PKG-1001', 'In Transit', '{"fragile": true,  "requires_signature": true}'),
    (1, 'PKG-1002', 'Picked Up',  '{"fragile": false, "requires_signature": false}'),
    (2, 'PKG-2001', 'Delivered',  '{"fragile": false, "requires_signature": true}');


INSERT INTO tracking_events (package_id, location_id, status, event_timestamp) VALUES
    (1, 1, 'Created',          '2026-10-30 08:00:00+00'),
    (1, 1, 'Picked Up',        '2026-10-30 09:15:00+00'),
    (1, 2, 'In Transit',       '2026-10-31 14:40:00+00'),
    (2, 1, 'Created',          '2026-10-30 08:05:00+00'),
    (2, 1, 'Picked Up',        '2026-10-30 09:20:00+00'),
    (3, 2, 'Created',          '2026-10-28 10:00:00+00'),
    (3, 2, 'Picked Up',        '2026-10-28 11:00:00+00'),
    (3, 1, 'Out for Delivery', '2026-10-29 07:30:00+00'),
    (3, 1, 'Delivered',        '2026-10-29 11:10:00+00');
