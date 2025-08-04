#!/usr/bin/env python3
"""
Check database contents
"""
from app import create_app
from extensions import db
from models import User, Category, Brand, Product

def check_database():
    app = create_app()
    
    with app.app_context():
        print("=== Users ===")
        users = User.query.all()
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Admin: {user.is_admin}")
        
        print(f"\n=== Categories (Total: {Category.query.count()}) ===")
        categories = Category.query.all()
        for cat in categories:
            print(f"ID: {cat.id}, Name: {cat.name}")
        
        print(f"\n=== Brands (Total: {Brand.query.count()}) ===")
        brands = Brand.query.all()
        for brand in brands:
            print(f"ID: {brand.id}, Name: {brand.name}")
        
        print(f"\n=== Products (Total: {Product.query.count()}) ===")
        products = Product.query.all()
        for product in products:
            print(f"ID: {product.id}, Name: {product.name}, Owner: {product.owner.username}, Status: {product.status}")

if __name__ == '__main__':
    check_database()
