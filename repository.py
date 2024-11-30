import sqlite3

conn = sqlite3.connect("messages.db")

# Initialize SQLite Database
def init_db():
    cursor = conn.cursor()
    # Create a table to store messages if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY,
        new_filename TEXT UNIQUE,
        download_status TEXT,
        upload_status TEXT,
        content TEXT,
        download_timestamp TEXT,
        upload_timestamp timestamp TEXT
    )
    """)
    conn.commit()
    return conn