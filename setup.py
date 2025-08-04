#!/usr/bin/env python3
"""
Product Registry Application Setup Script

This script helps you set up the Product Registry application by:
1. Installing required dependencies
2. Creating the database with sample data
3. Setting up the initial admin user
4. Providing instructions to run the application

Usage:
    python setup.py
"""

import os
import sys
import subprocess
import sqlite3
from datetime import datetime

def print_header():
    """Print application header"""
    print("=" * 60)
    print("🛡️  PRODUCT REGISTRY SETUP")
    print("=" * 60)
    print("Setting up your secure product registration system...")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python version: {sys.version.split()[0]} (Compatible)")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies. Please install manually:")
        print("   pip install -r requirements.txt")
        return False
    return True

def create_database():
    """Create database and tables"""
    print("\n🗄️  Setting up database...")
    try:
        # Import after dependencies are installed
        from app import app, db
        from models import User, Category, Brand, Product
        
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Create default admin user
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@productregistry.com',
                    mobile_number='1234567890',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                print("👤 Created default admin user")
            
            # Create default categories
            if Category.query.count() == 0:
                categories = [
                    Category(name='Camera', description='Digital cameras and film cameras'),
                    Category(name='Lens', description='Camera lenses and optical equipment'),
                    Category(name='Light', description='Photography and videography lighting equipment'),
                    Category(name='Audio', description='Microphones and audio recording equipment'),
                    Category(name='Accessories', description='Tripods, bags, and other accessories')
                ]
                for category in categories:
                    db.session.add(category)
                print("📂 Created default categories")
            
            # Create default brands
            if Brand.query.count() == 0:
                brands = [
                    Brand(name='Canon', description='Canon camera equipment'),
                    Brand(name='Nikon', description='Nikon camera equipment'),
                    Brand(name='Sony', description='Sony camera equipment'),
                    Brand(name='Fujifilm', description='Fujifilm camera equipment'),
                    Brand(name='Panasonic', description='Panasonic camera equipment'),
                    Brand(name='Godox', description='Godox lighting equipment'),
                    Brand(name='Manfrotto', description='Manfrotto tripods and accessories')
                ]
                for brand in brands:
                    db.session.add(brand)
                print("🏷️  Created default brands")
            
            db.session.commit()
            print("✅ Database setup completed!")
            
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        return False
    return True

def create_sample_data():
    """Create sample data for demonstration"""
    print("\n📝 Creating sample data...")
    try:
        from app import app, db
        from models import User, Product, Category, Brand
        
        with app.app_context():
            # Create sample user
            sample_user = User.query.filter_by(username='demo_user').first()
            if not sample_user:
                sample_user = User(
                    username='demo_user',
                    email='demo@example.com',
                    mobile_number='9876543210'
                )
                sample_user.set_password('demo123')
                db.session.add(sample_user)
                db.session.commit()
                
                # Create sample products for demo user
                camera_category = Category.query.filter_by(name='Camera').first()
                lens_category = Category.query.filter_by(name='Lens').first()
                canon_brand = Brand.query.filter_by(name='Canon').first()
                sony_brand = Brand.query.filter_by(name='Sony').first()
                
                if camera_category and lens_category and canon_brand and sony_brand:
                    sample_products = [
                        Product(
                            name='Canon EOS R5',
                            serial_number='CR5-2024-001',
                            user_id=sample_user.id,
                            category_id=camera_category.id,
                            brand_id=canon_brand.id,
                            status='for_sale'
                        ),
                        Product(
                            name='Sony FX3',
                            serial_number='SFX3-2024-001',
                            user_id=sample_user.id,
                            category_id=camera_category.id,
                            brand_id=sony_brand.id,
                            status='locked'
                        )
                    ]
                    
                    for product in sample_products:
                        db.session.add(product)
                    
                    db.session.commit()
                    print("👤 Created demo user with sample products")
            
    except Exception as e:
        print(f"⚠️  Sample data creation failed: {str(e)}")
        # This is not critical, so we continue

def print_instructions():
    """Print final instructions"""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("\n1. Run the application:")
    print("   python app.py")
    print("\n2. Open your web browser and go to:")
    print("   http://localhost:5000")
    print("\n3. Login credentials:")
    print("   👨‍💼 Admin User:")
    print("      Username: admin")
    print("      Password: admin123")
    print("\n   👤 Demo User:")
    print("      Username: demo_user")
    print("      Password: demo123")
    print("\n4. Features to explore:")
    print("   • Register products (up to 3 free)")
    print("   • Change product status (For Sale/Locked/Stolen)")
    print("   • Create deals between users")
    print("   • Admin tools for managing categories and brands")
    print("   • Search products by serial number or mobile")
    print("   • View stolen products report")
    print("\n⚠️  SECURITY NOTES:")
    print("   • Change default passwords before production use")
    print("   • Update the SECRET_KEY in app.py")
    print("   • Use a production database (PostgreSQL) for real deployment")
    print("\n" + "=" * 60)

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create database
    if not create_database():
        sys.exit(1)
    
    # Create sample data
    create_sample_data()
    
    # Print final instructions
    print_instructions()

if __name__ == "__main__":
    main()
