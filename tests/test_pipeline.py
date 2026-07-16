import os
import pytest
from src.database import get_db_connection, init_db
from src.ingest import ingest_teams


@pytest.fixture
def test_db(tmp_path):
    """Generates an ephemeral SQLite file for database assertions."""
    db_file = tmp_path / "test_nba.db"
    schema_file = tmp_path / "schema.sql"

    ddl = """
    CREATE TABLE teams (
        team_id INTEGER PRIMARY KEY,
        abbreviation TEXT,
        nickname TEXT,
        city TEXT,
        arena TEXT,
        arena_capacity INTEGER
    );
    """
    with open(schema_file, "w") as f:
        f.write(ddl)

    init_db(str(db_file), schema_path=str(schema_file))
    return str(db_file)


@pytest.fixture
def mock_teams_csv(tmp_path):
    """Creates a small mock data file simulating our Socrata CSV entries."""
    csv_file = tmp_path / "teams_mock.csv"
    with open(csv_file, "w", newline="") as f:
        f.write("LEAGUE_ID,TEAM_ID,MIN_YEAR,MAX_YEAR,ABBREVIATION,NICKNAME,YEARFOUNDED,CITY,ARENA,ARENACAPACITY\n")
        f.write("00,1610612737,1949,2026,ATL,Hawks,1949,Atlanta,State Farm Arena,18600\n")
    return str(csv_file)


def test_teams_ingestion(mock_teams_csv, test_db):
    """Ensures parser isolates and saves fields cleanly with standard data types."""
    ingest_teams(mock_teams_csv, test_db)
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams WHERE abbreviation='ATL';")
    row = cursor.fetchone()

    assert row is not None
    assert row["nickname"] == "Hawks"
    assert row["arena_capacity"] == 18600
    conn.close()