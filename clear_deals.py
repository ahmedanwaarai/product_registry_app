#!/usr/bin/env python3
"""
Script to delete all deals and deal items from the database
"""
from app import create_app
from models import Deal, DealItem
from extensions import db

def clear_all_deals():
    """Delete all deals and deal items from the database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Delete all deal items first (due to foreign key constraints)
            deal_items_count = DealItem.query.count()
            DealItem.query.delete()
            
            # Delete all deals
            deals_count = Deal.query.count()
            Deal.query.delete()
            
            # Commit the changes
            db.session.commit()
            
            print(f"Successfully deleted:")
            print(f"- {deal_items_count} deal items")
            print(f"- {deals_count} deals")
            print("Database is now clean and ready for testing!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error occurred while deleting deals: {e}")
            return False
    
    return True

if __name__ == "__main__":
    clear_all_deals()
