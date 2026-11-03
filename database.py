import sqlite3
from datetime import datetime

DB_NAME = "events.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = connect_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            camera_id TEXT,
            event_time TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_event(event_type, camera_id):

    conn = connect_db()

    conn.execute("""
        INSERT INTO events
        (event_type, camera_id, event_time)
        VALUES (?, ?, ?)
    """, (
        event_type,
        camera_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

def get_events():

    conn = connect_db()

    rows = conn.execute("""
        SELECT id, event_type, camera_id, event_time
        FROM events ORDER BY id DESC LIMIT 100
    """).fetchall()

    conn.close()

    return rows
