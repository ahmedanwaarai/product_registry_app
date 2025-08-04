from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from sqlalchemy import or_
from models import User, Product, Category, Brand, Deal, DealItem, ProductStatusHistory, OwnershipHistory
from forms import (LoginForm, UserRegistrationForm, ProductRegistrationForm, 
                  CategoryForm, BrandForm, DealForm, DealItemForm, SearchForm, 
                  ProductStatusForm, EnhancedDealForm, ProductVerificationForm, ContactForm,
                  PasswordResetRequestForm, PasswordResetForm, EnhancedSearchForm,
                  UnifiedDealForm, ShopkeeperApprovalForm, CreateAdminForm)
from datetime import datetime
from urllib.parse import urlparse as url_parse

# Create Blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    """Home page"""
    return render_template('index.html', title='Product Registry')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both users and admins"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('main.admin_dashboard'))
        return redirect(url_for('main.user_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                if user.is_admin:
                    next_page = url_for('main.admin_dashboard')
                else:
                    next_page = url_for('main.user_dashboard')
            return redirect(next_page)
        flash('Invalid username or password', 'danger')
    return render_template('login.html', title='Login', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.user_dashboard'))
    
    form = UserRegistrationForm()
    if form.validate_on_submit():
        is_shopkeeper = (form.user_type.data == 'shopkeeper')
        user = User(
            username=form.username.data,
            email=form.email.data,
            mobile_number=form.mobile_number.data,
            id_card_number=form.id_card_number.data,
            shop_name=form.shop_name.data if is_shopkeeper else None,
            is_shopkeeper=is_shopkeeper,
            shopkeeper_approved=False if is_shopkeeper else True  # Regular users are auto-approved
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        if is_shopkeeper:
            flash('Your Shopkeeper registration request has been submitted and is pending admin approval.', 'info')
        else:
            flash('Registration successful! You can now login.', 'success')
        
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/user_dashboard')
@login_required
def user_dashboard():
    """User dashboard"""
    if current_user.is_admin:
        return redirect(url_for('main.admin_dashboard'))
    
    products = Product.query.filter_by(user_id=current_user.id).all()
    product_count = len(products)
    can_register = current_user.can_register_product()
    
    return render_template('user_dashboard.html', 
                         title='User Dashboard',
                         products=products,
                         product_count=product_count,
                         can_register=can_register)

@bp.route('/register_product', methods=['GET', 'POST'])
@login_required
def register_product():
    """Register a new product"""
    if current_user.is_admin:
        flash('Admins cannot register products', 'warning')
        return redirect(url_for('main.admin_dashboard'))
    
    if not current_user.can_register_product():
        if current_user.is_shopkeeper and not current_user.shopkeeper_approved:
            flash('Your shopkeeper account is pending admin approval. You cannot register products until your account is approved.', 'warning')
        else:
            limit = 25 if current_user.is_shopkeeper else 3
            user_type = 'shopkeeper' if current_user.is_shopkeeper else 'regular user'
            product_count = Product.query.filter_by(user_id=current_user.id).count()
            flash(f'You have reached the limit of {limit} free products for {user_type}. Please subscribe to register more.', 'warning')
        return redirect(url_for('main.user_dashboard'))
    
    form = ProductRegistrationForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            serial_number=form.serial_number.data,
            category_id=form.category_id.data,
            brand_id=form.brand_id.data,
            user_id=current_user.id
        )
        db.session.add(product)
        db.session.flush()  # Get product ID
        
        # Create initial status history
        product.create_initial_history()
        
        db.session.commit()
        flash('Product registered successfully!', 'success')
        return redirect(url_for('main.user_dashboard'))
    
    return render_template('register_product.html', title='Register Product', form=form)

@bp.route('/update_product_status/<int:product_id>', methods=['GET', 'POST'])
@login_required
def update_product_status(product_id):
    """Update product status (lock, unlock, mark as stolen)"""
    product = Product.query.get_or_404(product_id)
    
    # Check if user owns this product or is admin
    if product.user_id != current_user.id and not current_user.is_admin:
        flash('You can only update your own products', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    form = ProductStatusForm()
    
    if form.validate_on_submit():
        # Preserve Admin restrictions only
        if current_user.is_admin:
            # Admin restriction: Cannot change from 'Locked' to 'For Sale' - only product owner can do this
            if product.status == 'locked' and form.status.data == 'for_sale':
                flash('Only the product owner can change status from Locked to For Sale.', 'danger')
                return redirect(url_for('main.admin_search'))

            # Restriction: Only original owner can change status from 'Stolen' to any other status
            if product.status == 'stolen' and form.status.data != 'stolen':
                original_owner_id = product.get_original_owner_id()
                if current_user.id != original_owner_id:
                    flash('Only the original owner can change product status from Stolen to any other status.', 'danger')
                    return redirect(url_for('main.admin_search'))
        product.update_status(form.status.data, current_user.id)
        db.session.commit()
        flash('Product status updated successfully!', 'success')
        
        if current_user.is_admin:
            return redirect(url_for('main.admin_search'))
        return redirect(url_for('main.user_dashboard'))
    
    # Pre-populate current status on GET request
    if request.method == 'GET':
        form.status.data = product.status
    
    return render_template('update_product_status.html', 
                         title='Update Product Status', 
                         form=form, 
                         product=product)

@bp.route('/create_deal', methods=['GET', 'POST'])
@login_required
def create_deal():
    """Create a new deal with product selection"""
    if current_user.is_admin:
        flash('Admins cannot create deals', 'warning')
        return redirect(url_for('main.admin_dashboard'))
    
    form = DealForm()
    user_products = Product.query.filter_by(user_id=current_user.id, status='for_sale').all()
    
    if form.validate_on_submit():
        buyer = User.query.filter_by(username=form.buyer_username.data).first()
        seller = User.query.filter_by(username=form.seller_username.data).first()
        
        if buyer.id == seller.id:
            flash('Buyer and seller cannot be the same person', 'danger')
            return render_template('create_deal.html', title='Create Deal', form=form, user_products=user_products)
        
        # Create the deal
        deal = Deal(buyer_id=buyer.id, seller_id=seller.id)
        
        # Add description if provided
        deal_description = request.form.get('deal_description', '').strip()
        if deal_description:
            deal.description = deal_description
        
        db.session.add(deal)
        db.session.flush()  # Get the deal ID without committing
        
        # Handle product selection based on deal type
        deal_type = request.form.get('deal_type', 'single')
        total_amount = 0
        
        if deal_type == 'single':
            # Single product deal
            product_id = request.form.get('single_product_id')
            product_price = request.form.get('single_product_price')
            
            if product_id and product_price:
                product = Product.query.get(product_id)
                if product and product.user_id == current_user.id and product.status == 'for_sale':
                    deal_item = DealItem(
                        deal_id=deal.id,
                        product_id=product.id,
                        price=float(product_price)
                    )
                    db.session.add(deal_item)
                    total_amount += float(product_price)
                else:
                    flash('Selected product is not available for sale', 'danger')
                    return render_template('create_deal.html', title='Create Deal', form=form, user_products=user_products)
            else:
                flash('Please select a product and set a price', 'danger')
                return render_template('create_deal.html', title='Create Deal', form=form, user_products=user_products)
        
        else:
            # Multi-product deal
            selected_products = request.form.getlist('multi_products')
            
            if not selected_products:
                flash('Please select at least one product for the deal', 'danger')
                return render_template('create_deal.html', title='Create Deal', form=form, user_products=user_products)
            
            for product_id in selected_products:
                product_price = request.form.get(f'price_{product_id}')
                
                if product_price:
                    product = Product.query.get(product_id)
                    if product and product.user_id == current_user.id and product.status == 'for_sale':
                        deal_item = DealItem(
                            deal_id=deal.id,
                            product_id=product.id,
                            price=float(product_price)
                        )
                        db.session.add(deal_item)
                        total_amount += float(product_price)
                    else:
                        flash(f'Product {product.name if product else "Unknown"} is not available for sale', 'warning')
                else:
                    product = Product.query.get(product_id)
                    flash(f'Please set a price for {product.name if product else "selected product"}', 'warning')
                    return render_template('create_deal.html', title='Create Deal', form=form, user_products=user_products)
        
        # Update deal total
        deal.total_amount = total_amount
        
        db.session.commit()
        flash(f'Deal created successfully with {len(selected_products) if deal_type == "multi" else 1} product(s)!', 'success')
        return redirect(url_for('main.deal_details', deal_id=deal.id))
    
    return render_template('create_deal.html', title='Create Deal', form=form, user_products=user_products)

@bp.route('/deal/<int:deal_id>')
@login_required
def deal_details(deal_id):
    """View deal details"""
    deal = Deal.query.get_or_404(deal_id)
    
    # Check if user is involved in this deal or is admin
    if (deal.buyer_id != current_user.id and 
        deal.seller_id != current_user.id and 
        not current_user.is_admin):
        flash('You can only view deals you are involved in', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    return render_template('deal_details.html', title='Deal Details', deal=deal)

@bp.route('/user_deals')
@login_required
def user_deals():
    """View user's deals"""
    if current_user.is_admin:
        return redirect(url_for('main.admin_dashboard'))
    
    buyer_deals = Deal.query.filter_by(buyer_id=current_user.id).all()
    seller_deals = Deal.query.filter_by(seller_id=current_user.id).all()
    
    return render_template('user_deals.html', 
                         title='My Deals',
                         buyer_deals=buyer_deals,
                         seller_deals=seller_deals)

# Admin Routes
@bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    total_users = User.query.filter_by(is_admin=False).count()
    total_products = Product.query.count()
    total_deals = Deal.query.count()
    stolen_products = Product.query.filter_by(status='stolen').count()
    
    return render_template('admin_dashboard.html',
                         title='Admin Dashboard',
                         total_users=total_users,
                         total_products=total_products,
                         total_deals=total_deals,
                         stolen_products=stolen_products)

@bp.route('/admin/manage_categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    """Manage product categories"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, description=form.description.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('main.manage_categories'))
    
    categories = Category.query.all()
    return render_template('manage_categories.html',
                         title='Manage Categories',
                         form=form,
                         categories=categories)

@bp.route('/admin/manage_brands', methods=['GET', 'POST'])
@login_required
def manage_brands():
    """Manage brands"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    form = BrandForm()
    if form.validate_on_submit():
        brand = Brand(name=form.name.data, description=form.description.data)
        db.session.add(brand)
        db.session.commit()
        flash('Brand added successfully!', 'success')
        return redirect(url_for('main.manage_brands'))
    
    brands = Brand.query.all()
    return render_template('manage_brands.html',
                         title='Manage Brands',
                         form=form,
                         brands=brands)

@bp.route('/admin/deal_history', methods=['GET'])
@login_required
def admin_deal_history():
    """View complete deal history for a product by serial number"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))

    search_query = request.args.get('search', '').strip()
    history_results = []
    
    if search_query:
        # Search for products by serial, mobile, ID card, or name
        history_results = Product.query.join(User).filter(
            or_(
                Product.serial_number.ilike(f'%{search_query}%'),
                User.mobile_number.ilike(f'%{search_query}%'),
                User.id_card_number.ilike(f'%{search_query}%'),
                User.username.ilike(f'%{search_query}%')
            )
        ).all()

    return render_template('admin_deal_history.html',
                           title='Admin Deal History',
                           history_results=history_results,
                           search_query=search_query)

@bp.route('/admin/product_deal_history/<int:product_id>', methods=['GET'])
@login_required
def admin_product_deal_history(product_id):
    """View complete deal history for a specific product"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))

    product = Product.query.get_or_404(product_id)
    
    # Get all deals involving this product
    deals = db.session.query(Deal).join(DealItem).filter(
        DealItem.product_id == product_id
    ).order_by(Deal.created_at.desc()).all()
    
    # Get ownership history
    ownership_history = OwnershipHistory.query.filter_by(
        product_id=product_id
    ).order_by(OwnershipHistory.transfer_date.desc()).all()
    
    return render_template('admin_product_deal_history.html',
                           title=f'Deal History - {product.serial_number}',
                           product=product,
                           deals=deals,
                           ownership_history=ownership_history)

@bp.route('/admin/deals', methods=['GET', 'POST'])
@login_required
def admin_deal_approval():
    """Admin deal approval page"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))

    # Get search parameters
    status_filter = request.args.get('status', 'pending')
    search_query = request.args.get('search', '').strip()
    
    # Base query
    query = Deal.query.filter_by(status=status_filter)
    
    # Apply search filter if search query exists
    deals = []
    if search_query:
        # Search by seller name (registered or non-registered)
        seller_name_deals = query.join(User, Deal.seller_id == User.id, isouter=True).filter(
            or_(
                User.username.ilike(f'%{search_query}%'),
                Deal.seller_name.ilike(f'%{search_query}%')
            )
        ).all()
        
        # Search by buyer name
        buyer_name_deals = query.join(User, Deal.buyer_id == User.id).filter(
            User.username.ilike(f'%{search_query}%')
        ).all()
        
        # Search by mobile number (buyer or seller)
        mobile_deals = query.join(User, Deal.buyer_id == User.id, isouter=True).filter(
            or_(
                User.mobile_number.ilike(f'%{search_query}%'),
                Deal.seller_mobile.ilike(f'%{search_query}%')
            )
        ).all()
        
        # Search by serial number (through deal items)
        serial_deals = query.join(DealItem).join(Product).filter(
            Product.serial_number.ilike(f'%{search_query}%')
        ).all()
        
        # Combine all results and remove duplicates
        all_deals = seller_name_deals + buyer_name_deals + mobile_deals + serial_deals
        deals = list({deal.id: deal for deal in all_deals}.values())
    else:
        deals = query.all()

    if request.method == 'POST':
        # Update deal status
        deal_id = request.form.get('deal_id')
        new_status = request.form.get('status')
        notes = request.form.get('approval_notes', '').strip()
        deal = Deal.query.get(deal_id)

        if deal:
            deal.status = new_status
            deal.approved_by = current_user.id
            deal.approved_at = datetime.utcnow()
            deal.approval_notes = notes
            
            # Automatically transfer ownership when deal is approved
            if new_status == 'approved':
                for deal_item in deal.deal_items:
                    product = deal_item.product
                    
                    # Record ownership history
                    ownership_record = OwnershipHistory(
                        product_id=product.id,
                        previous_owner_id=product.user_id,
                        new_owner_id=deal.buyer_id,
                        deal_id=deal.id,
                        transfer_type='sale'
                    )
                    db.session.add(ownership_record)
                    
                    # Transfer ownership
                    product.user_id = deal.buyer_id
                
                flash('Deal approved successfully! Ownership has been transferred.', 'success')
            else:
                flash('Deal status updated successfully!', 'success')
            
            db.session.commit()
        else:
            flash('Deal not found.', 'danger')

        return redirect(url_for('main.admin_deal_approval', status=status_filter))

    return render_template('admin_deals.html',
                         title='Admin Deal Approval',
                         deals=deals,
                         status_filter=status_filter)

@bp.route('/admin/search', methods=['GET', 'POST'])
@login_required
def admin_search():
    """Admin search functionality"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    form = EnhancedSearchForm()
    results = []
    search_executed = False
    
    if form.validate_on_submit():
        search_executed = True
        search_type = form.search_type.data
        search_query = form.search_query.data
        
        if search_type == 'serial':
            product = Product.query.filter_by(serial_number=search_query).first()
            if product:
                results = [product]
        elif search_type == 'mobile':
            user = User.query.filter_by(mobile_number=search_query).first()
            if user:
                results = Product.query.filter_by(user_id=user.id).all()
        elif search_type == 'username':
            user = User.query.filter_by(username=search_query).first()
            if user:
                results = Product.query.filter_by(user_id=user.id).all()
        elif search_type == 'id_card':
            user = User.query.filter_by(id_card_number=search_query).first()
            if user:
                results = [user]
        elif search_type == 'shop_name':
            results = User.query.filter(User.shop_name.ilike(f'%{search_query}%')).all()
    
    return render_template('admin_search.html',
                         title='Search Products & Users',
                         form=form,
                         results=results,
                         search_executed=search_executed)

@bp.route('/shopkeeper_login', methods=['GET', 'POST'])
def shopkeeper_login():
    """Shopkeeper login page"""
    if current_user.is_authenticated and current_user.is_shopkeeper:
        return redirect(url_for('main.shopkeeper_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, is_shopkeeper=True).first()
        if user and user.check_password(form.password.data):
            if not user.shopkeeper_approved:
                flash('Your shopkeeper account has not been approved by the admin yet.', 'warning')
                return redirect(url_for('main.shopkeeper_login'))
            
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.shopkeeper_dashboard'))
        flash('Invalid username or password for a shopkeeper account.', 'danger')
    return render_template('shopkeeper_login.html', title='Shopkeeper Login', form=form)

@bp.route('/shopkeeper_dashboard')
@login_required
def shopkeeper_dashboard():
    """Shopkeeper dashboard"""
    if not current_user.is_shopkeeper:
        flash('Access denied. Shopkeeper account required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    products = Product.query.filter_by(user_id=current_user.id).all()
    product_count = len(products)
    
    return render_template('shopkeeper_dashboard.html', 
                         title='Shopkeeper Dashboard',
                         products=products,
                         product_count=product_count)

@bp.route('/create_unified_deal', methods=['GET', 'POST'])
@login_required
def create_unified_deal():
    """Create a unified deal for sale or transfer"""
    form = UnifiedDealForm()
    
    if form.validate_on_submit():
        deal_type = form.deal_type.data
        buyer_username = form.buyer_username.data
        seller_username = form.seller_username.data
        serial_numbers = [sn.strip() for sn in form.serial_numbers.data.split(',') if sn.strip()]

        buyer = User.query.filter_by(username=buyer_username).first()
        if not buyer:
            flash(f'Buyer \"{buyer_username}\" not found', 'danger')
            return render_template('create_unified_deal.html', title='Create Deal', form=form)

        seller = None
        if seller_username:
            seller = User.query.filter_by(username=seller_username).first()
            if not seller:
                flash(f'Seller \"{seller_username}\" not found', 'danger')
                return render_template('create_unified_deal.html', title='Create Deal', form=form)
        
        if buyer == seller:
            flash('Buyer and seller cannot be the same.', 'danger')
            return render_template('create_unified_deal.html', title='Create Deal', form=form)
        
        # Create Deal
        deal = Deal(
            deal_type=deal_type,
            buyer_id=buyer.id,
            seller_id=seller.id if seller else None,
            total_amount=form.total_amount.data,
            description=form.description.data
        )
        
        db.session.add(deal)
        db.session.flush()
        
        # Add Deal Items and Transfer Ownership
        for serial_number in serial_numbers:
            product = Product.query.filter_by(serial_number=serial_number).first()
            if not product:
                flash(f'Product with serial number {serial_number} not found.', 'danger')
                db.session.rollback()
                return render_template('create_unified_deal.html', title='Create Deal', form=form)
            
            deal_item = DealItem(
                deal_id=deal.id,
                product_id=product.id,
                price=form.total_amount.data if deal_type == 'sale' else 0
            )
            db.session.add(deal_item)
            
            # Transfer ownership immediately
            product.transfer_ownership(buyer.id, deal.id, deal_type)

        db.session.commit()
        flash(f'{deal_type.capitalize()} deal created successfully!', 'success')
        return redirect(url_for('main.deal_details', deal_id=deal.id))
        
    return render_template('create_unified_deal.html', title='Create Deal', form=form)


@bp.route('/admin/users')
@login_required
def admin_users():
    """View all users with enhanced search and management"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    # Get search parameters
    search_query = request.args.get('search', '')
    user_type_filter = request.args.get('type', 'all')
    
    # Build query
    query = User.query.filter_by(is_admin=False)
    
    if search_query:
        query = query.filter(
            or_(
                User.username.contains(search_query),
                User.mobile_number.contains(search_query),
                User.email.contains(search_query)
            )
        )
    
    if user_type_filter == 'shopkeeper':
        query = query.filter_by(is_shopkeeper=True)
    elif user_type_filter == 'user':
        query = query.filter_by(is_shopkeeper=False)
    
    users = query.all()
    total_users = User.query.filter_by(is_admin=False).count()
    
    return render_template('admin_users.html', 
                         title='User Management', 
                         users=users, 
                         total_users=total_users,
                         search_query=search_query,
                         user_type_filter=user_type_filter)

@bp.route('/admin/shopkeeper_approvals')
@login_required
def shopkeeper_approvals():
    """View pending shopkeeper approvals"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    pending_shopkeepers = User.query.filter_by(is_shopkeeper=True, shopkeeper_approved=False).all()
    approved_shopkeepers = User.query.filter_by(is_shopkeeper=True, shopkeeper_approved=True).all()
    
    return render_template('admin_shopkeeper_approvals.html',
                         title='Shopkeeper Approvals',
                         pending_shopkeepers=pending_shopkeepers,
                         approved_shopkeepers=approved_shopkeepers)

@bp.route('/admin/approve_shopkeeper/<int:user_id>', methods=['POST'])
@login_required
def approve_shopkeeper(user_id):
    """Approve or reject shopkeeper application"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')
    
    if action == 'approve':
        user.shopkeeper_approved = True
        flash(f'Shopkeeper {user.username} has been approved!', 'success')
    elif action == 'reject':
        # For rejection, we could either delete the user or mark them as rejected
        # For now, we'll just not approve them
        user.shopkeeper_approved = False
        flash(f'Shopkeeper application for {user.username} has been rejected.', 'warning')
    
    db.session.commit()
    return redirect(url_for('main.shopkeeper_approvals'))

@bp.route('/admin/create_admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    """Create new admin user (Main Admin only)"""
    if not current_user.is_admin or not current_user.can_create_admins:
        flash('Access denied. Only Main Admin can create new admins.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    
    form = CreateAdminForm()
    if form.validate_on_submit():
        admin = User(
            username=form.username.data,
            email=form.email.data,
            mobile_number=form.mobile_number.data,
            id_card_number=form.id_card_number.data,
            is_admin=True,
            can_create_admins=(form.role.data == 'full'),
            shopkeeper_approved=True  # Not applicable but set to True
        )
        admin.set_password(form.password.data)
        db.session.add(admin)
        db.session.commit()
        
        role_type = 'Full Access' if form.role.data == 'full' else 'Limited Access'
        flash(f'Admin user "{form.username.data}" created successfully with {role_type}!', 'success')
        return redirect(url_for('main.admin_users'))
    
    return render_template('create_admin.html', title='Create New Admin', form=form)

@bp.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit user details (admin only)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Update user details
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.mobile_number = request.form.get('mobile_number')
        user.has_subscription = 'has_subscription' in request.form
        
        if user.is_shopkeeper:
            user.shopkeeper_approved = 'shopkeeper_approved' in request.form
        
        db.session.commit()
        flash(f'User {user.username} updated successfully!', 'success')
        return redirect(url_for('main.admin_users'))
    
    return render_template('admin_edit_user.html', title='Edit User', user=user)


@bp.route('/admin/stolen_report')
@login_required
def stolen_report():
    """View stolen products report"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    stolen_products = Product.query.filter_by(status='stolen').all()
    return render_template('stolen_report.html',
                         title='Stolen Products Report',
                         stolen_products=stolen_products)

@bp.route('/product_history/<int:product_id>')
@login_required
def product_history(product_id):
    """View product status history"""
    product = Product.query.get_or_404(product_id)
    
    # Check permissions
    if (product.user_id != current_user.id and not current_user.is_admin):
        flash('You can only view history of your own products', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    history = ProductStatusHistory.query.filter_by(product_id=product_id).order_by(
        ProductStatusHistory.changed_at.desc()).all()
    # Add initial registration entry if not present
    if not history or history[-1].old_status is not None:
        initial_history = ProductStatusHistory(
            product_id=product.id,
            old_status=None,
            new_status=product.status,
            changed_at=product.created_at,
            changed_by=product.user_id
        )
        db.session.add(initial_history)
        db.session.commit()
        history.append(initial_history)

    return render_template('product_history.html',
                         title='Product History',
                         product=product,
                         history=history)

# Enhanced Deal Creation Route
@bp.route('/user_create_deal', methods=['GET', 'POST'])
@login_required
def user_create_deal():
    """Create a deal using serial numbers and manual seller details"""
    if current_user.is_admin:
        flash('Admins cannot create deals', 'warning')
        return redirect(url_for('main.admin_dashboard'))

    form = EnhancedDealForm()

    if form.validate_on_submit():
        # Get seller details
        seller_name = form.seller_name.data.strip()
        seller_mobile = form.seller_mobile.data.strip()
        seller_id_card = form.seller_id_card.data.strip()
        seller_address = form.seller_address.data.strip()
        
        # Debug: Log form data
        print(f"Form validated. Seller: {seller_name}, Serial Numbers: {form.serial_numbers.data}")

        # Process serial numbers and get product details
        serial_numbers = [sn.strip() for sn in form.serial_numbers.data.split(',') if sn.strip()]
        valid_products = []
        invalid_products = []
        product_details = []

        for serial_number in serial_numbers:
            product = Product.query.filter_by(serial_number=serial_number).first()
            
            # Debug logging
            print(f"Processing product {serial_number}:")
            if product:
                print(f"  - Found: {product.name}")
                print(f"  - Status: {product.status}")
                print(f"  - Owner: {product.owner.username if product.owner else 'None'}")
                print(f"  - Can be sold: {product.can_be_sold()}")
                print(f"  - Current user is shopkeeper: {current_user.is_shopkeeper}")
            else:
                print(f"  - Not found in database")
            
            if not product:
                invalid_products.append(f"{serial_number} (not found)")
            elif product.status == 'locked':
                invalid_products.append(f"{serial_number} (locked)")
            elif product.status == 'stolen':
                invalid_products.append(f"{serial_number} (stolen/snatched)")
            elif product.status != 'for_sale':
                invalid_products.append(f"{serial_number} (not for sale)")
            elif not product.can_be_sold():
                invalid_products.append(f"{serial_number} (not eligible for sale - holding period not met)")
            else:
                valid_products.append(product)
                product_details.append({
                    'product': product,
                    'brand': product.brand.name,
                    'category': product.category.name,
                    'name': product.name,
                    'serial': product.serial_number
                })
                print(f"  - Added to valid products")

        if invalid_products:
            flash(f'Cannot process: {", ".join(invalid_products)}', 'danger')
            return render_template('user_create_deal.html', title='Create Deal', form=form)

        if not valid_products:
            flash('No valid products found for deal.', 'warning')
            return render_template('user_create_deal.html', title='Create Deal', form=form)

        # Create deal (no price needed for verification deals)
        deal = Deal(
            buyer_id=current_user.id,
            seller_name=seller_name,
            seller_mobile=seller_mobile,
            seller_id_card=seller_id_card,
            seller_address=seller_address,
            description=form.description.data or f'Deal for {len(valid_products)} product(s)',
            total_amount=0.0  # Price can be added later
        )

        db.session.add(deal)
        db.session.flush()  # Get deal ID

        # Create deal items
        for product in valid_products:
            deal_item = DealItem(
                deal_id=deal.id,
                product_id=product.id,
                price=0.0  # Price can be set later
            )
            db.session.add(deal_item)

        db.session.commit()
        flash('Deal created successfully!', 'success')
        return redirect(url_for('main.deal_details', deal_id=deal.id))

    return render_template('user_create_deal.html', title='Create Deal', form=form)

# AJAX Product Verification Route
@bp.route('/verify_product_ajax', methods=['POST'])
def verify_product_ajax():
    """AJAX endpoint for real-time product verification"""
    from flask import jsonify, request
    
    try:
        data = request.get_json()
        serial_number = data.get('serial_number', '').strip()
        
        if not serial_number:
            return jsonify({
                'success': False,
                'message': 'Serial number is required'
            })
        
        product = Product.query.filter_by(serial_number=serial_number).first()
        
        if not product:
            return jsonify({
                'success': False,
                'message': 'Product not found in database'
            })
        
        # Check if the product can be sold based on business logic
        can_sell = product.can_be_sold()
        
        return jsonify({
            'success': True,
            'product': {
                'name': product.name,
                'serial_number': product.serial_number,
                'brand': product.brand.name,
                'category': product.category.name,
                'status': product.status,
                'can_sell': can_sell
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error verifying product'
        })

# Product Verification Route
@bp.route('/verify_product', methods=['GET', 'POST'])
def verify_product():
    """Verify product status by serial number (public access)"""
    form = ProductVerificationForm()
    product = None
    
    if form.validate_on_submit():
        product = Product.query.filter_by(serial_number=form.serial_number.data).first()
        if not product:
            flash('Product with this serial number not found in our database.', 'warning')
    
    return render_template('verify_product.html', 
                         title='Verify Product', 
                         form=form, 
                         product=product)

# Ownership Transfer Route
@bp.route('/transfer_ownership', methods=['GET', 'POST'])
@login_required
def transfer_ownership():
    """Transfer ownership of products to logged-in user"""
    if current_user.is_admin:
        flash('Admins cannot transfer ownership', 'warning')
        return redirect(url_for('main.admin_dashboard'))

    form = EnhancedDealForm()

    if form.validate_on_submit():
        # Get seller details
        seller_name = form.seller_name.data.strip()
        seller_mobile = form.seller_mobile.data.strip()
        seller_id_card = form.seller_id_card.data.strip()
        seller_address = form.seller_address.data.strip()

        # Process serial numbers
        serial_numbers = [sn.strip() for sn in form.serial_numbers.data.split(',') if sn.strip()]
        valid_products = []
        invalid_products = []

        for serial_number in serial_numbers:
            product = Product.query.filter_by(serial_number=serial_number).first()
            if not product:
                invalid_products.append(f"{serial_number} (not found)")
            elif product.status == 'locked':
                invalid_products.append(f"{serial_number} (locked)")
            elif product.status == 'stolen':
                invalid_products.append(f"{serial_number} (stolen/snatched)")
            else:
                valid_products.append(product)

        if invalid_products:
            flash(f'Cannot transfer: {", ".join(invalid_products)}', 'danger')
            return render_template('transfer_ownership.html', title='Transfer Ownership', form=form)

        if not valid_products:
            flash('No valid products found for transfer.', 'warning')
            return render_template('transfer_ownership.html', title='Transfer Ownership', form=form)

        # Create transfer deal
        deal = Deal(
            buyer_id=current_user.id,
            seller_name=seller_name,
            seller_mobile=seller_mobile,
            seller_id_card=seller_id_card,
            seller_address=seller_address,
            deal_type='transfer',
            description=form.description.data or 'Ownership Transfer',
            total_amount=0.0  # No price for transfers
        )

        db.session.add(deal)
        db.session.flush()  # Get deal ID

        # Create deal items and transfer ownership
        for product in valid_products:
            # Create deal item
            deal_item = DealItem(
                deal_id=deal.id,
                product_id=product.id,
                price=0.0  # No price for transfers
            )
            db.session.add(deal_item)

            # Record ownership history
            ownership_record = OwnershipHistory(
                product_id=product.id,
                previous_owner_id=product.user_id,
                new_owner_id=current_user.id,
                deal_id=deal.id,
                transfer_type='transfer'
            )
            db.session.add(ownership_record)

            # Transfer ownership
            product.user_id = current_user.id

        db.session.commit()
        flash(f'Successfully transferred ownership of {len(valid_products)} product(s)!', 'success')
        return redirect(url_for('main.deal_details', deal_id=deal.id))

    return render_template('transfer_ownership.html', title='Transfer Ownership', form=form)

# Admin Ownership History Route
@bp.route('/admin/ownership_history/<int:product_id>')
@login_required
def admin_ownership_history(product_id):
    """View ownership history for a product (Admin only)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))

    product = Product.query.get_or_404(product_id)
    ownership_history = OwnershipHistory.query.filter_by(product_id=product_id).order_by(
        OwnershipHistory.transfer_date.desc()).all()

    return render_template('admin_ownership_history.html',
                         title='Product Ownership History',
                         product=product,
                         ownership_history=ownership_history)

# Static Information Pages
@bp.route('/about')
def about():
    """About Us page"""
    return render_template('about.html', title='About Us')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact Us page"""
    form = ContactForm()
    if form.validate_on_submit():
        # In a real application, you would send an email or save to database
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html', title='Contact Us', form=form)

@bp.route('/services')
def services():
    """Our Services page"""
    return render_template('services.html', title='Our Services')

@bp.route('/terms')
def terms():
    """Terms & Conditions page"""
    return render_template('terms.html', title='Terms & Conditions')

# Brand Management Routes with Edit/Delete
@bp.route('/admin/edit_brand/<int:brand_id>', methods=['GET', 'POST'])
@login_required
def edit_brand(brand_id):
    """Edit existing brand"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    brand = Brand.query.get_or_404(brand_id)
    form = BrandForm(obj=brand)
    
    if form.validate_on_submit():
        # Check if name is being changed and if new name already exists
        if form.name.data != brand.name:
            existing_brand = Brand.query.filter_by(name=form.name.data).first()
            if existing_brand:
                flash('Brand name already exists.', 'danger')
                return render_template('edit_brand.html', title='Edit Brand', form=form, brand=brand)
        
        brand.name = form.name.data
        brand.description = form.description.data
        db.session.commit()
        flash('Brand updated successfully!', 'success')
        return redirect(url_for('main.manage_brands'))
    
    return render_template('edit_brand.html', title='Edit Brand', form=form, brand=brand)

@bp.route('/admin/delete_brand/<int:brand_id>', methods=['POST'])
@login_required
def delete_brand(brand_id):
    """Delete brand"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    brand = Brand.query.get_or_404(brand_id)
    
    # Check if brand has associated products
    if brand.products:
        flash('Cannot delete brand. There are products associated with this brand.', 'danger')
        return redirect(url_for('main.manage_brands'))
    
    db.session.delete(brand)
    db.session.commit()
    flash('Brand deleted successfully!', 'success')
    return redirect(url_for('main.manage_brands'))

# Password Reset Routes
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('main.user_dashboard'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            db.session.commit()
            # In a real application, send email with reset link
            # For now, just flash the token (for development only)
            flash(f'Password reset link has been sent to your email. Token: {token}', 'info')
            flash('Check your email for password reset instructions.', 'info')
        else:
            flash('If an account with that email exists, you will receive a password reset email.', 'info')
        return redirect(url_for('main.login'))
    
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.user_dashboard'))
    
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset token.', 'danger')
        return redirect(url_for('main.login'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        db.session.commit()
        flash('Your password has been reset successfully!', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('reset_password.html', title='Reset Password', form=form)

# Deal PDF Export Route
@bp.route('/deal/<int:deal_id>/export')
@login_required
def export_deal_pdf(deal_id):
    """Export deal as PDF"""
    deal = Deal.query.get_or_404(deal_id)
    
    # Check if user is involved in this deal or is admin
    if (deal.buyer_id != current_user.id and 
        deal.seller_id != current_user.id and 
        not current_user.is_admin):
        flash('You can only export deals you are involved in', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    # Generate PDF using ReportLab
    from flask import make_response
    from pdf_generator import generate_deal_pdf
    
    try:
        pdf_data = generate_deal_pdf(deal)
        
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=deal_{deal.id}_{deal.created_at.strftime("%Y%m%d")}.pdf'
        response.headers['Content-Length'] = len(pdf_data)
        
        return response
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('main.deal_details', deal_id=deal.id))

# Sale Deal Completion and Ownership Transfer
@bp.route('/admin/complete_deal/<int:deal_id>', methods=['POST'])
@login_required
def complete_deal(deal_id):
    """Complete a deal and transfer ownership (Admin only)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    deal = Deal.query.get_or_404(deal_id)
    
    if deal.status != 'approved':
        flash('Only approved deals can be completed.', 'danger')
        return redirect(url_for('main.admin_deal_approval'))
    
    # Complete the deal and transfer ownership
    for deal_item in deal.deal_items:
        product = deal_item.product
        
        # Record ownership history
        ownership_record = OwnershipHistory(
            product_id=product.id,
            previous_owner_id=product.user_id,
            new_owner_id=deal.buyer_id,
            deal_id=deal.id,
            transfer_type='sale'
        )
        db.session.add(ownership_record)
        
        # Transfer ownership
        product.user_id = deal.buyer_id
    
    # Update deal status
    deal.status = 'completed'
    deal.completed_at = datetime.utcnow()
    
    db.session.commit()
    flash('Deal completed successfully! Ownership has been transferred.', 'success')
    return redirect(url_for('main.admin_deal_approval'))

# User Ownership History (Limited to last 2 owners)
@bp.route('/ownership_history/<int:product_id>')
@login_required
def user_ownership_history(product_id):
    """View limited ownership history for a product (User access)"""
    product = Product.query.get_or_404(product_id)
    
    # Check if user is current or previous owner
    recent_history = OwnershipHistory.query.filter_by(product_id=product_id).order_by(
        OwnershipHistory.transfer_date.desc()).limit(2).all()
    
    user_can_view = False
    if current_user.is_admin:
        user_can_view = True
    elif product.user_id == current_user.id:
        user_can_view = True
    elif recent_history and len(recent_history) > 1 and recent_history[1].previous_owner_id == current_user.id:
        user_can_view = True
    
    if not user_can_view:
        flash('You can only view ownership history for products you currently own or previously owned.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    
    return render_template('user_ownership_history.html',
                         title='Product Ownership History',
                         product=product,
                         ownership_history=recent_history)

def register_routes(app):
    """Register blueprint with the Flask app"""
    app.register_blueprint(bp)
