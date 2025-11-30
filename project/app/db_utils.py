"""
===========================================================
 app/db_utils.py
-----------------------------------------------------------
Handles all SQLite database operations for the KittyLit app.

Includes:
- DB connection helper
- Creating tables on startup
- Insert / Query / Update / Delete functions
- Popularity update
- Logging for traceability

Author: Ammu
Updated: 2025-11-28
===========================================================
"""

import sqlite3
import logging
from typing import List, Dict, Optional
from datetime import datetime

# ------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s][db_utils] %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Database Path (SQLite)
# ------------------------------------------------------------
DB_PATH = 'data/kittylit_books.db'


# ============================================================
# 1. DB INITIALIZATION
# ============================================================
def init_db():
    """
    Create the 'books' table if it does not already exist.
    This schema supports:
        - UI filters (genre, language, age_group, publication_year)
        - Agent decisions (source, cached_at)
        - Governance (timestamps)
        - Analytics (popularity)
    """

    logger.debug("Initializing SQLite database...")

    create_table_query = """
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        -- Core information
        title TEXT NOT NULL,
        author TEXT,
        description TEXT,
        isbn TEXT UNIQUE,

        -- UI & Agent Filters
        genre TEXT,
        language TEXT,
        age_group INTEGER,
        publication_year TEXT,

        -- Extra Metadata
        thumbnail_url TEXT,
        source TEXT,
        popularity INTEGER DEFAULT 0,

        -- Operational Tracking
        cached_at TEXT,
        agent_notes TEXT,

        -- Governance Timestamps
        created_at TEXT,
        updated_at TEXT
    );
    """

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        conn.close()

        logger.debug("Database initialized successfully (tables ensured)")

    except Exception as e:
        logger.error(f"DB initialization failed: {e}")
        raise


# ============================================================
# 2. CONNECTION HANDLER
# ============================================================
def get_connection() -> sqlite3.Connection:
    """Open a new SQLite connection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        logger.debug("Opened DB connection successfully")
        return conn
    except Exception as e:
        logger.error(f"Error opening DB connection: {e}")
        raise


# ============================================================
# 3. INSERT BOOK
# ============================================================
def insert_book(book: Dict) -> bool:
    """
    Insert a book into the database.
    Uses INSERT OR IGNORE to avoid duplicate ISBNs.
    """

    query = '''
        INSERT OR IGNORE INTO books 
        (title, author, description, isbn,
         genre, language, age_group, publication_year,
         thumbnail_url, source, popularity,
         cached_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    try:
        now = datetime.utcnow().isoformat()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (
            book['title'],
            book.get('author'),
            book.get('description'),
            book['isbn'],

            book.get('genre'),
            book.get('language'),
            book.get('age_group'),
            book.get('publication_year'),

            book.get('thumbnail_url'),
            book.get('source'),
            book.get('popularity', 0),

            now,   # cached_at
            now,   # created_at
            now    # updated_at
        ))

        conn.commit()
        inserted = cursor.rowcount > 0
        conn.close()

        logger.debug(f"Inserted book ISBN={book.get('isbn')} : {inserted}")
        return inserted

    except Exception as e:
        logger.error(f"Error inserting book ISBN={book.get('isbn')}: {e}")
        return False


# ============================================================
# 4. QUERY BOOKS (supports optional filters)
# ============================================================
def query_books(filter_by: Optional[Dict] = None) -> List[Dict]:
    """Fetch books optionally filtered by fields."""
    query = "SELECT * FROM books"
    params = []

    if filter_by:
        clauses = []
        for key, value in filter_by.items():
            if value:
                clauses.append(f"{key} LIKE ?")
                params.append(f"%{value}%")
        if clauses:
            query += " WHERE " + " AND ".join(clauses)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        books = [dict(row) for row in rows]
        logger.debug(f"Queried books with filters {filter_by} → {len(books)} found")
        return books

    except Exception as e:
        logger.error(f"Error querying books with filters {filter_by}: {e}")
        return []


# ============================================================
# 5. UPDATE BOOK
# ============================================================
def update_book(isbn: str, update_fields: Dict) -> bool:
    """Update fields for a book identified by ISBN."""

    if not update_fields:
        logger.warning(f"No fields provided for update of ISBN={isbn}")
        return False

    update_fields["updated_at"] = datetime.utcnow().isoformat()

    set_clause = ", ".join(f"{k} = ?" for k in update_fields.keys())
    params = list(update_fields.values()) + [isbn]

    query = f"UPDATE books SET {set_clause} WHERE isbn = ?"

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        logger.debug(f"Updated book ISBN={isbn} → {success}")
        return success

    except Exception as e:
        logger.error(f"Error updating ISBN={isbn}: {e}")
        return False


# ============================================================
# 6. DELETE BOOK
# ============================================================
def delete_book(isbn: str) -> bool:
    """Delete a book entry by ISBN."""

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE isbn = ?", (isbn,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()

        logger.debug(f"Deleted ISBN={isbn} → {success}")
        return success

    except Exception as e:
        logger.error(f"Error deleting ISBN={isbn}: {e}")
        return False


# ============================================================
# 7. UPDATE POPULARITY
# ============================================================
def update_book_popularity(isbn: str, increment: int):
    """Increment popularity counter for a book."""

    query = """
        UPDATE books
        SET popularity = COALESCE(popularity, 0) + ?
        WHERE isbn = ?
    """

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (increment, isbn))
        conn.commit()
        conn.close()

        logger.debug(f"Popularity +{increment} for ISBN={isbn}")

    except Exception as e:
        logger.error(f"Error updating popularity for ISBN={isbn}: {e}")
