#!/usr/bin/env python3
"""
Script to create initial status history entries for existing products
that don't have any history records.
"""

from app import create_app
from models import db, Product, ProductStatusHistory

def create_initial_history_for_all_products():
    """Create initial status history for all products that don't have any"""
    app = create_app()
    
    with app.app_context():
        # Get all products
        products = Product.query.all()
        updated_count = 0
        
        for product in products:
            # Check if product already has initial history
            existing_history = ProductStatusHistory.query.filter_by(
                product_id=product.id, 
                old_status=None
            ).first()
            
            if not existing_history:
                # Create initial history entry
                initial_history = ProductStatusHistory(
                    product_id=product.id,
                    old_status=None,
                    new_status=product.status,
                    changed_at=product.created_at,
                    changed_by=product.user_id
                )
                db.session.add(initial_history)
                updated_count += 1
                print(f"Created initial history for product: {product.name} (ID: {product.id})")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\nSuccessfully created initial history entries for {updated_count} products.")
        else:
            print("No products needed initial history entries.")

if __name__ == "__main__":
    create_initial_history_for_all_products()
