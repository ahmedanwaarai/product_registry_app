#!/usr/bin/env python3
"""
Migration script to add new fields to User model for enhanced functionality
"""

from app import create_app
from extensions import db
from models import User
from sqlalchemy import text

def upgrade_database():
    """Add new fields to User model"""
    app = create_app()
    
    with app.app_context():
        # Check if columns exist before adding them
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        
        migrations = []
        
        if 'is_shopkeeper' not in columns:
            migrations.append('ALTER TABLE user ADD COLUMN is_shopkeeper BOOLEAN DEFAULT FALSE')
        
        if 'reset_token' not in columns:
            migrations.append('ALTER TABLE user ADD COLUMN reset_token VARCHAR(100)')
        
        if 'reset_token_expiry' not in columns:
            migrations.append('ALTER TABLE user ADD COLUMN reset_token_expiry DATETIME')
        
        # Execute migrations
        for migration in migrations:
            try:
                db.session.execute(text(migration))
                print(f"✓ Executed: {migration}")
            except Exception as e:
                print(f"✗ Failed: {migration} - {e}")
        
        # Commit changes
        if migrations:
            db.session.commit()
            print(f"✓ Database updated with {len(migrations)} changes")
        else:
            print("✓ Database is up to date")

if __name__ == '__main__':
    upgrade_database()
