"""
Simple SQLite database implementation for development/testing
"""

import logging
import sqlite3
from typing import Any

logger = logging.getLogger(__name__)

class SimpleDB:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = None
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.create_tables()
            logger.info("SimpleDB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SimpleDB: {e}")
            raise

    def create_tables(self):
        """Create database tables"""
        cursor = self.connection.cursor()

        # Create basic tables for development
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                developer TEXT,
                location TEXT,
                price REAL,
                vantage_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS developers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                performance_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER,
                price REAL,
                date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.connection.commit()

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def get_projects(self, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        """Get projects with pagination"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM projects
            ORDER BY vantage_score DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]

    def get_developers(self, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        """Get developers with pagination"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM developers
            ORDER BY performance_score DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]

# Global instance
_db_instance = None

def init_db():
    """Initialize the global database instance"""
    global _db_instance
    _db_instance = SimpleDB()
    return _db_instance

def get_db() -> SimpleDB:
    """Get the global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SimpleDB()
    return _db_instance
