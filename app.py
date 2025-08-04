from flask import Flask
from extensions import db, migrate, login_manager, csrf
import os
from datetime import datetime
import pytz

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product_registry.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Set Pakistan timezone as default
    app.config['TIMEZONE'] = 'Asia/Karachi'
    os.environ['TZ'] = 'Asia/Karachi'
    
    # Create timezone utility functions
    pakistan_tz = pytz.timezone('Asia/Karachi')
    
    @app.template_filter('pakistan_time')
    def pakistan_time_filter(dt):
        """Convert UTC datetime to Pakistan time"""
        if dt is None:
            return ''
        if dt.tzinfo is None:
            # Assume UTC if no timezone info
            dt = pytz.utc.localize(dt)
        return dt.astimezone(pakistan_tz).strftime('%d-%m-%Y %H:%M:%S PKT')
    
    @app.template_filter('pakistan_date')
    def pakistan_date_filter(dt):
        """Convert UTC datetime to Pakistan date"""
        if dt is None:
            return ''
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        return dt.astimezone(pakistan_tz).strftime('%d-%m-%Y')
    
    @app.context_processor
    def inject_timezone_utils():
        def now_pakistan():
            return datetime.now(pakistan_tz)
        
        def current_pakistan_time():
            return datetime.now(pakistan_tz).strftime('%d-%m-%Y')
        
        def utc_to_pakistan(utc_dt):
            """Convert UTC datetime to Pakistan timezone"""
            if utc_dt is None:
                return 'N/A'
            if utc_dt.tzinfo is None:
                utc_dt = pytz.utc.localize(utc_dt)
            return utc_dt.astimezone(pakistan_tz).strftime('%d-%m-%Y %I:%M %p')
            
        return dict(
            now_pakistan=now_pakistan,
            current_pakistan_time=current_pakistan_time,
            utc_to_pakistan=utc_to_pakistan,
            pakistan_tz=pakistan_tz
        )

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Import models to register them with SQLAlchemy
    import models
    
    # Register routes blueprint
    from routes import register_routes
    register_routes(app)
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        from models import User, Category, Brand
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@productregistry.com',
                mobile_number='1234567890',
                id_card_number='99999-000000-1',  # Dummy ID card for main admin
                is_admin=True,
                can_create_admins=True  # Main admin can create other admins
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
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
                
        db.session.commit()
        print("Database initialized successfully!")
        print("Default admin user: username='admin', password='admin123'")
    
    app.run(debug=True)
