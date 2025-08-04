#!/usr/bin/env python3
"""
Migration script to add description field to Deal model
"""

import sqlite3
import os

def migrate_database():
    """Add description column to Deal table"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'product_registry.db')
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run the main application first.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the description column already exists
        cursor.execute("PRAGMA table_info(deal)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'description' not in columns:
            # Add the description column
            cursor.execute("ALTER TABLE deal ADD COLUMN description TEXT")
            conn.commit()
            print("Successfully added description column to Deal table")
        else:
            print("Description column already exists in Deal table")
        
        conn.close()
        
    except Exception as e:
        print(f"Error migrating database: {e}")

if __name__ == "__main__":
    migrate_database()
