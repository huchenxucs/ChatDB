

tab_fruits = """
CREATE TABLE fruits (
    fruit_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    fruit_name TEXT NOT NULL,
    selling_price REAL,
    stock_quantity INTEGER,
    fruit_type TEXT,
    shelf_life INTEGER
);
"""

tab_customers = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    first_name TEXT,
    last_name TEXT,
    phone_number TEXT,
    email TEXT
);
"""

tab_suppliers = """
CREATE TABLE suppliers (
    supplier_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    supplier_name TEXT NOT NULL,
    contact_number TEXT,
    email TEXT
);
"""

tab_sales = """
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    customer_id INTEGER,
    sale_date DATE,
    total_price REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
"""

tab_sale_items = """
CREATE TABLE sale_items (
    sale_item_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    sale_id INTEGER NOT NULL,
    fruit_id INTEGER NOT NULL,
    quantity_sold INTEGER,
    price_per_item REAL,
    item_total_price REAL,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    FOREIGN KEY (fruit_id) REFERENCES fruits(fruit_id)
);
"""

tab_purchases = """
CREATE TABLE purchases (
    purchase_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    supplier_id INTEGER NOT NULL,
    purchase_date DATE,
    total_cost REAL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);
"""

tab_purchase_items = """
CREATE TABLE purchase_items (
    purchase_item_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    purchase_id INTEGER NOT NULL,
    fruit_id INTEGER NOT NULL,
    quantity_purchased INTEGER,
    cost_per_item REAL,
    item_total_cost REAL,
    FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id),
    FOREIGN KEY (fruit_id) REFERENCES fruits(fruit_id)
);
"""

tables = [tab_fruits, tab_customers, tab_suppliers, tab_sales, tab_sale_items, tab_purchases, tab_purchase_items]
