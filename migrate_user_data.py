#!/usr/bin/env python3
"""
Migration script to add dummy ID card numbers and shop names to existing users.
This prevents form validation errors due to new required fields.
"""

from app import create_app
from extensions import db
from models import User
import random

def generate_dummy_id_card():
    """Generate a dummy ID card number in format: 35202-2818708-5"""
    # Generate random numbers
    first_part = random.randint(10000, 99999)
    second_part = random.randint(1000000, 9999999)
    third_part = random.randint(1, 9)
    return f"{first_part}-{second_part}-{third_part}"

def generate_dummy_shop_name():
    """Generate a dummy shop name for shopkeepers"""
    shop_prefixes = ["Digital", "Tech", "Photo", "Camera", "Electronics", "Professional"]
    shop_suffixes = ["Store", "Shop", "Center", "Hub", "Mart", "Place"]
    return f"{random.choice(shop_prefixes)} {random.choice(shop_suffixes)}"

def migrate_user_data():
    """Add dummy data to existing users"""
    app = create_app()
    
    with app.app_context():
        print("Starting user data migration...")
        
        # Get all users that need ID card numbers
        users_without_id = User.query.filter(
            (User.id_card_number == None) | (User.id_card_number == "")
        ).all()
        
        print(f"Found {len(users_without_id)} users without ID card numbers")
        
        for user in users_without_id:
            # Generate unique ID card number
            while True:
                dummy_id = generate_dummy_id_card()
                existing = User.query.filter_by(id_card_number=dummy_id).first()
                if not existing:
                    user.id_card_number = dummy_id
                    break
            
            # Add shop name for shopkeepers if they don't have one
            if user.is_shopkeeper and not user.shop_name:
                user.shop_name = generate_dummy_shop_name()
            
            print(f"Updated user {user.username}: ID={user.id_card_number}, Shop={user.shop_name or 'N/A'}")
        
        # Commit all changes
        db.session.commit()
        print(f"Migration completed! Updated {len(users_without_id)} users.")

if __name__ == "__main__":
    migrate_user_data()
