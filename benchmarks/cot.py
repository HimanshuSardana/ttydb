import sqlite3
from ollama import chat
from pydantic import BaseModel
import logging

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

logging.basicConfig(
    level=logging.INFO,  # Use INFO or WARNING to reduce verbosity
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

cursor.executescript("""
DROP TABLE IF EXISTS OrderDetails;
DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Customers;
DROP TABLE IF EXISTS Employees;

CREATE TABLE Employees (
    employee_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    hire_date TEXT NOT NULL
);

CREATE TABLE Customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE Products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock_quantity INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('IN_STOCK', 'OUT_OF_STOCK', 'DISCONTINUED'))
);

CREATE TABLE Orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    salesperson_id INTEGER, -- Can be NULL if sale is online/unassisted
    order_date TEXT NOT NULL,
    total_amount REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY (salesperson_id) REFERENCES Employees(employee_id)
);

CREATE TABLE Reviews (
    review_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    review_date TEXT NOT NULL,
    review_text TEXT,
    FOREIGN KEY (product_id) REFERENCES Products(product_id),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE OrderDetails (
    order_detail_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
""")
logger.info("Database schema created successfully.")

employees = [
    ("Jane", "Doe", "2024-03-15"),
    ("John", "Smith", "2023-11-20"),
    ("Emily", "Jones", "2025-08-01"),
]
cursor.executemany(
    "INSERT INTO Employees (first_name, last_name, hire_date) VALUES (?, ?, ?)",
    employees
)

customers = [
    ("Alice Johnson", "alice@example.com"),
    ("Bob Williams", "bob@example.com"),
    ("Charlie Brown", "charlie@example.com"),
    ("Diana Prince", "diana@example.com"),
]
cursor.executemany(
    "INSERT INTO Customers (name, email) VALUES (?, ?)",
    customers
)

products = [
    ("Laptop", "Electronics", 999.99, 50, "IN_STOCK"),
    ("Smartphone", "Electronics", 699.99, 0, "OUT_OF_STOCK"),
    ("Coffee Maker", "Home Appliances", 79.99, 30, "IN_STOCK"),
    ("Headphones", "Electronics", 149.99, 100, "IN_STOCK"),
    ("Blender", "Home Appliances", 45.00, 0, "DISCONTINUED"),
    ("Desk Lamp", "Furniture", 35.50, 25, "IN_STOCK"),
]
cursor.executemany(
    "INSERT INTO Products (product_name, category, price, stock_quantity, status) VALUES (?, ?, ?, ?, ?)",
    products
)

orders = [
    (1, 1, "2025-07-10", 1299.97),  # customer_id=1, salesperson_id=1
    (2, 2, "2025-07-15", 699.99),
    (1, None, "2025-07-20", 79.99),
    (3, 1, "2025-07-25", 289.98),
    (4, 2, "2025-07-28", 45.00),
]
cursor.executemany(
    "INSERT INTO Orders (customer_id, salesperson_id, order_date, total_amount) VALUES (?, ?, ?, ?)",
    orders
)

reviews = [
    (1, 1, 5, "2025-07-15", "An excellent machine with great battery life. Highly recommended!"),
    (2, 2, 3, "2025-07-18", "It's an okay smartphone, but the screen could be brighter."),
    (4, 1, 4, "2025-07-15", "Good sound quality for the price."),
    (6, 4, 1, "2025-07-30", "Terrible product. It broke on the first use."),
    (3, 1, 5, "2025-07-22", "Makes a perfect cup of coffee every time. Truly great!"),
]
cursor.executemany(
    "INSERT INTO Reviews (product_id, customer_id, rating, review_date, review_text) VALUES (?, ?, ?, ?, ?)",
    reviews
)

conn.commit()
logger.info("Sample data inserted successfully.")

def get_schema_and_samples(cursor, sample_limit=5):
    logging.info("Fetching database schema and sample data...")
    schema_info = "Database schema and sample data:\n\n"
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    logging.debug(f"Found tables: {tables}")
    
    for table in tables:
        schema_info += f"Table `{table}`:\n"
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        schema_info += " Columns:\n"
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            schema_info += f"  - {col_name} ({col_type})\n"
        
        cursor.execute(f"SELECT * FROM {table} LIMIT {sample_limit};")
        rows = cursor.fetchall()
        if rows:
            schema_info += " Sample rows:\n"
            for row in rows:
                schema_info += f"  {row}\n"
        else:
            schema_info += " Sample rows: (no rows)\n"
        schema_info += "\n"
    
    logging.info("Schema and sample data fetched successfully.")
    return schema_info


class SQLResponse(BaseModel):
    sql: str
    explanation: str

def generate_sql_with_context(nl_query, cursor, prev_sql=None, prev_error=None):
    schema_hint = get_schema_and_samples(cursor)
    
    if prev_sql is None:
        prompt_content = (
            schema_hint
            + f"\nConvert the following request into SQL and explain it:\n{nl_query}"
        )
    else:
        prompt_content = (
            schema_hint
            + f"\nThe last SQL query you generated was:\n{prev_sql}\n"
            + f"It caused this error when executed:\n{prev_error}\n"
            + "Please fix the SQL query accordingly, explain the fix, and output the new SQL."
        )

    # logging.debug(f"Prompt content for SQL generation:\n{prompt_content}")
    response = chat(
        messages=[{"role": "user", "content": prompt_content}],
        model="text2sql",
        format=SQLResponse.model_json_schema(),
    )
    return SQLResponse.model_validate_json(response.message.content)

def execute_with_retry(nl_query, cursor, max_retries=5):
    attempt = 0
    last_sql = None
    last_error = None

    while attempt < max_retries:
        attempt += 1
        print(f"\n[Attempt {attempt}] Generating SQL for: {nl_query}")
        sql_response = generate_sql_with_context(nl_query, cursor, prev_sql=last_sql, prev_error=last_error)
        sql_query = sql_response.sql.replace("WHEREING", "WHERE")  # Fix common typo if needed
        print("Generated SQL:", sql_query)
        print("Explanation:", sql_response.explanation)
        try:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            print("✅ Query succeeded. Rows returned:", len(rows))
            return True  # success
        except Exception as e:
            print("❌ Error executing SQL:", e)
            last_sql = sql_query
            last_error = str(e)

    print("❌ Failed after retries. Last error:", last_error)
    return False  # failed after all retries

def benchmark(queries, cursor):
    correct_count = 0
    for q in queries:
        if execute_with_retry(q, cursor):
            correct_count += 1
    total = len(queries)
    print(f"\nBenchmark Score: {correct_count}/{total} correct")

queries = [
    "Which product has the highest price?",
    "List all products with price greater than 500.",
    "Show all categories along with the count of products in each.",
    "Find the average price of electronics.",
    "Get all products that are out of stock.",

    # Additional queries:
    "List the top 5 products with the highest stock quantity.",
    "Show all customers who have placed at least one order.",
    "Find the total sales amount for each salesperson.",
    "Which employee has generated the most revenue in sales?",
    "List all orders placed by a specific customer, sorted by order date descending.",
    "Find the average rating for each product.",
    "Show all reviews for products in the 'Electronics' category.",
    "List customers who have never placed an order.",
    "Find products that have never received a review.",
    "Get the total quantity sold for each product.",
    "Which products have been ordered more than 100 times in total?",
    "Find the customers who left a 5-star review for a product they purchased.",
    "List employees hired after January 1, 2024, who have not made any sales yet.",
    "Show all orders with total amount greater than 1000.",
    "Find the most recent review for each product.",
    "List the names and emails of customers who bought a Laptop.",
    "Get the total revenue generated by each product category.",
    "Show all orders where the salesperson was not assigned (online sales).",
    "Find the average order amount per customer.",
]


if __name__ == "__main__":
    benchmark(queries, cursor)
