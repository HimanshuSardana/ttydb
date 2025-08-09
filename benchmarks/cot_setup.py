import sqlite3

conn = sqlite3.connect('your_database.db')
cursor = conn.cursor()

# Create a sample Products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT,
    price REAL,
    stock_quantity INTEGER,
    status TEXT
);
""")

# Insert sample data
sample_data = [
    (1, 'Laptop', 'Electronics', 1200.0, 25, 'AVAILABLE'),
    (2, 'Mouse', 'Electronics', 25.0, 0, 'AVAILABLE'),
    (3, 'Desk Chair', 'Furniture', 150.0, 5, 'AVAILABLE'),
    (4, 'Monitor', 'Electronics', 300.0, 0, 'DISCONTINUED'),
    (5, 'Notebook', 'Stationery', 3.5, 100, 'AVAILABLE'),
]

cursor.executemany("""
INSERT OR IGNORE INTO Products (product_id, product_name, category, price, stock_quantity, status)
VALUES (?, ?, ?, ?, ?, ?)
""", sample_data)

conn.commit()
conn.close()
print("Sample database created and populated.")

