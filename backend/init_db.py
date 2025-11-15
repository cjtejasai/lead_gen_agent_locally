#!/usr/bin/env python3
"""Initialize database tables"""

import sys
import os
import logging

# Add backend directory to path (works anywhere)
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.core.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    logger.info("✓ Database initialized successfully!")