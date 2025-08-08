"""
PostgreSQL database implementation for production
"""

import logging
import os
from datetime import datetime
from typing import Any

import asyncpg

logger = logging.getLogger(__name__)

class PostgresDB:
    def __init__(self):
        self.pool = None
        self.connection_params = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'user': os.getenv('POSTGRES_USER', 'vantage_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'vantage_password'),
            'database': os.getenv('POSTGRES_DB', 'vantage_ai')
        }

    async def init_connection_pool(self):
        """Initialize the connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                **self.connection_params,
                min_size=5,
                max_size=20
            )
            logger.info("PostgreSQL connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise

    async def close_connection_pool(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")

    async def get_projects(self, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        """Get projects with pagination"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM projects
                ORDER BY vantage_score DESC
                LIMIT $1 OFFSET $2
            """, limit, offset)

            return [dict(row) for row in rows]

    async def get_developers(self, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        """Get developers with pagination"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM developers
                ORDER BY performance_score DESC
                LIMIT $1 OFFSET $2
            """, limit, offset)

            return [dict(row) for row in rows]

    async def get_market_overview(self) -> dict[str, Any]:
        """Get market overview statistics"""
        async with self.pool.acquire() as conn:
            # Get basic market stats
            total_projects = await conn.fetchval("SELECT COUNT(*) FROM projects")
            avg_price = await conn.fetchval("SELECT AVG(price) FROM projects")
            avg_score = await conn.fetchval("SELECT AVG(vantage_score) FROM projects")

            return {
                "total_projects": total_projects,
                "average_price": float(avg_price) if avg_price else 0,
                "average_vantage_score": float(avg_score) if avg_score else 0,
                "last_updated": datetime.now().isoformat()
            }

# Global instance
_db_instance = None

async def init_connection_pool():
    """Initialize the global database connection pool"""
    global _db_instance
    _db_instance = PostgresDB()
    await _db_instance.init_connection_pool()
    return _db_instance

async def close_connection_pool():
    """Close the global database connection pool"""
    global _db_instance
    if _db_instance:
        await _db_instance.close_connection_pool()

def get_db() -> PostgresDB:
    """Get the global database instance"""
    global _db_instance
    return _db_instance

def get_db_pool():
    """Get the database connection pool for direct access"""
    global _db_instance
    if _db_instance and _db_instance.pool:
        return _db_instance.pool
    else:
        raise RuntimeError("Database connection pool not initialized. Call init_connection_pool() first.")
