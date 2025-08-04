from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask import current_app
import pytz

# Import db and login_manager from the extensions
from extensions import db, login_manager

# Pakistan timezone
PAKISTAN_TZ = pytz.timezone('Asia/Karachi')

def pakistan_now():
    """Get current time in Pakistan timezone"""
    return datetime.now(PAKISTAN_TZ)

def utc_to_pakistan(utc_dt):
    """Convert UTC datetime to Pakistan timezone"""
    if utc_dt is None:
        return None
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(PAKISTAN_TZ).strftime('%d-%m-%Y %I:%M %p')

class User(UserMixin, db.Model):
    """User model for regular users, shopkeepers, and admins"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    id_card_number = db.Column(db.String(20), unique=True, nullable=False)  # Format: 35202-2818708-5
    shop_name = db.Column(db.String(100), nullable=True)  # Required for shopkeepers
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_shopkeeper = db.Column(db.Boolean, default=False)
    can_create_admins = db.Column(db.Boolean, default=False)  # Main admin privilege
    shopkeeper_approved = db.Column(db.Boolean, default=False)  # Admin approval for shopkeepers
    has_subscription = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='owner', lazy=True)
    deals_as_buyer = db.relationship('Deal', foreign_keys='Deal.buyer_id', backref='buyer', lazy=True)
    deals_as_seller = db.relationship('Deal', foreign_keys='Deal.seller_id', backref='seller', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def can_register_product(self):
        """Check if user can register more products
        Regular users: 3 free, unlimited with subscription
        Shopkeepers: 25 free, unlimited with subscription (must be approved)
        """
        if self.is_shopkeeper and not self.shopkeeper_approved:
            return False  # Unapproved shopkeepers cannot register products
            
        product_count = Product.query.filter_by(user_id=self.id).count()
        if self.is_shopkeeper:
            return product_count < 25 or self.has_subscription
        return product_count < 3 or self.has_subscription
    
    def can_sell_products(self):
        """Check if user can create deals to sell products
        Regular users: after 3 days of registration
        Shopkeepers: immediately
        """
        if self.is_shopkeeper:
            return True
        
        days_since_registration = (datetime.utcnow() - self.created_at).days
        return days_since_registration >= 3
    
    def get_user_type(self):
        """Get user type as string"""
        if self.is_admin:
            return 'admin'
        elif self.is_shopkeeper:
            return 'shopkeeper'
        else:
            return 'user'
    
    def generate_reset_token(self):
        """Generate password reset token"""
        import secrets
        self.reset_token = secrets.token_urlsafe(50)
        # Token expires in 1 hour
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Verify password reset token"""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        if datetime.utcnow() > self.reset_token_expiry:
            return False
        return self.reset_token == token
    
    def clear_reset_token(self):
        """Clear password reset token"""
        self.reset_token = None
        self.reset_token_expiry = None
    
    def __repr__(self):
        return f'<User {self.username}>'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Category(db.Model):
    """Product categories (Camera, Lens, Light, etc.)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Brand(db.Model):
    """Product brands"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='brand', lazy=True)
    
    def __repr__(self):
        return f'<Brand {self.name}>'

class Product(db.Model):
    """Registered products"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='for_sale')  # for_sale, locked, stolen
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    
    # Relationships
    status_history = db.relationship('ProductStatusHistory', backref='product', lazy=True)
    deal_items = db.relationship('DealItem', backref='product', lazy=True)
    
    def update_status(self, new_status, changed_by_user_id=None):
        """Update product status and create history record"""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        # Create status history record
        history = ProductStatusHistory(
            product_id=self.id,
            old_status=old_status,
            new_status=new_status,
            changed_at=datetime.utcnow(),
            changed_by=changed_by_user_id
        )
        db.session.add(history)
    
    def can_be_sold(self):
        """Check if this product can be sold based on business logic"""
        if self.status != 'for_sale':
            return False
        
        # Get the product owner
        owner = User.query.get(self.user_id)
        if not owner:
            return False
        
        # Shopkeepers can sell immediately
        if owner.is_shopkeeper:
            return True
        
        # Regular users must wait 3 days after product registration
        days_since_registration = (datetime.utcnow() - self.created_at).days
        return days_since_registration >= 3
    
    def transfer_ownership(self, new_owner_id, deal_id, transfer_type='sale'):
        """Transfer product ownership and record history"""
        old_owner_id = self.user_id
        self.user_id = new_owner_id
        self.updated_at = datetime.utcnow()
        
        # Create ownership history record
        ownership_record = OwnershipHistory(
            product_id=self.id,
            previous_owner_id=old_owner_id,
            new_owner_id=new_owner_id,
            deal_id=deal_id,
            transfer_type=transfer_type
        )
        db.session.add(ownership_record)
    
    def get_original_owner_id(self):
        """Get the original owner ID of the product (who first registered it)
        If no ownership history exists, the current owner is the original owner
        """
        first_ownership = OwnershipHistory.query.filter_by(product_id=self.id).order_by(OwnershipHistory.transfer_date.asc()).first()
        if first_ownership and first_ownership.previous_owner_id:
            return first_ownership.previous_owner_id
        else:
            # If no history exists, current owner is the original owner
            return self.user_id
    
    def create_initial_history(self):
        """Create initial status history entry for newly registered product"""
        # Check if initial history already exists
        initial_history = ProductStatusHistory.query.filter_by(
            product_id=self.id, old_status=None
        ).first()
        
        if not initial_history:
            history = ProductStatusHistory(
                product_id=self.id,
                old_status=None,
                new_status=self.status,
                changed_at=self.created_at,
                changed_by=self.user_id
            )
            db.session.add(history)
    
    def __repr__(self):
        return f'<Product {self.name} - {self.serial_number}>'

class ProductStatusHistory(db.Model):
    """Track status changes of products"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # User who made the change
    
    # Relationships
    changed_by_user = db.relationship('User', backref='status_changes_made')
    
    def __repr__(self):
        return f'<StatusHistory {self.product_id}: {self.old_status} -> {self.new_status}>'

class OwnershipHistory(db.Model):
    """Track ownership transfers of products"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    previous_owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    new_owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    deal_id = db.Column(db.Integer, db.ForeignKey('deal.id'), nullable=True)  # Associated deal
    transfer_date = db.Column(db.DateTime, default=datetime.utcnow)
    transfer_type = db.Column(db.String(20), default='sale')  # sale, transfer, initial_registration
    
    # Relationships
    product = db.relationship('Product', backref='ownership_history')
    previous_owner = db.relationship('User', foreign_keys=[previous_owner_id], backref='products_sold')
    new_owner = db.relationship('User', foreign_keys=[new_owner_id], backref='products_acquired')
    deal = db.relationship('Deal', backref='ownership_transfers')
    
    @staticmethod
    def get_visible_history(product_id, current_user):
        """Get ownership history visible to the current user
        - Current owner: can see all history
        - Previous owner: can see history up to their ownership period
        - Admin: can see all history
        """
        product = Product.query.get(product_id)
        if not product:
            return []
        
        # Admin can see all history
        if current_user.is_admin:
            return OwnershipHistory.query.filter_by(product_id=product_id).order_by(
                OwnershipHistory.transfer_date.desc()).all()
        
        # Current owner can see all history
        if product.user_id == current_user.id:
            return OwnershipHistory.query.filter_by(product_id=product_id).order_by(
                OwnershipHistory.transfer_date.desc()).all()
        
        # Previous owners can see limited history
        user_ownership_history = OwnershipHistory.query.filter(
            (OwnershipHistory.product_id == product_id) &
            ((OwnershipHistory.previous_owner_id == current_user.id) |
             (OwnershipHistory.new_owner_id == current_user.id))
        ).order_by(OwnershipHistory.transfer_date.desc()).all()
        
        return user_ownership_history
    
    def __repr__(self):
        return f'<OwnershipHistory {self.product_id}: User {self.previous_owner_id} -> User {self.new_owner_id}>'

class Deal(db.Model):
    """Deals between users"""
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed, cancelled
    total_amount = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text)  # Optional deal description
    deal_type = db.Column(db.String(20), default='normal')  # normal, transfer
    
    # Seller details for non-registered sellers
    seller_name = db.Column(db.String(100))  # For non-registered sellers
    seller_mobile = db.Column(db.String(15))  # For non-registered sellers
    seller_id_card = db.Column(db.String(50))  # For non-registered sellers
    seller_address = db.Column(db.Text)  # For non-registered sellers
    
    # Approval tracking
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime)
    approval_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Foreign Keys
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable for non-registered sellers
    
    # Relationships
    deal_items = db.relationship('DealItem', backref='deal', lazy=True)
    
    def __repr__(self):
        return f'<Deal {self.id}: {self.buyer.username} <- {self.seller.username}>'

class DealItem(db.Model):
    """Items in a deal"""
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    
    # Foreign Keys
    deal_id = db.Column(db.Integer, db.ForeignKey('deal.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    def __repr__(self):
        return f'<DealItem {self.product.name}: ${self.price}>'
