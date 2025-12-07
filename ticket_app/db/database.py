import sqlite3
from . import models  # pour les dataclasses si besoin
from ..config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            urgency TEXT,
            deadline TEXT,
            theme TEXT,
            archived INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try:
        cur.execute("ALTER TABLE tickets ADD COLUMN archived INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        # colonne déjà présente
        pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS postits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            x INTEGER,
            y INTEGER,
            width INTEGER,
            height INTEGER,
            color TEXT,
            tags TEXT DEFAULT '',
            order_index INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try:
        cur.execute("ALTER TABLE postits ADD COLUMN tags TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        # colonne déjà présente
        pass
    try:
        cur.execute("ALTER TABLE postits ADD COLUMN order_index INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        # colonne déjà présente
        pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS themes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            color TEXT,
            x INTEGER DEFAULT 0,
            y INTEGER DEFAULT 0,
            width INTEGER DEFAULT 0,
            height INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
