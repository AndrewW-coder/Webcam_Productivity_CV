import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import DB_PATH

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# connection to db
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# gets all sessions
@app.get("/sessions")
def get_sessions():
    """Return all raw sessions."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY start_time DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# gets summary of all sessions
@app.get("/summary")
def get_summary():
    """Return total seconds spent in each state."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT state, SUM(end_time - start_time) as total_seconds
        FROM sessions
        GROUP BY state
    """).fetchall()
    conn.close()
    return {row["state"]: round(row["total_seconds"], 1) for row in rows}


# gets daily summary of all sessions
@app.get("/summary/daily")
def get_daily_summary():
    """Return per-day breakdown of time in each state."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            DATE(start_time, 'unixepoch', 'localtime') as date,
            state,
            SUM(end_time - start_time) as total_seconds
        FROM sessions
        GROUP BY date, state
        ORDER BY date DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]