import sqlite3
import time
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "leaderboard.db")

_leaderboard_cache = None
_leaderboard_cache_time = 0.0
_LEADERBOARD_TTL = 2.0

def init_database():
    """Initialize the SQLite leaderboard database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS scores
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      wave INTEGER NOT NULL,
                      score INTEGER NOT NULL,
                      date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] Could not init database: {e}")

def get_leaderboard_data(limit=5):
    """Fetch top leaderboard entries with TTL cache."""
    global _leaderboard_cache, _leaderboard_cache_time
    now = time.time()
    if _leaderboard_cache is not None and (now - _leaderboard_cache_time) < _LEADERBOARD_TTL:
        return _leaderboard_cache
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name, wave FROM scores ORDER BY wave DESC, score DESC, date ASC LIMIT ?", (limit,))
        data = c.fetchall()
        conn.close()
        _leaderboard_cache = data
        _leaderboard_cache_time = now
        return data
    except Exception as e:
        print(f"[DB ERROR] Could not fetch leaderboard: {e}")
        return []

def save_score(name, wave, score):
    """Save a new player score to the database."""
    global _leaderboard_cache
    _leaderboard_cache = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO scores (name, wave, score) 
                     VALUES (?, ?, ?)''', (name, wave, score))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] Could not save score: {e}")

# Ensure database is initialized on import
init_database()
