from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField, SubmitField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from wtforms.widgets import TextArea
from models import User, Product, Category, Brand

class LoginForm(FlaskForm):
    """Login form for both users and admins"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UserRegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(min=10, max=15)])
    id_card_number = StringField('ID Card Number', validators=[DataRequired(), Length(min=15, max=15)],
                                render_kw={"placeholder": "35202-2818708-5", "maxlength": "15"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', 
                             validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    user_type = SelectField('Account Type', choices=[
        ('user', 'User'),
        ('shopkeeper', 'Shopkeeper')
    ], default='user', validators=[DataRequired()])
    shop_name = StringField('Shop Name', validators=[Length(max=100)],
                           render_kw={"placeholder": "Required for Shopkeepers"})
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Check if username is already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')
    
    def validate_mobile_number(self, mobile_number):
        """Check if mobile number is already registered"""
        user = User.query.filter_by(mobile_number=mobile_number.data).first()
        if user:
            raise ValidationError('Mobile number already registered. Please use a different number.')
    
    def validate_id_card_number(self, id_card_number):
        """Check if ID card number is already registered and has correct format"""
        # Check format: 35202-2818708-5 (exactly 15 characters with dashes)
        import re
        pattern = r'^\d{5}-\d{7}-\d{1}$'
        if not re.match(pattern, id_card_number.data):
            raise ValidationError('ID Card Number must be in format: 35202-2818708-5')
        
        user = User.query.filter_by(id_card_number=id_card_number.data).first()
        if user:
            raise ValidationError('ID Card Number already registered. Please use a different ID card number.')
    
    def validate_shop_name(self, shop_name):
        """Check if shop name is provided for shopkeeper accounts"""
        if self.user_type.data == 'shopkeeper' and not shop_name.data:
            raise ValidationError('Shop Name is required for Shopkeeper accounts.')

class ProductRegistrationForm(FlaskForm):
    """Product registration form"""
    name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=100)])
    serial_number = StringField('Serial Number', validators=[DataRequired(), Length(min=3, max=100)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    brand_id = SelectField('Brand', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Register Product')
    
    def __init__(self, *args, **kwargs):
        super(ProductRegistrationForm, self).__init__(*args, **kwargs)
        # Populate category and brand choices
        self.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
        self.brand_id.choices = [(b.id, b.name) for b in Brand.query.all()]
    
    def validate_serial_number(self, serial_number):
        """Check if serial number is already registered"""
        product = Product.query.filter_by(serial_number=serial_number.data).first()
        if product:
            raise ValidationError('This serial number is already registered.')

class CategoryForm(FlaskForm):
    """Form for adding/editing categories (Admin only)"""
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Category')
    
    def validate_name(self, name):
        """Check if category name already exists"""
        category = Category.query.filter_by(name=name.data).first()
        if category:
            raise ValidationError('Category name already exists.')

class BrandForm(FlaskForm):
    """Form for adding/editing brands (Admin only)"""
    name = StringField('Brand Name', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Brand')
    
    def validate_name(self, name):
        """Check if brand name already exists"""
        brand = Brand.query.filter_by(name=name.data).first()
        if brand:
            raise ValidationError('Brand name already exists.')

class DealForm(FlaskForm):
    """Form for creating deals"""
    buyer_username = StringField('Buyer Username', validators=[DataRequired()])
    seller_username = StringField('Seller Username', validators=[DataRequired()])
    submit = SubmitField('Create Deal')
    
    def validate_buyer_username(self, buyer_username):
        """Check if buyer username exists"""
        user = User.query.filter_by(username=buyer_username.data).first()
        if not user:
            raise ValidationError('Buyer username not found.')
    
    def validate_seller_username(self, seller_username):
        """Check if seller username exists"""
        user = User.query.filter_by(username=seller_username.data).first()
        if not user:
            raise ValidationError('Seller username not found.')

class DealItemForm(FlaskForm):
    """Form for adding items to deals"""
    product_id = HiddenField('Product ID')
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add to Deal')

class SearchForm(FlaskForm):
    """Search form for admin"""
    search_type = SelectField('Search By', choices=[
        ('serial', 'Serial Number'),
        ('mobile', 'Mobile Number')
    ], validators=[DataRequired()])
    search_query = StringField('Search Query', validators=[DataRequired()])
    submit = SubmitField('Search')

class ProductStatusForm(FlaskForm):
    """Form for changing product status"""
    status = SelectField('Status', choices=[
        ('for_sale', 'For Sale'),
        ('locked', 'Locked'),
        ('stolen', 'Stolen/Snatched')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')

class EnhancedDealForm(FlaskForm):
    """Enhanced form for creating deals with serial numbers and seller details"""
    # Seller details (manual entry)
    seller_name = StringField('Seller Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    seller_mobile = StringField('Seller Mobile Number', validators=[DataRequired(), Length(min=10, max=15)])
    seller_id_card = StringField('Seller ID Card Number', validators=[DataRequired(), Length(min=5, max=50)])
    seller_address = TextAreaField('Seller Address', validators=[DataRequired(), Length(min=10, max=200)])
    
    # Product serial numbers (comma-separated)
    serial_numbers = TextAreaField('Product Serial Numbers (comma-separated)', 
                                 validators=[DataRequired()],
                                 render_kw={"placeholder": "Enter serial numbers separated by commas", "rows": 3})
    
    # Deal description
    description = TextAreaField('Deal Description (Optional)', 
                              render_kw={"placeholder": "Optional deal description", "rows": 2})
    
    submit = SubmitField('Create Deal')

class ProductVerificationForm(FlaskForm):
    """Form for product verification by serial number"""
    serial_number = StringField('Serial Number', 
                               validators=[DataRequired(), Length(min=3, max=100)],
                               render_kw={"placeholder": "Enter product serial number"})
    submit = SubmitField('Verify Product')

class ContactForm(FlaskForm):
    """Contact form for static pages"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Length(min=10, max=15)])
    message = TextAreaField('Message', 
                           validators=[DataRequired(), Length(min=10, max=500)],
                           render_kw={"rows": 4})
    submit = SubmitField('Send Message')

class PasswordResetRequestForm(FlaskForm):
    """Password reset request form"""
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')
    
    def validate_email(self, email):
        """Check if email exists in database"""
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('No account found with this email address.')

class PasswordResetForm(FlaskForm):
    """Password reset form"""
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm New Password', 
                             validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Reset Password')

class EnhancedSearchForm(FlaskForm):
    """Enhanced search form for admin with additional fields"""
    search_type = SelectField('Search By', choices=[
        ('serial', 'Serial Number'),
        ('mobile', 'Mobile Number'),
        ('username', 'Username'),
        ('id_card', 'ID Card Number'),
        ('shop_name', 'Shop Name')
    ], validators=[DataRequired()])
    search_query = StringField('Search Query', validators=[DataRequired()])
    submit = SubmitField('Search')

class UnifiedDealForm(FlaskForm):
    """Unified form for both Sale and Transfer deals"""
    deal_type = SelectField('Deal Type', choices=[
        ('sale', 'Sale Deal'),
        ('transfer', 'Transfer Deal')
    ], validators=[DataRequired()])
    
    # Buyer information
    buyer_username = StringField('Buyer Username', validators=[DataRequired()])
    
    # Seller information (for registered sellers)
    seller_username = StringField('Seller Username (if registered user)', validators=[])
    
    # Seller details for non-registered sellers
    seller_name = StringField('Seller Full Name')
    seller_mobile = StringField('Seller Mobile Number')
    seller_id_card = StringField('Seller ID Card Number')
    seller_address = TextAreaField('Seller Address')
    
    # Product information
    serial_numbers = TextAreaField('Product Serial Numbers (comma-separated)', 
                                 validators=[DataRequired()],
                                 render_kw={"placeholder": "Enter serial numbers separated by commas", "rows": 3})
    
    # Deal details
    total_amount = FloatField('Total Amount', validators=[NumberRange(min=0)], default=0.0)
    description = TextAreaField('Deal Description (Optional)', 
                              render_kw={"placeholder": "Optional deal description", "rows": 2})
    
    submit = SubmitField('Create Deal')
    
    def validate_buyer_username(self, buyer_username):
        """Check if buyer username exists"""
        user = User.query.filter_by(username=buyer_username.data).first()
        if not user:
            raise ValidationError('Buyer username not found.')
    
    def validate_seller_username(self, seller_username):
        """Check if seller username exists (if provided)"""
        if seller_username.data:
            user = User.query.filter_by(username=seller_username.data).first()
            if not user:
                raise ValidationError('Seller username not found.')

class CreateAdminForm(FlaskForm):
    """Form for creating new admin users"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(min=10, max=15)])
    id_card_number = StringField('ID Card Number', validators=[DataRequired(), Length(min=15, max=15)],
                                render_kw={"placeholder": "35202-2818708-5", "maxlength": "15"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', 
                             validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    role = SelectField('Admin Role', choices=[
        ('full', 'Full Access'),
        ('limited', 'Limited Access')
    ], validators=[DataRequired()])
    submit = SubmitField('Create Admin')

    def validate_username(self, username):
        """Check if username is already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')
    
    def validate_mobile_number(self, mobile_number):
        """Check if mobile number is already registered"""
        user = User.query.filter_by(mobile_number=mobile_number.data).first()
        if user:
            raise ValidationError('Mobile number already registered. Please use a different number.')
    
    def validate_id_card_number(self, id_card_number):
        """Check if ID card number is already registered and has correct format"""
        # Check format: 35202-2818708-5 (exactly 15 characters with dashes)
        import re
        pattern = r'^\d{5}-\d{7}-\d{1}$'
        if not re.match(pattern, id_card_number.data):
            raise ValidationError('ID Card Number must be in format: 35202-2818708-5')
        
        user = User.query.filter_by(id_card_number=id_card_number.data).first()
        if user:
            raise ValidationError('ID Card Number already registered. Please use a different ID card number.')

class ShopkeeperApprovalForm(FlaskForm):
    """Form for admin to approve/reject shopkeeper applications"""
    action = SelectField('Action', choices=[
        ('approve', 'Approve'),
        ('reject', 'Reject')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes (Optional)', render_kw={"rows": 3})
    submit = SubmitField('Submit')
