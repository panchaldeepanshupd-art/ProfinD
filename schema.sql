-- ====================================================================
-- ProfinD Database Schema (SQLite3)
-- Compliant with ADBMS 3NF Normalization and Foreign Key Integrity
-- Currency is stored as exact integer paise (1 INR = 100 paise)
-- ====================================================================

PRAGMA foreign_keys = ON;

-- 1. Products Table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    specifications TEXT,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Stores Table (Online E-Commerce Retailers)
CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    website_url TEXT NOT NULL,
    logo_color TEXT DEFAULT '#2563eb',
    is_active INTEGER DEFAULT 1
);

-- 3. Offers Table (Store-specific Product Listings & Pricing)
CREATE TABLE IF NOT EXISTS offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    price_paise INTEGER NOT NULL CHECK (price_paise >= 0),
    delivery_charge_paise INTEGER DEFAULT 0 CHECK (delivery_charge_paise >= 0),
    offer_url TEXT NOT NULL,
    is_in_stock INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    CONSTRAINT uq_product_store UNIQUE(product_id, store_id)
);

-- 4. Price History Table (Historical Price Observations for Trend Analysis)
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    price_paise INTEGER NOT NULL CHECK (price_paise >= 0),
    delivery_charge_paise INTEGER DEFAULT 0 CHECK (delivery_charge_paise >= 0),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
);

-- 5. Admin Users Table (For Secure Portal Access)
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- Database Indexes for Query Optimization
-- ====================================================================
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_offers_product_id ON offers(product_id);
CREATE INDEX IF NOT EXISTS idx_price_history_lookup ON price_history(product_id, recorded_at);
