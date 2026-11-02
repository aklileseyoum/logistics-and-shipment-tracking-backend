

CREATE TABLE customers (
    id    INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name  TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);


CREATE TABLE locations (
    id    INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name  TEXT NOT NULL,
    city  TEXT NOT NULL,
    state TEXT NOT NULL,
    UNIQUE (name, city, state)
);

CREATE TABLE shipments (
    id                      INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id             INT NOT NULL REFERENCES customers(id),
    origin_location_id      INT NOT NULL REFERENCES locations(id),
    destination_location_id INT NOT NULL REFERENCES locations(id),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (origin_location_id <> destination_location_id)
);

CREATE TABLE packages (
    id               INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    shipment_id      INT NOT NULL REFERENCES shipments(id),
    tracking_id      TEXT NOT NULL UNIQUE,
    current_status   TEXT NOT NULL DEFAULT 'Created'
        CHECK (current_status IN ('Created', 'Picked Up', 'In Transit',
                                  'Out for Delivery', 'Delivered', 'Exception')),
    package_metadata JSONB
);

CREATE TABLE tracking_events (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    package_id      INT NOT NULL REFERENCES packages(id),
    location_id     INT NOT NULL REFERENCES locations(id),
    status          TEXT NOT NULL
        CHECK (status IN ('Created', 'Picked Up', 'In Transit',
                          'Out for Delivery', 'Delivered', 'Exception')),
    event_timestamp TIMESTAMPTZ NOT NULL DEFAULT now()
);
