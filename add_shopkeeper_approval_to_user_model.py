from app import app, db
from models import User

with app.app_context():
    # Add the new 'shopkeeper_approved' column to the User table
    with db.engine.connect() as conn:
        try:
            conn.execute(db.text('ALTER TABLE user ADD COLUMN shopkeeper_approved BOOLEAN DEFAULT FALSE'))
            conn.commit()
            print("Column 'shopkeeper_approved' added successfully!")
        except Exception as e:
            print(f"Column might already exist or error occurred: {e}")

