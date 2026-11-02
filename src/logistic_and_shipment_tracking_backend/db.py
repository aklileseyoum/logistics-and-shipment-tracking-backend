"""PostgreSQL connection pool (settings match docker-compose.yml)."""

import os
from typing import Any

from psycopg2 import pool
from psycopg2.extensions import connection

_pool: Any = pool.SimpleConnectionPool(
    1,
    5,
    host=os.getenv("PGHOST", "localhost"),
    port=int(os.getenv("PGPORT", "5434")),
    user=os.getenv("PGUSER", "app"),
    password=os.getenv("PGPASSWORD", "app_password"),
    dbname=os.getenv("PGDATABASE", "logistics"),
)


def get_connection() -> connection:
    """Borrow a connection from the pool. Always give it back."""
    return _pool.getconn()


def release_connection(conn: connection) -> None:
    """Return a borrowed connection to the pool."""
    _pool.putconn(conn)


def close_pool() -> None:
    """Close every connection (call once when the program ends)."""
    _pool.closeall()
