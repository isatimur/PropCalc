"""
Database infrastructure module
"""

from .postgres_db import PostgresDB, close_connection_pool, init_connection_pool
from .postgres_db import get_db as get_postgres_db
from .simple_db import SimpleDB
from .simple_db import get_db as get_simple_db
from .simple_db import init_db as init_simple_db

__all__ = [
    'SimpleDB',
    'PostgresDB',
    'init_simple_db',
    'init_connection_pool',
    'close_connection_pool',
    'get_simple_db',
    'get_postgres_db'
]
