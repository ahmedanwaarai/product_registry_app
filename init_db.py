#!/usr/bin/env python3
"""
Initialize database with sample data
"""
from app import create_app
from extensions import db
from models import User, Category, Brand, Product
from werkzeug.security import generate_password_hash

def init_database():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                mobile_number='+1234567890',
                is_admin=True,
                has_subscription=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Created admin user")
        
        # Check if demo user exists
        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            # Create demo user
            demo_user = User(
                username='demo',
                email='demo@example.com',
                mobile_number='+1234567891',
                is_admin=False,
                has_subscription=False
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            print("Created demo user")
        
        # Commit users before continuing
        db.session.commit()
        
        # Create sample categories
        categories = [
            {'name': 'Camera', 'description': 'Digital cameras and film cameras'},
            {'name': 'Lens', 'description': 'Camera lenses and accessories'},
            {'name': 'Lighting', 'description': 'Studio lights and flash equipment'},
            {'name': 'Audio', 'description': 'Microphones and audio recording equipment'},
            {'name': 'Accessories', 'description': 'Tripods, bags, and other accessories'},
        ]
        
        for cat_data in categories:
            existing = Category.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(name=cat_data['name'], description=cat_data['description'])
                db.session.add(category)
                print(f"Created category: {cat_data['name']}")
        
        # Create sample brands
        brands = [
            {'name': 'Canon', 'description': 'Canon camera equipment'},
            {'name': 'Nikon', 'description': 'Nikon camera equipment'},
            {'name': 'Sony', 'description': 'Sony camera equipment'},
            {'name': 'Fujifilm', 'description': 'Fujifilm camera equipment'},
            {'name': 'Panasonic', 'description': 'Panasonic camera equipment'},
            {'name': 'Godox', 'description': 'Godox lighting equipment'},
            {'name': 'Profoto', 'description': 'Profoto lighting equipment'},
        ]
        
        for brand_data in brands:
            existing = Brand.query.filter_by(name=brand_data['name']).first()
            if not existing:
                brand = Brand(name=brand_data['name'], description=brand_data['description'])
                db.session.add(brand)
                print(f"Created brand: {brand_data['name']}")
        
        # Commit all changes
        db.session.commit()
        
        # Create a sample product for demo user
        if demo_user and not Product.query.filter_by(user_id=demo_user.id).first():
            camera_category = Category.query.filter_by(name='Camera').first()
            canon_brand = Brand.query.filter_by(name='Canon').first()
            
            if camera_category and canon_brand:
                sample_product = Product(
                    name='Canon EOS R5',
                    serial_number='CR5123456789',
                    user_id=demo_user.id,
                    category_id=camera_category.id,
                    brand_id=canon_brand.id,
                    status='for_sale'
                )
                db.session.add(sample_product)
                db.session.commit()
                print("Created sample product for demo user")
        
        print("Database initialization completed!")

if __name__ == '__main__':
    init_database()
