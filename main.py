import os
import argparse
import logging
from src.database import init_db
from src.ingest import download_file, ingest_teams, ingest_games, TEAMS_URL, GAMES_URL
from src.analysis import run_analytical_queries

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("main")


def main():
    parser = argparse.ArgumentParser(description="NBA Historical Games ETL & Analysis Pipeline")
    parser.add_argument("--db", default="data/nba_history.db", help="Target SQLite DB path")
    parser.add_argument("--teams-csv", default="data/teams.csv", help="Teams CSV Path")
    parser.add_argument("--games-csv", default="data/games.csv", help="Games CSV Path")
    parser.add_argument("--force-reset", action="store_true", help="Force rebuild DB")

    args = parser.parse_args()

    # Automatically create the database parent folder if it doesn't exist
    db_dir = os.path.dirname(args.db)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    # Initialize Directories and DB
    db_exists = os.path.exists(args.db)
    if args.force_reset or not db_exists:
        init_db(args.db)

    # Download raw assets
    local_teams = download_file(TEAMS_URL, args.teams_csv)
    local_games = download_file(GAMES_URL, args.games_csv)

    # Ingest data
    ingest_teams(local_teams, args.db)
    ingest_games(local_games, args.db)

    # Run analytical SQL and visualization routines
    run_analytical_queries(args.db)
    logger.info("ETL and analysis finished successfully!")


if __name__ == "__main__":
    main()