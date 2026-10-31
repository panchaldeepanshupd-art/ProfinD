"""
ProfinD - Smart E-Commerce Product Price Comparison and Analysis System
Main Flask Application Entry Point
"""

from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
import database
import price_comparison

# Initialize the Flask application
app = Flask(__name__, instance_relative_config=True)

# Secret key used for session security and flash messaging
app.config['SECRET_KEY'] = 'profind-dev-secret-key-change-in-production'


# Register custom Jinja filter for Indian Rupee currency display
@app.template_filter('inr')
def inr_filter(paise):
    """Jinja filter: converts integer paise to Indian Rupee notation (e.g. ₹65,999)"""
    return database.format_inr(paise)


# Initialize SQLite database with tables and starter data automatically
with app.app_context():
    database.init_db()


def admin_required(f):
    """
    Decorator enforcing authentication on administrative routes.
    Unauthorized requests are redirected to /admin/login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Administrative authorization required. Please log in.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ====================================================================
# Public Consumer Facing Routes
# ====================================================================

@app.route('/')
def home():
    """
    Renders the ProfinD Homepage featuring the hero search bar,
    how-it-works workflow, and featured product highlights from the database.
    """
    featured_products = database.search_products()[:4]
    return render_template('index.html', featured_products=featured_products)


@app.route('/products')
def products():
    """
    Product catalog and search route.
    Handles keyword searching and category filtering using parameterized SQL queries.
    """
    query = request.args.get('q', '').strip()
    selected_category = request.args.get('category', '').strip()

    if 'q' in request.args and not query and not selected_category:
        flash('Please enter a product name or keyword to search.', 'info')

    product_results = database.search_products(keyword=query, category=selected_category)
    categories = database.get_all_categories()

    return render_template(
        'products.html',
        products=product_results,
        query=query,
        categories=categories,
        selected_category=selected_category
    )


@app.route('/product/<int:product_id>')
def product_details(product_id):
    """
    Product details and price comparison route.
    Uses O(n) DAA linear scan algorithm from price_comparison.py.
    Provides structured specifications and 30-day price history analysis.
    """
    product = database.get_product_by_id(product_id)
    if not product:
        flash(f'Product with ID #{product_id} was not found.', 'danger')
        return redirect(url_for('products'))

    raw_offers = database.get_offers_for_product(product_id)
    analysis = price_comparison.analyze_offers(raw_offers)
    specs_list = database.parse_specifications(product['specifications'])

    # Historical price analysis
    history_rows = database.get_price_history(product_id)
    history_analysis = price_comparison.analyze_price_history(history_rows)

    return render_template(
        'product_details.html',
        product=product,
        offers=raw_offers,
        analysis=analysis,
        specs_list=specs_list,
        history=history_analysis
    )


@app.route('/deal/<int:offer_id>')
def view_deal(offer_id):
    """
    Secure outbound shopping link redirector.
    Fulfills Section 4.E & Section 10:
    - Validates target URL scheme to prevent open-redirect and protocol exploits
    - Redirects safely to the retailer with HTTP 302
    """
    offer = database.get_offer_by_id(offer_id)
    if not offer:
        flash('The requested store deal is no longer available.', 'danger')
        return redirect(url_for('products'))

    url = offer['offer_url']
    if not database.is_safe_url(url):
        flash('Security Alert: The outbound URL was blocked as it failed safety verification.', 'danger')
        return redirect(url_for('product_details', product_id=offer['product_id']))

    return redirect(url, code=302)


@app.route('/compare')
def compare():
    """
    Dedicated Price Comparison view.
    Allows users to select and inspect full store comparison tables with DAA metrics.
    """
    all_products = database.search_products()
    selected_id = request.args.get('product_id', type=int)

    if not selected_id and all_products:
        selected_id = all_products[0]['id']

    selected_product = database.get_product_by_id(selected_id) if selected_id else None
    offers = database.get_offers_for_product(selected_id) if selected_id else []
    analysis = price_comparison.analyze_offers(offers) if offers else None

    return render_template(
        'compare.html',
        all_products=all_products,
        selected_product=selected_product,
        offers=offers,
        analysis=analysis
    )


@app.route('/about')
def about():
    """About the ProfinD Academic Project route."""
    return render_template('about.html')


@app.route('/contact')
def contact():
    """Contact & Project Viva inquiry route."""
    return render_template('contact.html')


# ====================================================================
# Secure Administrative Routes (Phase 9)
# ====================================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """
    Admin authentication portal using scrypt/PBKDF2 password verification.
    """
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if database.verify_admin_credentials(username, password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash(f'Authentication successful. Welcome, {username}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Please verify credentials.', 'danger')

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    """Terminates administrative session."""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('You have been logged out of the administrator portal.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """
    Administrative control dashboard for products, stores, and offers.
    """
    stats = database.get_dashboard_stats()
    products_list = database.search_products()
    stores_list = database.get_all_stores()

    return render_template(
        'admin_dashboard.html',
        stats=stats,
        products=products_list,
        stores=stores_list
    )


@app.route('/admin/product/add', methods=['POST'])
@admin_required
def admin_add_product():
    """Protected route to add a new product with input validation."""
    name = request.form.get('name', '').strip()
    brand = request.form.get('brand', '').strip()
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()
    specifications = request.form.get('specifications', '').strip()
    image_url = request.form.get('image_url', '').strip()

    if not name or not brand or not category:
        flash('Product name, brand, and category are mandatory.', 'danger')
        return redirect(url_for('admin_dashboard'))

    prod_id = database.add_product(name, brand, category, description, specifications, image_url)
    flash(f'Product "{name}" (ID #{prod_id}) created successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/product/delete/<int:product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    """Protected route to remove an obsolete product and cascade offers."""
    database.delete_product(product_id)
    flash(f'Product #{product_id} and all associated store offers were removed.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/offer/add', methods=['POST'])
@admin_required
def admin_add_offer():
    """Protected route to add or update a store offer with price validation."""
    try:
        product_id = int(request.form.get('product_id'))
        store_id = int(request.form.get('store_id'))
        price_rupees = float(request.form.get('price_rupees', 0))
        delivery_rupees = float(request.form.get('delivery_rupees', 0))
        offer_url = request.form.get('offer_url', '').strip()

        if price_rupees <= 0:
            flash('Price must be greater than zero.', 'danger')
            return redirect(url_for('admin_dashboard'))

        if not database.is_safe_url(offer_url):
            flash('Invalid offer URL: Scheme must be http or https.', 'danger')
            return redirect(url_for('admin_dashboard'))

        price_paise = int(price_rupees * 100)
        delivery_paise = int(delivery_rupees * 100)

        database.add_offer(product_id, store_id, price_paise, delivery_paise, offer_url)
        flash('Store offer recorded and new price checkpoint added to history.', 'success')
    except (ValueError, TypeError) as e:
        flash(f'Input validation error: {str(e)}', 'danger')

    return redirect(url_for('admin_dashboard'))


# ====================================================================
# Custom Error Handlers (Section 12)
# ====================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error handler with friendly navigation."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Custom 500 error handler protecting stack traces in production."""
    return render_template('404.html'), 500


if __name__ == '__main__':
    # Starts the local development server on http://127.0.0.1:5000/
    app.run(debug=True, port=5000)
