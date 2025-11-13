"""Database connection and session management"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Check if database connection is working"""
    try:
        # Try to execute a simple query
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection check passed")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def init_db():
    """Initialize database - create all tables"""
    from app.models.database import Base
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")