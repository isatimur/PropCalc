"""
Connection pool management for PropCalc
Implements proper asyncpg connection pooling with health monitoring
"""

import asyncio
import logging
from typing import Any, Dict, Optional
import asyncpg
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class PoolManager:
    """Manages database connection pools with proper lifecycle management"""
    
    def __init__(self):
        self.pools: Dict[str, asyncpg.Pool] = {}
        self._lock = asyncio.Lock()
        self._health_check_interval = 30  # seconds
        self._max_retries = 3
        
    async def create_pool(self, name: str, dsn: str, **kwargs) -> asyncpg.Pool:
        """Create a new connection pool"""
        async with self._lock:
            if name not in self.pools:
                try:
                    # Set default pool settings if not provided
                    pool_kwargs = {
                        'min_size': 5,
                        'max_size': 20,
                        'command_timeout': 60,
                        'server_settings': {
                            'application_name': 'propcalc_backend',
                            'timezone': 'UTC'
                        }
                    }
                    pool_kwargs.update(kwargs)
                    
                    pool = await asyncpg.create_pool(dsn, **pool_kwargs)
                    self.pools[name] = pool
                    logger.info(f"✅ Created connection pool: {name}")
                    
                    # Start health monitoring for this pool
                    asyncio.create_task(self._monitor_pool_health(name, pool))
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create connection pool {name}: {e}")
                    raise
                    
            return self.pools[name]
    
    async def get_pool(self, name: str) -> Optional[asyncpg.Pool]:
        """Get an existing connection pool"""
        return self.pools.get(name)
    
    async def close_pool(self, name: str):
        """Close a specific connection pool"""
        if name in self.pools:
            pool = self.pools[name]
            await pool.close()
            del self.pools[name]
            logger.info(f"✅ Closed connection pool: {name}")
    
    async def close_all_pools(self):
        """Close all connection pools"""
        for name in list(self.pools.keys()):
            await self.close_pool(name)
        logger.info("✅ All connection pools closed")
    
    async def _monitor_pool_health(self, name: str, pool: asyncpg.Pool):
        """Monitor pool health and reconnect if needed"""
        while name in self.pools:
            try:
                # Test pool health
                async with pool.acquire() as conn:
                    await conn.execute('SELECT 1')
                
                await asyncio.sleep(self._health_check_interval)
                
            except Exception as e:
                logger.warning(f"⚠️ Pool {name} health check failed: {e}")
                # Attempt to recreate the pool
                await self._recreate_pool(name, pool)
                break
    
    async def _recreate_pool(self, name: str, old_pool: asyncpg.Pool):
        """Recreate a failed connection pool"""
        try:
            # Close old pool
            await old_pool.close()
            
            # Get DSN from environment (simplified - in production, store DSNs)
            dsn = f"postgresql://{self._get_db_config()}"
            
            # Create new pool
            new_pool = await asyncpg.create_pool(
                dsn,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            self.pools[name] = new_pool
            logger.info(f"✅ Recreated connection pool: {name}")
            
            # Restart health monitoring
            asyncio.create_task(self._monitor_pool_health(name, new_pool))
            
        except Exception as e:
            logger.error(f"❌ Failed to recreate pool {name}: {e}")
    
    def _get_db_config(self) -> str:
        """Get database configuration from environment"""
        import os
        user = os.getenv('POSTGRES_USER', 'vantage_user')
        password = os.getenv('POSTGRES_PASSWORD', 'vantage_password')
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        db = os.getenv('POSTGRES_DB', 'vantage_ai')
        return f"{user}:{password}@{host}:{port}/{db}"
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get comprehensive connection pool statistics"""
        stats = {
            "total_pools": len(self.pools),
            "pools": {}
        }
        
        for name, pool in self.pools.items():
            try:
                pool_stats = {
                    "min_size": pool.get_min_size(),
                    "max_size": pool.get_max_size(),
                    "size": pool.get_size(),
                    "free_size": pool.get_free_size(),
                    "active_connections": pool.get_size() - pool.get_free_size()
                }
                stats["pools"][name] = pool_stats
            except Exception as e:
                logger.warning(f"Could not get stats for pool {name}: {e}")
                stats["pools"][name] = {"error": str(e)}
        
        return stats
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get all connection pool statistics (alias for get_pool_stats)"""
        return self.get_pool_stats()
    
    @asynccontextmanager
    async def get_connection(self, pool_name: str = "default"):
        """Get a connection from the specified pool with automatic release"""
        pool = await self.get_pool(pool_name)
        if not pool:
            raise ValueError(f"Pool {pool_name} not found")
        
        async with pool.acquire() as conn:
            yield conn

# Global pool manager instance
_pool_manager: Optional[PoolManager] = None

def init_connection_pools():
    """Initialize connection pools"""
    global _pool_manager
    _pool_manager = PoolManager()
    logger.info("✅ Connection pool manager initialized")

def get_pool_manager() -> PoolManager:
    """Get pool manager instance"""
    if _pool_manager is None:
        raise RuntimeError("Connection pools not initialized. Call init_connection_pools() first.")
    return _pool_manager

async def close_connection_pools():
    """Close all connection pools"""
    if _pool_manager:
        await _pool_manager.close_all_pools()
