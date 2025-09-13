"""
Database connection and initialization for RealVibe Site Copilot
"""

from supabase import create_client, Client
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import asyncpg
import logging

logger = logging.getLogger(__name__)

# Supabase client
supabase: Client = None

# SQLAlchemy setup
engine = None
SessionLocal = None
Base = declarative_base()


async def init_db():
    """Initialize database connections"""
    global supabase, engine, SessionLocal
    
    try:
        # Initialize Supabase client
        if settings.supabase_url and settings.supabase_key:
            supabase = create_client(settings.supabase_url, settings.supabase_key)
            logger.info("Supabase client initialized")
        
        # Initialize SQLAlchemy engine for direct SQL operations
        if settings.database_url:
            engine = create_engine(settings.database_url)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            logger.info("SQLAlchemy engine initialized")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_supabase() -> Client:
    """Get Supabase client instance"""
    if supabase is None:
        raise RuntimeError("Supabase client not initialized")
    return supabase


def get_db():
    """Get database session"""
    if SessionLocal is None:
        raise RuntimeError("Database session not initialized")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def execute_migration(migration_file: str):
    """Execute a SQL migration file"""
    try:
        with open(migration_file, 'r') as f:
            sql_content = f.read()
        
        # Execute using asyncpg for better PostgreSQL support
        conn = await asyncpg.connect(settings.database_url)
        await conn.execute(sql_content)
        await conn.close()
        
        logger.info(f"Migration {migration_file} executed successfully")
        
    except Exception as e:
        logger.error(f"Failed to execute migration {migration_file}: {e}")
        raise


async def check_db_health():
    """Check database health"""
    try:
        if supabase:
            # Simple health check query
            result = supabase.table('sites').select('id').limit(1).execute()
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

