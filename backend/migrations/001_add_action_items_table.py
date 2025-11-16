#!/usr/bin/env python3
"""
Migration: Add action_items table
Run this script on the server to add the action items feature
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

def run_migration():
    """Create action_items table and indexes"""

    print("=" * 80)
    print("MIGRATION: Adding action_items table")
    print("=" * 80)

    with engine.connect() as conn:
        # Check if table already exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'action_items'
            );
        """))
        table_exists = result.scalar()

        if table_exists:
            print("⚠️  Table 'action_items' already exists. Skipping migration.")
            return

        print("\n📋 Creating action_items table...")

        # Create table
        conn.execute(text("""
            CREATE TABLE action_items (
                id SERIAL PRIMARY KEY,
                recording_id INTEGER NOT NULL REFERENCES recordings(id) ON DELETE CASCADE,

                -- Action details
                action TEXT NOT NULL,
                deadline TIMESTAMP,
                deadline_type VARCHAR(50),
                priority VARCHAR(20) DEFAULT 'medium',
                action_type VARCHAR(50),

                -- Context from conversation
                quote TEXT,
                mentioned_by VARCHAR(50),
                speaker_name VARCHAR(255),
                timestamp_seconds FLOAT,
                context TEXT,

                -- Contact information
                contact_email VARCHAR(255),
                contact_email_confidence FLOAT,
                contact_linkedin VARCHAR(500),
                contact_company VARCHAR(255),

                -- Status tracking
                status VARCHAR(20) DEFAULT 'pending',
                completed_at TIMESTAMP,
                notes TEXT,

                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        print("✅ Table created successfully")

        # Create indexes
        print("\n🔍 Creating indexes...")

        conn.execute(text("""
            CREATE INDEX idx_action_items_recording_id ON action_items(recording_id);
        """))
        print("✅ Index created: idx_action_items_recording_id")

        conn.execute(text("""
            CREATE INDEX idx_action_items_created_at ON action_items(created_at);
        """))
        print("✅ Index created: idx_action_items_created_at")

        conn.execute(text("""
            CREATE INDEX idx_action_items_status ON action_items(status);
        """))
        print("✅ Index created: idx_action_items_status")

        conn.execute(text("""
            CREATE INDEX idx_action_items_deadline ON action_items(deadline);
        """))
        print("✅ Index created: idx_action_items_deadline")

        conn.commit()

        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nAction items table is ready to use!")
        print("You can now extract action items from conversations.\n")


def rollback_migration():
    """Remove action_items table (rollback)"""

    print("=" * 80)
    print("ROLLBACK: Removing action_items table")
    print("=" * 80)

    with engine.connect() as conn:
        # Check if table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'action_items'
            );
        """))
        table_exists = result.scalar()

        if not table_exists:
            print("⚠️  Table 'action_items' does not exist. Nothing to rollback.")
            return

        print("\n🗑️  Dropping action_items table...")
        conn.execute(text("DROP TABLE IF EXISTS action_items CASCADE;"))
        conn.commit()

        print("✅ Table dropped successfully")
        print("\n" + "=" * 80)
        print("✅ ROLLBACK COMPLETED")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Action Items Table Migration")
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback the migration (drop table)"
    )

    args = parser.parse_args()

    try:
        if args.rollback:
            response = input("⚠️  This will DELETE the action_items table. Are you sure? (yes/no): ")
            if response.lower() == "yes":
                rollback_migration()
            else:
                print("Rollback cancelled.")
        else:
            run_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)