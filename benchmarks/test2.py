import sqlite3
from ollama import chat
from pydantic import BaseModel

# --- Schema Setup ---
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

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
    salesperson_id INTEGER,
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

# --- Populate Employees ---
employees = [
    ("Jane", "Doe", "2024-03-15"),
    ("John", "Smith", "2023-11-20"),
    ("Emily", "Jones", "2025-08-01"),
]
cursor.executemany(
    "INSERT INTO Employees (first_name, last_name, hire_date) VALUES (?, ?, ?)",
    employees
)

orders = [
    (1, 1, "2025-07-10", 1299.97),
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

# --- TOOL FUNCTIONS ---
def list_tables():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cursor.fetchall()]

def describe_table(table_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    return cursor.fetchall()

def sample_rows(table_name, limit=5):
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    return cursor.fetchall()

def validate_sql(sql_query):
    try:
        cursor.execute(sql_query)
        _ = cursor.fetchall()
        return {"valid": True, "rows": len(_)}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def search_schema(keyword):
    results = []
    for table in list_tables():
        cols = describe_table(table)
        matches = [c[1] for c in cols if keyword.lower() in c[1].lower()]
        if matches:
            results.append({table: matches})
    return results

# --- Response Model ---
class SQLResponse(BaseModel):
    sql: str
    explanation: str

# --- SQL Generation ---
def generate_sql(nl_query, prev_sql=None, error_message=None):
    schema_hint = f"Database currently has these tables: {list_tables()}\n\n"

    prompt = schema_hint + f"Convert the following request into SQL and explain it:\n{nl_query}"

    if prev_sql and error_message:
        prompt += f"\n\nThe previous SQL query was:\n{prev_sql}\nIt caused this error:\n{error_message}\n"
        prompt += "You can call tools like list_tables, describe_table, sample_rows, validate_sql, search_schema to check schema and fix errors."

    # Simulating "tool call" by letting the model request info
    # Here we intercept tool keywords and run them before returning
    response = chat(
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        model="text2sql",
        format=SQLResponse.model_json_schema(),
    )

    # If the model requests a tool call (e.g., "CALL: list_tables")
    content = response.message.content
    if "CALL:" in content:
        tool_call = content.split("CALL:")[1].strip()
        if tool_call.startswith("list_tables"):
            result = list_tables()
        elif tool_call.startswith("describe_table"):
            table_name = tool_call.split("(")[1].split(")")[0].strip("'\" ")
            result = describe_table(table_name)
        elif tool_call.startswith("sample_rows"):
            args = tool_call.split("(")[1].split(")")[0].split(",")
            table_name = args[0].strip("'\" ")
            limit = int(args[1]) if len(args) > 1 else 5
            result = sample_rows(table_name, limit)
        elif tool_call.startswith("validate_sql"):
            sql_arg = tool_call.split("(")[1].split(")")[0].strip("'\" ")
            result = validate_sql(sql_arg)
        elif tool_call.startswith("search_schema"):
            keyword = tool_call.split("(")[1].split(")")[0].strip("'\" ")
            result = search_schema(keyword)
        else:
            result = f"Unknown tool: {tool_call}"
        
        # Tell model the tool result and re-run
        return generate_sql(nl_query, prev_sql, f"Tool {tool_call} returned: {result}")

    return SQLResponse.model_validate_json(content)

# --- Retry Execution ---
def execute_with_retry(nl_query, max_retries=5):
    attempt = 0
    last_exception = None
    error_message = None
    prev_sql = None

    while attempt < max_retries:
        attempt += 1
        print(f"\n[Attempt {attempt}] Generating SQL for: {nl_query}")
        sql_response = generate_sql(nl_query, prev_sql, error_message)
        sql_query = sql_response.sql.strip().replace("WHEREING", "WHERE")

        print("Generated SQL:", sql_query)
        print("Explanation:", sql_response.explanation)

        try:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            print("✅ Query succeeded. Rows returned:", len(rows))
            return True
        except Exception as e:
            error_message = str(e)
            prev_sql = sql_query
            print("❌ Error executing SQL:", error_message)
            last_exception = e

    print("❌ Failed after retries. Last error:", last_exception)
    return False

# --- Benchmark ---
def benchmark(queries):
    correct_count = 0
    for q in queries:
        if execute_with_retry(q):
            correct_count += 1
    total = len(queries)
    print(f"\nBenchmark Score: {correct_count}/{total} correct")

# --- Test Queries ---
queries = [
    "Which product has the highest price?",
    "List all products with price greater than 500.",
    "Show all categories along with the count of products in each.",
    "Find the average price of electronics.",
    "Get all products that are out of stock.",
    "List the top 5 products with the highest stock quantity.",
]

benchmark(queries)

