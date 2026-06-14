import sqlite3

DB_PATH = "productivity.db"
MIN_SESSION_DURATION = 2  

# initialize database and create sessions table
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time REAL,
            end_time REAL,
            state TEXT
        )
    """)
    conn.commit()
    return conn

# log session into database
def log_session(conn, start_time, end_time, state):
    duration = end_time - start_time
    if duration < MIN_SESSION_DURATION:
        return
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (start_time, end_time, state) VALUES (?, ?, ?)",
        (start_time, end_time, state)
    )
    conn.commit()
    print(f"Logged: {state} for {duration:.1f}s")