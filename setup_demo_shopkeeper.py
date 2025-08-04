from app import app, db
from models import User

with app.app_context():
    # Check if demo shopkeeper already exists
    demo_shopkeeper = User.query.filter_by(username='shopkeeper_demo').first()
    
    if not demo_shopkeeper:
        # Create demo shopkeeper user
        demo_user = User(
            username='shopkeeper_demo',
            email='demo@shopkeeper.com',
            mobile_number='9999999999',
            is_shopkeeper=True,
            shopkeeper_approved=True  # Pre-approved for demo
        )
        demo_user.set_password('demo@12345')
        
        db.session.add(demo_user)
        db.session.commit()
        
        print("Demo shopkeeper user created successfully!")
        print("Username: shopkeeper_demo")
        print("Password: demo@12345")
    else:
        print("Demo shopkeeper user already exists!")
