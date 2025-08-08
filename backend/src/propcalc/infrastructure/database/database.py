"""
Database configuration and session management for PropCalc
Modern SQLAlchemy 2.0 setup with async support
"""

import os
from typing import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from ...config.settings import get_settings
from .models import Base

settings = get_settings()

# Database URLs
DATABASE_URL = settings.database_url
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Engine configurations
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=settings.debug,
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=settings.debug,
)

# Session factories
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Metadata
metadata = MetaData()

def get_db() -> Generator[Session, None, None]:
    """Get synchronous database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get asynchronous database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Get database session with context manager"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def get_async_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with context manager"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def create_tables() -> None:
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

async def create_tables_async() -> None:
    """Create all tables in the database (async)"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def drop_tables() -> None:
    """Drop all tables in the database"""
    Base.metadata.drop_all(bind=engine)

async def drop_tables_async() -> None:
    """Drop all tables in the database (async)"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception:
        return False

async def check_database_connection_async() -> bool:
    """Check if database connection is working (async)"""
    try:
        async with async_engine.connect() as connection:
            await connection.execute("SELECT 1")
        return True
    except Exception:
        return False

# Database health check
def get_database_info() -> dict:
    """Get database information and statistics"""
    try:
        with engine.connect() as connection:
            # Get table counts
            result = connection.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_rows,
                    n_dead_tup as dead_rows
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)
            
            tables_info = [dict(row._mapping) for row in result]
            
            # Get database size
            size_result = connection.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
            """)
            db_size = size_result.fetchone()[0]
            
            return {
                "status": "healthy",
                "database_size": db_size,
                "tables": tables_info,
                "total_tables": len(tables_info)
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Migration helpers
def get_current_revision() -> str:
    """Get current database revision"""
    try:
        from alembic import command
        from alembic.config import Config
        
        alembic_cfg = Config("alembic.ini")
        with engine.connect() as connection:
            result = connection.execute("SELECT version_num FROM alembic_version")
            return result.fetchone()[0] if result.rowcount > 0 else "None"
    except Exception:
        return "Unknown"

async def get_current_revision_async() -> str:
    """Get current database revision (async)"""
    try:
        async with async_engine.connect() as connection:
            result = await connection.execute("SELECT version_num FROM alembic_version")
            row = await result.fetchone()
            return row[0] if row else "None"
    except Exception:
        return "Unknown" 