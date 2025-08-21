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
            # Try to use the new pool manager if available
            try:
                from ...core.performance.connection_pool import get_pool_manager
                pool_manager = get_pool_manager()
                dsn = f"postgresql://{self.connection_params['user']}:{self.connection_params['password']}@{self.connection_params['host']}:{self.connection_params['port']}/{self.connection_params['database']}"
                self.pool = await pool_manager.create_pool("default", dsn)
                logger.info("✅ PostgreSQL connection pool initialized via pool manager")
            except (ImportError, RuntimeError):
                # Fallback to direct pool creation
                self.pool = await asyncpg.create_pool(
                    **self.connection_params,
                    min_size=5,
                    max_size=20,
                    command_timeout=60
                )
                logger.info("✅ PostgreSQL connection pool initialized directly")
        except Exception as e:
            logger.error(f"❌ Failed to initialize PostgreSQL connection pool: {e}")
            raise

    async def close_connection_pool(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("✅ PostgreSQL connection pool closed")

    async def get_connection(self):
        """Get a connection from the pool"""
        if not self.pool:
            await self.init_connection_pool()
        return await self.pool.acquire()

    async def release_connection(self, connection):
        """Release a connection back to the pool"""
        if self.pool:
            await self.pool.release(connection)

    async def execute_query(self, query: str, *args) -> Any:
        """Execute a query and return results"""
        connection = await self.get_connection()
        try:
            result = await connection.fetch(query, *args)
            return result
        finally:
            await self.release_connection(connection)

    async def execute_command(self, command: str, *args) -> str:
        """Execute a command and return status"""
        connection = await self.get_connection()
        try:
            result = await connection.execute(command, *args)
            return result
        finally:
            await self.release_connection(connection)

    async def health_check(self) -> bool:
        """Check database health"""
        try:
            result = await self.execute_query("SELECT 1")
            return len(result) > 0
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def get_top_performers(self, limit: int = 5) -> list[dict[str, Any]]:
        """Get top performing properties/developers"""
        try:
            query = """
                SELECT 
                    developer_name,
                    location,
                    property_type,
                    COUNT(*) as transaction_count,
                    AVG(price_aed) as avg_price,
                    SUM(price_aed) as total_volume
                FROM dld_transactions
                WHERE developer_name IS NOT NULL 
                AND developer_name != ''
                GROUP BY developer_name, location, property_type
                ORDER BY total_volume DESC
                LIMIT $1
            """
            result = await self.execute_query(query, limit)
            return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error getting top performers: {e}")
            return []
    
    async def get_project_by_id(self, project_id: int) -> dict[str, Any] | None:
        """Get project by ID"""
        try:
            query = """
                SELECT 
                    id,
                    name,
                    developer_name,
                    location,
                    property_type,
                    price_aed,
                    area_sqft,
                    completion_date,
                    developer_score,
                    location_score,
                    project_quality_score,
                    market_sentiment_score
                FROM dld_transactions
                WHERE id = $1
                LIMIT 1
            """
            result = await self.execute_query(query, project_id)
            if result:
                return dict(result[0])
            return None
        except Exception as e:
            logger.error(f"Error getting project by ID: {e}")
            return None

# Global instance
_db_instance = None

async def get_db_instance() -> PostgresDB:
    """Get the global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = PostgresDB()
        await _db_instance.init_connection_pool()
    return _db_instance

async def get_db_connection():
    """Get a database connection from the pool"""
    db = await get_db_instance()
    return await db.get_connection()

async def close_db():
    """Close the database connection pool"""
    global _db_instance
    if _db_instance:
        await _db_instance.close_connection_pool()
        _db_instance = None
