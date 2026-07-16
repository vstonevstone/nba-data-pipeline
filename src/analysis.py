import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import logging
from src.database import get_db_connection

logger = logging.getLogger(__name__)


def run_analytical_queries(db_path: str):
    conn = get_db_connection(db_path)

    # ---------------------------------------------------------
    # Q1: Celtics vs Lakers Historical H2H record (Pure SQL)
    # Rationale: Helps understand rivalry performance dynamics.
    # ---------------------------------------------------------
    q1_sql = """
        SELECT 
            SUM(CASE WHEN (g.home_team_id = t_bos.team_id AND g.home_team_wins = 1) OR 
                          (g.visitor_team_id = t_bos.team_id AND g.home_team_wins = 0) THEN 1 ELSE 0 END) as celtics_wins,
            SUM(CASE WHEN (g.home_team_id = t_lal.team_id AND g.home_team_wins = 1) OR 
                          (g.visitor_team_id = t_lal.team_id AND g.home_team_wins = 0) THEN 1 ELSE 0 END) as lakers_wins,
            COUNT(*) as total_games
        FROM games g
        JOIN teams t_bos ON (g.home_team_id = t_bos.team_id OR g.visitor_team_id = t_bos.team_id)
        JOIN teams t_lal ON (g.home_team_id = t_lal.team_id OR g.visitor_team_id = t_lal.team_id)
        WHERE t_bos.abbreviation = 'BOS' AND t_lal.abbreviation = 'LAL'
          AND g.home_team_id != g.visitor_team_id;
    """
    logger.info("Executing Q1: Celtics vs Lakers H2H...")
    q1_df = pd.read_sql_query(q1_sql, conn)
    print("\n" + "=" * 50)
    print("🏀 RIVALRY HISTORICAL SUMMARY: CELTICS vs LAKERS")
    print("=" * 50)
    print(q1_df.to_markdown(index=False))

    # ---------------------------------------------------------
    # Q2: Top 5 Highest Average Home Game Point Differentials (Pure SQL)
    # Rationale: Identifies which arenas provide the strongest home-court advantage.
    # ---------------------------------------------------------
    q2_sql = """
        SELECT 
            t.nickname as team,
            COUNT(g.game_id) as home_games_played,
            ROUND(AVG(g.pts_home), 2) as avg_home_pts,
            ROUND(AVG(g.pts_away), 2) as avg_opponent_pts,
            ROUND(AVG(g.pts_home - g.pts_away), 2) as avg_home_margin
        FROM games g
        JOIN teams t ON g.home_team_id = t.team_id
        GROUP BY g.home_team_id
        HAVING home_games_played > 50
        ORDER BY avg_home_margin DESC
        LIMIT 5;
    """
    logger.info("Executing Q2: Dominant Home Courts...")
    q2_df = pd.read_sql_query(q2_sql, conn)
    print("\n" + "=" * 50)
    print("🏟️ TOP 5 MOST DOMINANT HOME COURTS")
    print("=" * 50)
    print(q2_df.to_markdown(index=False))

    # ---------------------------------------------------------
    # Q3: Historical Scoring Trends (Python + Matplotlib)
    # Rationale: Visualizes how rule and pace changes affect scoring trends over time.
    # ---------------------------------------------------------
    logger.info("Executing Q3: Charting NBA Pace Trajectory...")
    q3_sql = """
        SELECT 
            season,
            ROUND(AVG(pts_home + pts_away), 2) as avg_combined_score,
            ROUND(AVG(pts_home), 2) as avg_home_score,
            ROUND(AVG(pts_away), 2) as avg_away_score
        FROM games
        WHERE season >= 2004 AND pts_home IS NOT NULL AND pts_away IS NOT NULL
        GROUP BY season
        ORDER BY season ASC;
    """
    q3_df = pd.read_sql_query(q3_sql, conn)
    conn.close()

    # Generate Chart Output
    plt.figure(figsize=(10, 6))
    plt.plot(q3_df["season"], q3_df["avg_combined_score"], marker='o', color='#1d428a', linewidth=2.5,
             label="Total Game Score")
    plt.plot(q3_df["season"], q3_df["avg_home_score"], linestyle='--', color='#g96127', label="Home Team Score")

    plt.title("NBA League Scoring Volatility (2004 - Present)", fontsize=14, fontweight='bold')
    plt.xlabel("Season", fontsize=12)
    plt.ylabel("Average Points", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()

    plot_path = "nba_scoring_trends.png"
    plt.savefig(plot_path, dpi=300)
    logger.info(f"Visualized scoring trends exported successfully to: {plot_path}")