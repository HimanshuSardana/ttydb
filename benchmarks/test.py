import sqlite3
from ollama import chat
from pydantic import BaseModel

# --- Schema Setup ---
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE Products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL,
        status TEXT NOT NULL
    )
""")

sample_data = [
    ("Laptop", "Electronics", 999.99, 10, "IN_STOCK"),
    ("Smartphone", "Electronics", 699.99, 0, "OUT_OF_STOCK"),
    ("Coffee Maker", "Home Appliances", 79.99, 25, "IN_STOCK"),
    ("Headphones", "Electronics", 149.99, 5, "IN_STOCK"),
    ("Microwave", "Home Appliances", 120.00, 2, "DISCONTINUED"),
    ("Blender", "Home Appliances", 45.00, 15, "IN_STOCK"),
    ("Desk Chair", "Furniture", 199.99, 7, "IN_STOCK"),
    ("Bookshelf", "Furniture", 89.99, 0, "OUT_OF_STOCK"),
]
cursor.executemany(
    "INSERT INTO Products (product_name, category, price, stock_quantity, status) VALUES (?, ?, ?, ?, ?)",
    sample_data
)
conn.commit()

# --- Structured Output Model ---
class SQLResponse(BaseModel):
    sql: str
    explanation: str

def generate_sql(nl_query):
    schema_hint = """
Database schema:
Table: Products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock_quantity INTEGER NOT NULL,
    status TEXT NOT NULL
)
"""
    response = chat(
        messages=[
            {
                'role': 'user',
                'content': schema_hint + f"\nConvert the following request into SQL and explain it:\n{nl_query}",
            }
        ],
        model="text2sql",
        format=SQLResponse.model_json_schema(),
    )
    return SQLResponse.model_validate_json(response.message.content)

# --- Execute with retry ---
def execute_with_retry(nl_query, max_retries=5):
    attempt = 0
    last_exception = None

    while attempt < max_retries:
        attempt += 1
        print(f"\n[Attempt {attempt}] Generating SQL for: {nl_query}")
        sql_response = generate_sql(nl_query)

        sql_query = sql_response.sql.replace("WHEREING", "WHERE")
        print("Generated SQL:", sql_query)
        print("Explanation:", sql_response.explanation)

        try:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            print("✅ Query succeeded. Rows returned:", len(rows))
            return True  # Mark as correct
        except Exception as e:
            print("❌ Error executing SQL:", e)
            last_exception = e

    print("❌ Failed after retries. Last error:", last_exception)
    return False  # Mark as incorrect

# --- Benchmark Runner ---
def benchmark(queries):
    correct_count = 0
    for q in queries:
        if execute_with_retry(q):
            correct_count += 1
    total = len(queries)
    print(f"\n🏆 Benchmark Score: {correct_count}/{total} correct")

# --- Test Queries ---
queries = [
    "Which product has the highest price?",
    "List all products with price greater than 500.",
    "Show all categories along with the count of products in each.",
    "Find the average price of electronics.",
    "Get all products that are out of stock.",
    "Show products that are discontinued.",
    "Show all customer names and emails who placed an order in the last 30 days.",
    "Find the total sales amount for each product.",
    "List the top 5 products with the highest stock quantity.",
    "Get the average order amount per customer.",
    "Show the names of customers who have never placed an order.",
    "Retrieve all orders along with the customer name, ordered by order date descending.",
    "Find the product name and total revenue for each product, sorted from highest to lowest revenue.",
    "List all customers who ordered more than 5 different products."
]

benchmark(queries)

