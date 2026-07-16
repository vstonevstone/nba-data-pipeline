import os
import csv
import urllib.request
import logging
from typing import Generator, List, Tuple
from src.database import get_db_connection

logger = logging.getLogger(__name__)

# Open, direct download mirrors of NBA games and teams datasets
TEAMS_URL = "https://huggingface.co/datasets/hamzas/nba-games/resolve/main/teams.csv"
GAMES_URL = "https://huggingface.co/datasets/hamzas/nba-games/resolve/main/games.csv"


def download_file(url: str, target_path: str) -> str:
    """Streams data from the web to local storage to prevent memory spikes."""
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if os.path.exists(target_path):
        logger.info(f"Local asset found at {target_path}. Skipping download.")
        return target_path

    logger.info(f"Downloading: {url}...")
    with urllib.request.urlopen(url) as response, open(target_path, 'wb') as out_file:
        chunk_size = 1024 * 1024  # 1MB chunk buffers
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
    logger.info(f"Successfully saved to {target_path}")
    return target_path


def ingest_teams(csv_path: str, db_path: str):
    """Loads the Teams dimension table from downloaded CSV."""
    logger.info("Ingesting Teams dataset...")
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        teams_data = []
        for row in reader:
            try:
                cap = int(row["ARENACAPACITY"]) if row["ARENACAPACITY"] else None
                teams_data.append((
                    int(row["TEAM_ID"]),
                    row["ABBREVIATION"],
                    row["NICKNAME"],
                    row["CITY"],
                    row["ARENA"],
                    cap
                ))
            except ValueError as e:
                logger.warning(f"Skipping malformed team row: {row}. Error: {e}")

        cursor.executemany(
            """
            INSERT OR IGNORE INTO teams (team_id, abbreviation, nickname, city, arena, arena_capacity)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            teams_data
        )
        conn.commit()
    conn.close()
    logger.info("Teams ingestion finished.")


def parse_games_stream(file_path: str, batch_size: int = 10000) -> Generator[List[Tuple], None, None]:
    """Yields parsed game records in memory-safe batches."""
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            try:
                game_date = row["GAME_DATE_EST"].split(" ")[0]  # Standardizes date string
                pts_h = int(float(row["PTS_home"])) if row["PTS_home"] else None
                pts_a = int(float(row["PTS_away"])) if row["PTS_away"] else None

                batch.append((
                    int(row["GAME_ID"]),
                    game_date,
                    int(row["SEASON"]),
                    int(row["HOME_TEAM_ID"]),
                    int(row["VISITOR_TEAM_ID"]),
                    pts_h,
                    pts_a,
                    int(row["HOME_TEAM_WINS"])
                ))
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
            except (ValueError, KeyError):
                continue
        if batch:
            yield batch


def ingest_games(csv_path: str, db_path: str, batch_size: int = 10000):
    """Batches inserts into Games Table with idempotent UPSERT handling."""
    logger.info("Ingesting Games dataset...")
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    total = 0
    try:
        for batch in parse_games_stream(csv_path, batch_size):
            cursor.executemany(
                """
                INSERT OR IGNORE INTO games (
                    game_id, game_date, season, home_team_id, visitor_team_id, pts_home, pts_away, home_team_wins
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                batch
            )
            conn.commit()
            total += len(batch)
            logger.info(f"Ingested {total} games...")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to ingest games: {e}")
        raise e
    finally:
        conn.close()