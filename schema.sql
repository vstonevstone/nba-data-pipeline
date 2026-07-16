-- Drop tables to support clean, repeatable environment rebuilds
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS teams;

-- 1. Dimension Table: Teams
CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY,
    abbreviation TEXT NOT NULL,
    nickname TEXT NOT NULL,
    city TEXT NOT NULL,
    arena TEXT,
    arena_capacity INTEGER
);

-- 2. Fact Table: Games
CREATE TABLE games (
    game_id INTEGER PRIMARY KEY,
    game_date TEXT NOT NULL, -- Format: YYYY-MM-DD
    season INTEGER NOT NULL,
    home_team_id INTEGER NOT NULL,
    visitor_team_id INTEGER NOT NULL,
    pts_home INTEGER,
    pts_away INTEGER,
    home_team_wins INTEGER NOT NULL CHECK(home_team_wins IN (0, 1)),
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (visitor_team_id) REFERENCES teams(team_id),
    UNIQUE(game_date, home_team_id, visitor_team_id) -- Ensures Idempotency
);

-- 3. Optimization Indexes for analytical queries
CREATE INDEX idx_games_date ON games(game_date);
CREATE INDEX idx_games_season ON games(season);
CREATE INDEX idx_games_home_team ON games(home_team_id);
CREATE INDEX idx_games_visitor_team ON games(visitor_team_id);