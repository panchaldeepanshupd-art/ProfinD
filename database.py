"""
ProfinD — Database Module (SQLite3)
ADBMS Relational Layer with Parameterized SQL and Exact Currency Handling
"""

import os
import sqlite3
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash, check_password_hash

# Path to the SQLite database inside the instance/ directory
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
DB_PATH = os.path.join(DB_DIR, 'profind.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')


def get_db_connection():
    """
    Establishes and returns a connection to the SQLite database.
    Configures sqlite3.Row for dictionary-like column access and enables foreign keys.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def format_inr(paise):
    """
    Utility function to format integer paise into the standard Indian Rupee notation.
    Example: 6599900 paise -> '₹65,999'
    Avoids floating-point precision issues by using integer division.
    """
    if paise is None or paise == "":
        return "N/A"
    
    rupees = int(paise) // 100
    s = str(abs(rupees))
    
    if len(s) <= 3:
        formatted = s
    else:
        last3 = s[-3:]
        rem = s[:-3]
        groups = []
        while len(rem) > 2:
            groups.append(rem[-2:])
            rem = rem[:-2]
        if rem:
            groups.append(rem)
        groups.reverse()
        formatted = ",".join(groups) + "," + last3
        
    sign = "-" if rupees < 0 else ""
    return f"₹{sign}{formatted}"


def init_db():
    """
    Initializes database tables from schema.sql.
    Seeds default administrative user and comprehensive demo catalog if empty.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Execute Schema
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()

    # 2. Seed database if empty using seed_data
    import seed_data
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products;")
    if cursor.fetchone()[0] == 0:
        conn.close()
        seed_data.seed_database(reset=False)
    else:
        conn.close()


def search_products(keyword=None, category=None):
    """
    Searches the products catalog with case-insensitive matching across
    product name, brand, category, and description.
    Uses parameterized SQL to protect against SQL Injection.
    Calculates the minimum comparable offer total (price + delivery).
    """
    conn = get_db_connection()
    
    base_query = """
        SELECT 
            p.id,
            p.name,
            p.brand,
            p.category,
            p.description,
            p.specifications,
            p.image_url,
            MIN(o.price_paise + o.delivery_charge_paise) AS min_total_paise,
            MIN(o.price_paise) AS min_price_paise,
            COUNT(o.id) AS offer_count
        FROM products p
        LEFT JOIN offers o ON p.id = o.product_id AND o.is_active = 1
    """
    
    conditions = []
    params = []
    
    if keyword and keyword.strip():
        term = f"%{keyword.strip()}%"
        conditions.append("(p.name LIKE ? OR p.brand LIKE ? OR p.category LIKE ? OR p.description LIKE ?)")
        params.extend([term, term, term, term])
        
    if category and category.strip() and category.lower() != 'all':
        conditions.append("p.category = ?")
        params.append(category.strip())
        
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
        
    base_query += " GROUP BY p.id ORDER BY p.name ASC;"
    
    rows = conn.execute(base_query, params).fetchall()
    conn.close()
    return rows


def get_all_categories():
    """
    Returns a distinct list of product categories available in the database.
    """
    conn = get_db_connection()
    rows = conn.execute("SELECT DISTINCT category FROM products ORDER BY category ASC;").fetchall()
    conn.close()
    return [row['category'] for row in rows]


def get_product_by_id(product_id):
    """
    Fetches a single product record by its primary key ID.
    """
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM products WHERE id = ?;", (product_id,)).fetchone()
    conn.close()
    return row


def is_safe_url(url: str) -> bool:
    """
    Validates outbound store deal URLs to prevent open-redirect vulnerabilities
    and script-injection schemes (e.g. javascript:, file:, data:).
    Only valid HTTP and HTTPS URLs with a network location are permitted.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in {'http', 'https'} and bool(parsed.netloc)
    except Exception:
        return False


def parse_specifications(specs_str: str) -> list:
    """
    Parses a pipe-delimited specifications string into a structured list of
    dictionaries with 'label' and 'value' for professional table rendering.
    Example: 'Display: 6.1 OLED | Storage: 128GB' -> [{'label': 'Display', 'value': '6.1 OLED'}, ...]
    """
    if not specs_str:
        return []
    items = []
    tokens = str(specs_str).split('|')
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        if ':' in token:
            parts = token.split(':', 1)
            items.append({'label': parts[0].strip(), 'value': parts[1].strip()})
        else:
            items.append({'label': 'Feature', 'value': token})
    return items


def get_offers_for_product(product_id: int):
    """
    Retrieves all active store offers for a given product ID,
    joining the store details and calculating the final comparable price.
    """
    conn = get_db_connection()
    query = """
        SELECT 
            o.id,
            o.product_id,
            o.store_id,
            o.price_paise,
            o.delivery_charge_paise,
            (o.price_paise + o.delivery_charge_paise) AS total_paise,
            o.offer_url,
            o.is_in_stock,
            o.last_updated,
            s.name AS store_name,
            s.website_url AS store_website,
            s.logo_color
        FROM offers o
        JOIN stores s ON o.store_id = s.id
        WHERE o.product_id = ? AND o.is_active = 1
        ORDER BY total_paise ASC;
    """
    rows = conn.execute(query, (product_id,)).fetchall()
    conn.close()
    return rows


def get_offer_by_id(offer_id: int):
    """
    Fetches a single offer record by ID joined with its store metadata.
    """
    conn = get_db_connection()
    query = """
        SELECT o.*, s.name AS store_name, s.website_url AS store_website, s.logo_color
        FROM offers o
        JOIN stores s ON o.store_id = s.id
        WHERE o.id = ?;
    """
    row = conn.execute(query, (offer_id,)).fetchone()
    conn.close()
    return row


def get_price_history(product_id: int):
    """
    Retrieves historical price checkpoints for a product ordered chronologically.
    """
    conn = get_db_connection()
    query = """
        SELECT ph.id, ph.product_id, ph.store_id, ph.price_paise, ph.delivery_charge_paise,
               (ph.price_paise + ph.delivery_charge_paise) AS total_paise,
               ph.recorded_at, s.name AS store_name
        FROM price_history ph
        JOIN stores s ON ph.store_id = s.id
        WHERE ph.product_id = ?
        ORDER BY ph.recorded_at ASC;
    """
    rows = conn.execute(query, (product_id,)).fetchall()
    conn.close()
    return rows


def verify_admin_credentials(username: str, password: str) -> bool:
    """
    Verifies admin credentials using secure one-way password hashing (scrypt/PBKDF2).
    """
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM admin_users WHERE username = ?;", (username.strip(),)).fetchone()
    conn.close()
    if not user:
        return False
    return check_password_hash(user['password_hash'], password)


def get_all_stores():
    """Returns all stores for dropdown selectors."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM stores ORDER BY name ASC;").fetchall()
    conn.close()
    return rows


def get_dashboard_stats():
    """Returns count metrics for the administrative dashboard."""
    conn = get_db_connection()
    p_count = conn.execute("SELECT COUNT(*) FROM products;").fetchone()[0]
    s_count = conn.execute("SELECT COUNT(*) FROM stores;").fetchone()[0]
    o_count = conn.execute("SELECT COUNT(*) FROM offers;").fetchone()[0]
    h_count = conn.execute("SELECT COUNT(*) FROM price_history;").fetchone()[0]
    conn.close()
    return {
        'products_count': p_count,
        'stores_count': s_count,
        'offers_count': o_count,
        'history_count': h_count
    }


def add_product(name: str, brand: str, category: str, description: str, specifications: str, image_url: str) -> int:
    """Adds a new product using parameterized SQL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO products (name, brand, category, description, specifications, image_url)
           VALUES (?, ?, ?, ?, ?, ?);""",
        (name.strip(), brand.strip(), category.strip(), description.strip(), specifications.strip(), image_url.strip())
    )
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return product_id


def update_product(product_id: int, name: str, brand: str, category: str, description: str, specifications: str, image_url: str):
    """Updates an existing product."""
    conn = get_db_connection()
    conn.execute(
        """UPDATE products 
           SET name = ?, brand = ?, category = ?, description = ?, specifications = ?, image_url = ?
           WHERE id = ?;""",
        (name.strip(), brand.strip(), category.strip(), description.strip(), specifications.strip(), image_url.strip(), product_id)
    )
    conn.commit()
    conn.close()


def delete_product(product_id: int):
    """Deletes a product; ON DELETE CASCADE automatically removes its offers and history."""
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?;", (product_id,))
    conn.commit()
    conn.close()


def add_offer(product_id: int, store_id: int, price_paise: int, delivery_charge_paise: int, offer_url: str, in_stock: int = 1):
    """Adds or updates an offer, recording a new price observation into price_history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO offers (product_id, store_id, price_paise, delivery_charge_paise, offer_url, is_in_stock)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(product_id, store_id) DO UPDATE SET
               price_paise = excluded.price_paise,
               delivery_charge_paise = excluded.delivery_charge_paise,
               offer_url = excluded.offer_url,
               is_in_stock = excluded.is_in_stock,
               last_updated = CURRENT_TIMESTAMP;""",
        (product_id, store_id, price_paise, delivery_charge_paise, offer_url.strip(), in_stock)
    )
    # Record into price history
    cursor.execute(
        """INSERT INTO price_history (product_id, store_id, price_paise, delivery_charge_paise)
           VALUES (?, ?, ?, ?);""",
        (product_id, store_id, price_paise, delivery_charge_paise)
    )
    conn.commit()
    conn.close()


def delete_offer(offer_id: int):
    """Deletes an offer by ID."""
    conn = get_db_connection()
    conn.execute("DELETE FROM offers WHERE id = ?;", (offer_id,))
    conn.commit()
    conn.close()

