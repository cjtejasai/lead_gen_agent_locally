#!/usr/bin/env python3
"""Initialize database tables"""

import sys
import os

# Add backend directory to path (works anywhere)
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.core.database import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("✓ Database initialized successfully!")