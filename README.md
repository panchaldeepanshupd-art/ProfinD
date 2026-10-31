# ProfinD — Smart E-Commerce Product Price Comparison & Analysis System

An academic-grade, responsive, and database-connected web application developed for the **MCA Final-Semester AI/ML Capstone Project**.

---

## 1. Project Abstract
In modern digital commerce, consumers face significant price dispersion across competing online retailers (Amazon, Flipkart, Croma, Reliance Digital). Furthermore, misleading low base prices often mask compulsory shipping fees. **ProfinD** resolves this by automatically indexing retail offers, computing the true payable cost ($\text{Base Price} + \text{Delivery Fee}$), and executing an asymptotically optimal **$\mathcal{O}(n)$ Design and Analysis of Algorithms (DAA) Linear Scan** to mathematically guarantee the lowest comparable offer. Built strictly using Python, Flask, SQLite3, HTML5, CSS3, and JavaScript, the application maintains academic integrity with exact integer currency storage and prepared SQL security.

---

## 2. Technology Stack & Curriculum Mapping

| Curriculum Area | Technology Applied | Academic Competency Demonstrated |
| :--- | :--- | :--- |
| **Python & Web Framework** | Python 3.14, Flask 3.1, Jinja2, Werkzeug | WSGI micro-framework architecture, template inheritance, custom filters, session management |
| **Design & Analysis of Algorithms (DAA)** | Python algorithmic module (`price_comparison.py`) | Optimal $\mathcal{O}(n)$ Linear Scan Minimum, $\mathcal{O}(1)$ space, comparison counting vs $\mathcal{O}(n \log n)$ sorting |
| **Advanced Database Management Systems (ADBMS)** | SQLite3, `sqlite3.Row`, SQL DDL/DML | 3NF relational normalization, foreign key constraints (`ON DELETE CASCADE`), exact integer paise currency |
| **Advanced Internet Programming (AIP) & Frontend** | HTML5, CSS3 Grid/Flexbox, JavaScript | Accessible responsive web design, mobile navigation, client & server-side input validation |
| **Information Security** | Werkzeug Security, urllib parsing | Salted cryptographic password hashing (`scrypt`), SQL injection prevention, open-redirect defense |

---

## 3. Key Features

- **Responsive Homepage & Hero Search:** Modern brand identity, keyword search box with auto-validation, quick search tags, and dynamic featured products.
- **Product Catalog Search:** Case-insensitive search across names, brands, categories, and descriptions using parameterized SQL (`LIKE ?`).
- **Category Filter:** Instant filtering across Smartphones, Laptops, Audio, Wearables, and Tablets.
- **True Cost Price Comparison:** Evaluates Base Price + Delivery Charge so stores with lower base prices but high shipping fees are correctly identified as more expensive.
- **Tied Minimum Price Handling:** Accurately highlights all retailers sharing the identical lowest price.
- **30-Day Historical Price Analysis:** Tracks price checkpoints over time, calculating percentage change and directional purchase guidance.
- **Secure Deal Link Outbound Router:** Safe HTTP 302 redirection bridge with open-redirect and protocol attack filtering (`is_safe_url`).
- **Protected Administrator Dashboard:** Cryptographic session authentication (`@admin_required`), real-time metric cards, full CRUD capabilities for products and offers.
- **Custom Error Handling:** Styled 404 Not Found and 500 server error recovery.

---

## 4. Project Directory Layout

```text
ProfinD/
├── app.py                      # Main Flask application, routing & error handlers
├── database.py                 # SQLite3 database access layer & parameterized queries
├── price_comparison.py         # DAA O(n) minimum price algorithm & trend analyzer
├── seed_data.py                # Comprehensive academic demo catalog seeder
├── schema.sql                  # 3NF SQLite relational database schema
├── requirements.txt            # Locked Python dependency versions
├── README.md                   # Project documentation & setup guide
├── instance/
│   └── profind.db              # SQLite database (auto-generated at runtime)
├── static/
│   ├── css/
│   │   └── style.css           # Modern responsive styling & CSS variables
│   ├── js/
│   │   └── main.js             # Client-side validation & mobile navigation toggle
│   └── images/                 # Static graphical assets
├── templates/
│   ├── base.html               # Master Jinja2 layout (header, navbar, footer)
│   ├── index.html              # Homepage with hero, workflow, & featured cards
│   ├── products.html           # Product catalog with search & category filters
│   ├── product_details.html    # Full specifications, DAA analysis & price history
│   ├── compare.html            # Dedicated side-by-side comparison matrix
│   ├── about.html              # Project academic scope & syllabus mapping
│   ├── contact.html            # Project demonstration & candidate support info
│   ├── admin_login.html        # Secure admin sign-in with evaluation credentials
│   ├── admin_dashboard.html    # Management metrics, add product & add offer forms
│   └── 404.html                # Friendly custom 404 page
└── tests/
    ├── test_price_comparison.py # Automated DAA algorithmic unit tests (7 tests)
    └── test_routes.py          # Automated Flask routing & integration tests (11 tests)
```

---

## 5. Setup & Execution Instructions

### Prerequisites
- Python 3.10+ (Tested on Python 3.14.6)
- Git (Optional)
- Visual Studio Code or any modern code editor

### Step 1: Install Dependencies
Open your terminal in the `ProfinD` directory and run:
```powershell
pip install -r requirements.txt
```

### Step 2: Seed the Database (Optional — Auto-initializes on startup)
To populate or reset the database with the verified demo electronic catalog:
```powershell
python seed_data.py
```

### Step 3: Run the Automated Test Suites
Run all 18 automated unit and integration tests to verify system integrity:
```powershell
python -m unittest discover tests -v
```

### Step 4: Start the Local Development Server
```powershell
python app.py
```

### Step 5: Open in Web Browser
Navigate to:
```text
http://127.0.0.1:5000
```

---

## 6. Evaluation / Viva Credentials

To access and evaluate the **Administrative Portal**:
- **URL:** [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)
- **Username:** `admin`
- **Password:** `Admin@ProfinD2026`

---

## 7. DAA Algorithmic Specification

### The Problem
Given a collection of $n$ store offers $O = \{o_1, o_2, \dots, o_n\}$, where each offer $o_i$ has a base price $p_i \ge 0$ and a mandatory delivery fee $d_i \ge 0$, determine the offer $o^*$ that minimizes the total payable cost:
$$C(o_i) = p_i + d_i$$
$$o^* = \arg\min_{o_i \in O} C(o_i)$$

### The Solution: Linear Scan Minimum
```python
min_offer = valid_offers[0]
min_total = min_offer['computed_total_paise']

for offer in valid_offers[1:]:
    curr_total = offer['computed_total_paise']
    if curr_total < min_total:
        min_total = curr_total
        min_offer = offer
```

### Complexity Proof:
- **Comparisons:** Exactly $n - 1$ scalar comparisons for $n$ valid items.
- **Time Complexity:** $\Theta(n)$ in all cases (best, average, worst).
- **Auxiliary Space Complexity:** $\mathcal{O}(1)$ as only scalar memory references are tracked.
- **Why Sorting is Suboptimal:** Comparison-based sorting algorithms (Merge Sort, Timsort, Quicksort) take $\Omega(n \log n)$ time. Reordering all offers when only the minimum is needed is computationally wasteful.

---

## 8. License & Academic Disclaimer
Developed solely for academic evaluation, practical examination, and viva voce demonstration in the Master of Computer Applications (MCA) degree program. All retail store names and sample product prices are used strictly for demonstrative modeling.
