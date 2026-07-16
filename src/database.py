import os
import sqlite3
import logging

logger = logging.getLogger(__name__)


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Returns a SQLite connection with production-grade configurations."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db(db_path: str, schema_path: str = "schema.sql"):
    """Executes the DDL schema to build target SQLite tables."""
    logger.info(f"Initializing database at {db_path}...")
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at {schema_path}")

    with get_db_connection(db_path) as conn:
        with open(schema_path, "r") as f:
            conn.executescript(f.read())

    logger.info("Database schema and indexes built successfully.")