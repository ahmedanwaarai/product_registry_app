#!/usr/bin/env python3
"""
Migration script to add changed_by column to ProductStatusHistory table
Run this script to update existing database schema
"""

from app import app
from extensions import db
from sqlalchemy import text

def migrate_database():
    """Add changed_by column to ProductStatusHistory table"""
    with app.app_context():
        try:
            # Check if the column already exists
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM pragma_table_info('product_status_history') 
                    WHERE name='changed_by'
                """)).fetchone()
                
                if result.count == 0:
                    # Add the changed_by column
                    conn.execute(text("""
                        ALTER TABLE product_status_history 
                        ADD COLUMN changed_by INTEGER REFERENCES user(id)
                    """))
                    conn.commit()
                    print("✅ Successfully added 'changed_by' column to ProductStatusHistory table")
                else:
                    print("ℹ️  Column 'changed_by' already exists in ProductStatusHistory table")
                
        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            # Try alternative approach for SQLite
            try:
                print("🔄 Trying alternative approach...")
                with db.engine.connect() as conn:
                    conn.execute(text("""
                        ALTER TABLE product_status_history 
                        ADD COLUMN changed_by INTEGER
                    """))
                    conn.commit()
                    print("✅ Successfully added 'changed_by' column (without foreign key constraint)")
            except Exception as e2:
                print(f"❌ Alternative approach also failed: {str(e2)}")
                print("Manual intervention required. Please add the column manually or recreate the database.")

if __name__ == "__main__":
    print("🔧 Running database migration...")
    migrate_database()
    print("✅ Migration completed!")
