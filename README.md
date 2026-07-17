## 🐳 Running with Docker

This route runs the pipeline in an isolated container, eliminating the need to manually install Python or local package dependencies on your host machine.

### Prerequisite: Prepare Docker
1.  **Install:** If not already installed, download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for your OS.
2.  **Important - Start Docker:** Open the Docker Desktop application and ensure the engine status icon in the bottom-left corner is **green** (Engine Running).
3.  **Verify:** In your terminal, run `docker --version` to confirm your system recognizes the command.

### Step-by-Step Execution
From your terminal, execute the following commands in order:

```bash
# 1. Clone the project repository to your local machine
git clone https://github.com/vstonevstone/nba-data-pipeline.git

cd nba-data-pipeline

# 2. Build the lightweight container image
docker build -t nba-pipeline .

# 3. Run the pipeline (Triggers schema setup, data streaming, ingestion, and SQL analytics)
docker run --name nba-runner nba-pipeline

# 4. Copy the compiled SQLite database and trend chart back to your local machine
docker cp nba-runner:/app/data/nba_history.db ./nba_history.db
docker cp nba-runner:/app/nba_scoring_trends.png ./nba_scoring_trends.png

# 5. Run the automated test suite inside the container
docker run --entrypoint pytest nba-pipeline -v

# 6. Clean up the stopped container instance
docker rm nba-runner
```
### How to Verify and Inspect Results
Once the pipeline completes its run, you can inspect the outputs across three layers:

1. Terminal Logs (CLI Tables)
The script prints beautifully formatted markdown tables directly to your terminal. Look closely at your terminal output to find:

🏀 Celtics vs. Lakers Historical Rivalry: Head-to-head match records, overall wins, and win ratios.

🏟️ Top 5 Most Dominant Home Courts: A live leaderboard displaying franchises with the highest average home-game point differentials (minimum 50 games played).

2. Visual Trend Analysis
Open the generated nba_scoring_trends.png image file in the project's root folder. This high-definition Matplotlib plot visualizes the evolution of average home and away team scoring trends spanning from 2004 to the present.

3. Querying the SQLite Database
The compiled database is exported to nba_history.db (copied out of Docker) or data/nba_history.db (for local runs). Since native sqlite3 command-line tools are not installed by default on Windows systems, use these highly portable Python one-liners to query your database directly from your terminal:
````bash
# Verify the total number of games ingested (Expected: ~26,305+ records)
python -c "import sqlite3; conn = sqlite3.connect('nba_history.db'); print('🏀 Total Games Ingested:', conn.execute('SELECT COUNT(*) FROM games').fetchone()[0])"

# Preview the first 5 teams in the dimension table
python -c "import sqlite3; conn = sqlite3.connect('nba_history.db'); print('📋 First 5 Teams:'); [print(row) for row in conn.execute('SELECT * FROM teams LIMIT 5').fetchall()]" 
````
