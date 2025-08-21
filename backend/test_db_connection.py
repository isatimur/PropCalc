#!/usr/bin/env python3
"""
Test database connection
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

async def test_connection():
    """Test database connection"""
    
    # Database connection parameters
    host = os.getenv('POSTGRES_HOST', 'postgres')
    port = os.getenv('POSTGRES_PORT', '5432')
    user = os.getenv('POSTGRES_USER', 'vantage_user')
    password = os.getenv('POSTGRES_PASSWORD', 'vantage_password')
    database = os.getenv('POSTGRES_DB', 'vantage_ai')
    
    # Create connection URL
    database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
    
    print(f"Testing connection to: {database_url}")
    
    try:
        # Create async engine
        engine = create_async_engine(database_url, echo=True)
        
        # Test connection
        async with engine.begin() as conn:
            from sqlalchemy import text
            result = await conn.execute(text("SELECT COUNT(*) FROM dld_transactions"))
            count = result.scalar()
            print(f"✅ Connection successful! Found {count} transactions")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
