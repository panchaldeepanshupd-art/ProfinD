"""
ProfinD — Demo Data Seeder
Populates SQLite database with comprehensive, clearly labeled academic demo records.
Includes realistic price variations, delivery charge edge cases, and historical records.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
DB_PATH = os.path.join(DB_DIR, 'profind.db')
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')


def seed_database(reset=False):
    """
    Seeds the ProfinD database with verified demo products, retailers, offers, and price history.
    If reset=True, drops and recreates all tables.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    if reset:
        cursor.execute("DROP TABLE IF EXISTS price_history;")
        cursor.execute("DROP TABLE IF EXISTS offers;")
        cursor.execute("DROP TABLE IF EXISTS stores;")
        cursor.execute("DROP TABLE IF EXISTS products;")
        cursor.execute("DROP TABLE IF EXISTS admin_users;")

    # Apply Schema
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())

    # 1. Seed Admin User
    cursor.execute("SELECT COUNT(*) FROM admin_users;")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?);",
            ("admin", generate_password_hash("Admin@ProfinD2026"))
        )

    # 2. Seed Stores
    stores_data = [
        ("Amazon India", "https://www.amazon.in", "#ff9900"),
        ("Flipkart", "https://www.flipkart.com", "#2874f0"),
        ("Croma", "https://www.croma.com", "#00b2a9"),
        ("Reliance Digital", "https://www.reliancedigital.in", "#e42529")
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO stores (name, website_url, logo_color) VALUES (?, ?, ?);",
        stores_data
    )

    # 3. Comprehensive Products Catalog
    # Format: (name, brand, category, description, specifications, image_url)
    products_data = [
        (
            "Apple iPhone 15 (128 GB) - Blue",
            "Apple",
            "Smartphones",
            "Dynamic Island bubbles up alerts and Live Activities. 48MP main camera takes photos in super-high resolution. USB-C convenience.",
            "Display: 6.1-inch Super Retina XDR OLED | Chip: A16 Bionic | Storage: 128GB | Cameras: 48MP + 12MP Ultra-Wide | Port: USB-C",
            "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500&auto=format&fit=crop&q=80"
        ),
        (
            "Apple MacBook Air M2 (256 GB SSD) - Midnight",
            "Apple",
            "Laptops",
            "Redesigned around the next-generation M2 chip, MacBook Air is impossibly thin and brings exceptional speed and power efficiency.",
            "Display: 13.6-inch Liquid Retina | Chip: Apple M2 (8-core CPU, 8-core GPU) | Memory: 8GB Unified | Storage: 256GB SSD | Weight: 1.24 kg",
            "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&auto=format&fit=crop&q=80"
        ),
        (
            "Sony WH-1000XM5 Wireless Headphones - Silver",
            "Sony",
            "Audio",
            "Two processors control eight microphones for unprecedented noise cancellation. Auto NC Optimizer automatically optimizes noise cancelling based on wearing conditions.",
            "Form: Over-Ear | Battery Life: Up to 30 Hours | Quick Charge: 3 min for 3 hours | Driver: 30mm Carbon Fiber | Bluetooth: v5.2",
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop&q=80"
        ),
        (
            "Samsung Galaxy S24 5G (256 GB) - Onyx Black",
            "Samsung",
            "Smartphones",
            "Unleash new levels of creativity and productivity with Galaxy AI. 6.2-inch Dynamic AMOLED 2X with super-smooth 120Hz refresh rate.",
            "Display: 6.2-inch FHD+ 120Hz AMOLED | Chip: Exynos 2400 | RAM: 8GB | Storage: 256GB | Camera: 50MP OIS + 10MP Tele + 12MP Ultra-wide",
            "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&auto=format&fit=crop&q=80"
        ),
        (
            "Dell XPS 13 9315 Laptop (Intel Core i7, 16GB, 512GB SSD)",
            "Dell",
            "Laptops",
            "Dell's thinnest and lightest 13-inch XPS laptop is built for a lifestyle on the move. Long battery life and 12th Gen Intel Core performance.",
            "Display: 13.4-inch FHD+ 500 nits Anti-Glare | CPU: Intel Core i7-1250U | RAM: 16GB LPDDR5 | Storage: 512GB PCIe NVMe SSD | OS: Windows 11",
            "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500&auto=format&fit=crop&q=80"
        ),
        (
            "Apple AirPods Pro (2nd Generation) with MagSafe Case (USB-C)",
            "Apple",
            "Audio",
            "Up to 2x more Active Noise Cancellation than the previous generation. Transparency mode lets you comfortably hear the world around you.",
            "Chip: Apple H2 headphone chip | Battery: Up to 6 hours listening (30h with case) | Dust, Sweat and Water Resistant: IP54 | Port: USB-C",
            "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=500&auto=format&fit=crop&q=80"
        ),
        (
            "OnePlus 12 5G (256 GB) - Silky Black",
            "OnePlus",
            "Smartphones",
            "Powered by Snapdragon 8 Gen 3 with 4th Gen Hasselblad Camera System for Mobile. 5400mAh battery with 100W SUPERVOOC fast charging.",
            "Display: 6.82-inch 2K 120Hz ProXDR AMOLED | CPU: Snapdragon 8 Gen 3 | RAM: 12GB | Storage: 256GB | Battery: 5400 mAh, 100W charge",
            "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=500&auto=format&fit=crop&q=80"
        ),
        (
            "Apple Watch Series 9 GPS (41mm) - Starlight Aluminium",
            "Apple",
            "Wearables",
            "S9 SiP enables a magical new way to use your watch without touching the screen: Double Tap. Advanced health and safety sensors.",
            "Case: 41mm Aerospace-grade aluminum | Display: Always-On Retina up to 2000 nits | Sensors: Blood Oxygen, ECG, Temperature sensing",
            "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=500&auto=format&fit=crop&q=80"
        ),
        (
            "Apple iPad Air M2 11-inch (128 GB, Wi-Fi) - Space Grey",
            "Apple",
            "Tablets",
            "Freshly supercharged by the Apple M2 chip. Features a Liquid Retina display, new landscape camera, and all-day battery life.",
            "Display: 11-inch Liquid Retina | Chip: Apple M2 | Storage: 128GB | Cameras: 12MP Landscape Front + 12MP Back | Wi-Fi: Wi-Fi 6E",
            "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500&auto=format&fit=crop&q=80"
        ),
        (
            "ASUS ROG Zephyrus G14 Gaming Laptop (AMD Ryzen 9, RTX 4060)",
            "ASUS",
            "Laptops",
            "Ultraportable gaming beast featuring an OLED ROG Nebula Display and AI-accelerated AMD Ryzen processor inside a slim aluminum chassis.",
            "Display: 14-inch 3K 120Hz OLED | CPU: AMD Ryzen 9 8945HS | GPU: NVIDIA GeForce RTX 4060 8GB | RAM: 16GB LPDDR5X | Storage: 1TB SSD",
            "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500&auto=format&fit=crop&q=80"
        )
    ]

    cursor.execute("SELECT COUNT(*) FROM products;")
    existing_count = cursor.fetchone()[0]

    if existing_count < len(products_data):
        cursor.execute("DELETE FROM offers;")
        cursor.execute("DELETE FROM price_history;")
        cursor.execute("DELETE FROM products;")
        cursor.executemany(
            """INSERT INTO products (name, brand, category, description, specifications, image_url)
               VALUES (?, ?, ?, ?, ?, ?);""",
            products_data
        )

    # Retrieve inserted product IDs
    cursor.execute("SELECT id, name FROM products ORDER BY id ASC;")
    products_db = cursor.fetchall()
    prod_map = {row['name']: row['id'] for row in products_db}

    # 4. Realistic Offers with Delivery Edge Cases
    # Format: (product_name, store_id, price_paise, delivery_charge_paise, offer_url, in_stock)
    # Store IDs: 1=Amazon, 2=Flipkart, 3=Croma, 4=Reliance Digital
    offers_data = [
        # 1. iPhone 15:
        # Note edge case: Croma base is 65,499 (lowest base), but delivery is 1,000 => 66,499 total!
        # Amazon base is 65,999 + FREE delivery => 65,999 total. Amazon is CHEAPER in final total!
        (products_data[0][0], 1, 6599900, 0, "https://www.amazon.in/dp/B0CHX1W1XY", 1),
        (products_data[0][0], 2, 6649900, 0, "https://www.flipkart.com/apple-iphone-15-blue-128-gb/p/itmbf50ecd57392b", 1),
        (products_data[0][0], 3, 6549900, 100000, "https://www.croma.com/apple-iphone-15-128gb-blue/p/300652", 1),
        (products_data[0][0], 4, 6599900, 4900, "https://www.reliancedigital.in/apple-iphone-15-128-gb-blue/p/493839312", 1),

        # 2. MacBook Air M2:
        (products_data[1][0], 1, 8999000, 0, "https://www.amazon.in/dp/B0B3CQBRB4", 1),
        (products_data[1][0], 2, 8899000, 150000, "https://www.flipkart.com/apple-macbook-air-m2-8gb-256gb-ssd/p/itm1234567", 1),
        (products_data[1][0], 3, 8949000, 0, "https://www.croma.com/apple-macbook-air-m2-8gb-256gb/p/256711", 1),
        (products_data[1][0], 4, 9199000, 0, "https://www.reliancedigital.in/apple-macbook-air-m2/p/492850001", 1),

        # 3. Sony WH-1000XM5:
        (products_data[2][0], 1, 2699000, 0, "https://www.amazon.in/dp/B09XS7JWHH", 1),
        (products_data[2][0], 2, 2749000, 0, "https://www.flipkart.com/sony-wh-1000xm5/p/itm7891011", 1),
        (products_data[2][0], 3, 2699000, 0, "https://www.croma.com/sony-wh-1000xm5-bluetooth-headphone/p/262551", 1), # Equal lowest price tie!
        (products_data[2][0], 4, 2649000, 9900, "https://www.reliancedigital.in/sony-wh-1000xm5/p/492850381", 1),

        # 4. Samsung Galaxy S24:
        (products_data[3][0], 1, 7499900, 0, "https://www.amazon.in/dp/B0CQ28994N", 1),
        (products_data[3][0], 2, 7399900, 0, "https://www.flipkart.com/samsung-galaxy-s24-5g/p/itmabc123", 1), # Lowest
        (products_data[3][0], 3, 7449900, 0, "https://www.croma.com/samsung-galaxy-s24-5g/p/304123", 1),
        (products_data[3][0], 4, 7499900, 0, "https://www.reliancedigital.in/samsung-galaxy-s24-5g/p/493928192", 1),

        # 5. Dell XPS 13:
        (products_data[4][0], 1, 10999000, 0, "https://www.amazon.in/dp/B0B5GBW7M6", 1),
        (products_data[4][0], 2, 11249000, 0, "https://www.flipkart.com/dell-xps-13-intel-core-i7/p/itmxyz456", 1),
        (products_data[4][0], 3, 10899000, 200000, "https://www.croma.com/dell-xps-13-laptop/p/271892", 1),
        (products_data[4][0], 4, 10949000, 0, "https://www.reliancedigital.in/dell-xps-13/p/492850123", 1),

        # 6. Apple AirPods Pro 2:
        (products_data[5][0], 1, 2099900, 0, "https://www.amazon.in/dp/B0CHWRXH8B", 1),
        (products_data[5][0], 2, 2049900, 0, "https://www.flipkart.com/apple-airpods-pro-2nd-gen-type-c/p/itm8765432", 1), # Lowest
        (products_data[5][0], 3, 2099000, 0, "https://www.croma.com/apple-airpods-pro-2nd-gen/p/301124", 1),
        (products_data[5][0], 4, 2199000, 0, "https://www.reliancedigital.in/apple-airpods-pro-2/p/493839444", 1),

        # 7. OnePlus 12:
        (products_data[6][0], 1, 6499900, 0, "https://www.amazon.in/dp/B0CQPNW8V9", 1), # Lowest
        (products_data[6][0], 2, 6549900, 0, "https://www.flipkart.com/oneplus-12-silky-black-256-gb/p/itmded12345", 1),
        (products_data[6][0], 3, 6499900, 50000, "https://www.croma.com/oneplus-12-5g/p/304899", 1),
        (products_data[6][0], 4, 6599900, 0, "https://www.reliancedigital.in/oneplus-12-5g/p/494285912", 1),

        # 8. Apple Watch Series 9:
        (products_data[7][0], 1, 3799900, 0, "https://www.amazon.in/dp/B0CHX545TC", 1),
        (products_data[7][0], 2, 3849900, 0, "https://www.flipkart.com/apple-watch-series-9-gps/p/itmwatch9", 1),
        (products_data[7][0], 3, 3749900, 100000, "https://www.croma.com/apple-watch-series-9/p/300891", 1), # 37499 + 1000 = 38499
        (products_data[7][0], 4, 3799000, 0, "https://www.reliancedigital.in/apple-watch-series-9/p/493839555", 1),

        # 9. Apple iPad Air M2:
        (products_data[8][0], 1, 5699900, 0, "https://www.amazon.in/dp/B0D3J75F4M", 1),
        (products_data[8][0], 2, 5749000, 0, "https://www.flipkart.com/apple-ipad-air-6th-gen-11-inch/p/itmipadair6", 1),
        (products_data[8][0], 3, 5649000, 0, "https://www.croma.com/apple-ipad-air-m2-11-inch/p/306789", 1), # Lowest
        (products_data[8][0], 4, 5699000, 0, "https://www.reliancedigital.in/apple-ipad-air-11-m2/p/494392012", 1),

        # 10. ASUS ROG Zephyrus G14:
        (products_data[9][0], 1, 14999000, 0, "https://www.amazon.in/dp/B0CW1B9Y8F", 1),
        (products_data[9][0], 2, 14899000, 250000, "https://www.flipkart.com/asus-rog-zephyrus-g14-2024/p/itmrog14", 1), # 148990 + 2500 = 151490
        (products_data[9][0], 3, 14949000, 0, "https://www.croma.com/asus-rog-zephyrus-g14-gaming-laptop/p/305912", 1), # Lowest
        (products_data[9][0], 4, 15199000, 0, "https://www.reliancedigital.in/asus-rog-zephyrus-g14/p/494102919", 1)
    ]

    cursor.execute("DELETE FROM offers;")
    for prod_name, store_id, price_p, del_p, url, in_stock in offers_data:
        p_id = prod_map[prod_name]
        cursor.execute(
            """INSERT INTO offers (product_id, store_id, price_paise, delivery_charge_paise, offer_url, is_in_stock)
               VALUES (?, ?, ?, ?, ?, ?);""",
            (p_id, store_id, price_p, del_p, url, in_stock)
        )

    # 5. Historical Price Records (Spanning Past 30 Days)
    # Allows Phase 9 Price History analysis without inventing live data
    cursor.execute("DELETE FROM price_history;")
    history_records = []
    now = datetime.now()

    # Generate 4 historical checkpoints for each product (Day -30, Day -20, Day -10, Day -1)
    for prod_name, p_id in prod_map.items():
        # Representative base price
        if "iPhone 15" in prod_name:
            points = [(30, 6999900), (20, 6849900), (10, 6699900), (2, 6599900)]
        elif "MacBook Air" in prod_name:
            points = [(30, 9499000), (20, 9299000), (10, 9099000), (2, 8999000)]
        elif "WH-1000XM5" in prod_name:
            points = [(30, 2999000), (20, 2849000), (10, 2799000), (2, 2699000)]
        elif "Galaxy S24" in prod_name:
            points = [(30, 7999900), (20, 7799900), (10, 7599900), (2, 7399900)]
        elif "AirPods Pro" in prod_name:
            points = [(30, 2290000), (20, 2199000), (10, 2149000), (2, 2049900)]
        else:
            points = [(30, 5999900), (20, 5899900), (10, 5799900), (2, 5699900)]

        for days_ago, hist_price in points:
            hist_time = (now - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
            history_records.append((p_id, 1, hist_price, 0, hist_time))

    cursor.executemany(
        """INSERT INTO price_history (product_id, store_id, price_paise, delivery_charge_paise, recorded_at)
           VALUES (?, ?, ?, ?, ?);""",
        history_records
    )

    conn.commit()
    conn.close()
    print("Database successfully seeded with comprehensive demo catalog.")


if __name__ == '__main__':
    seed_database(reset=True)
