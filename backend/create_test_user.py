#!/usr/bin/env python3
"""Create a test user for development"""

import sys
import os

# Add backend directory to path (works anywhere)
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal
from app.models.database import User
from loguru import logger

def create_test_user():
    db = SessionLocal()

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "test@ayka.com").first()

        if existing_user:
            logger.info(f"Test user already exists (ID: {existing_user.id})")
            return

        # Create test user
        test_user = User(
            email="test@ayka.com",
            password_hash="dummy_hash",  # Not real auth for demo
            full_name="Test User",
            is_active=True
        )

        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        logger.info(f"✓ Test user created successfully!")
        logger.info(f"  ID: {test_user.id}")
        logger.info(f"  Email: {test_user.email}")
        logger.info(f"  Name: {test_user.full_name}")

    except Exception as e:
        logger.error(f"Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()