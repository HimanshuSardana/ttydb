import sqlite3
from ollama import chat
from pydantic import BaseModel
from typing import Optional, Dict
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more verbosity
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup SQLite in-memory DB and cursor
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# Create schema and insert sample data
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
logger.info("Database schema created.")

# Insert sample data
employees = [
    ("Jane", "Doe", "2024-03-15"),
    ("John", "Smith", "2023-11-20"),
    ("Emily", "Jones", "2025-08-01"),
]
cursor.executemany(
    "INSERT INTO Employees (first_name, last_name, hire_date) VALUES (?, ?, ?)", employees
)

customers = [
    ("Alice Johnson", "alice@example.com"),
    ("Bob Williams", "bob@example.com"),
    ("Charlie Brown", "charlie@example.com"),
    ("Diana Prince", "diana@example.com"),
]
cursor.executemany(
    "INSERT INTO Customers (name, email) VALUES (?, ?)", customers
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
    "INSERT INTO Products (product_name, category, price, stock_quantity, status) VALUES (?, ?, ?, ?, ?)", products
)

orders = [
    (1, 1, "2025-07-10", 1299.97),  # customer_id=1, salesperson_id=1
    (2, 2, "2025-07-15", 699.99),
    (1, None, "2025-07-20", 79.99),
    (3, 1, "2025-07-25", 289.98),
    (4, 2, "2025-07-28", 45.00),
]
cursor.executemany(
    "INSERT INTO Orders (customer_id, salesperson_id, order_date, total_amount) VALUES (?, ?, ?, ?)", orders
)

reviews = [
    (1, 1, 5, "2025-07-15", "An excellent machine with great battery life. Highly recommended!"),
    (2, 2, 3, "2025-07-18", "It's an okay smartphone, but the screen could be brighter."),
    (4, 1, 4, "2025-07-15", "Good sound quality for the price."),
    (6, 4, 1, "2025-07-30", "Terrible product. It broke on the first use."),
    (3, 1, 5, "2025-07-22", "Makes a perfect cup of coffee every time. Truly great!"),
]
cursor.executemany(
    "INSERT INTO Reviews (product_id, customer_id, rating, review_date, review_text) VALUES (?, ?, ?, ?, ?)", reviews
)

conn.commit()
logger.info("Sample data inserted.")

# Models
class ToolCall(BaseModel):
    tool_name: str
    args: Dict[str, object]

class SQLResponse(BaseModel):
    sql: Optional[str] = None
    explanation: Optional[str] = None
    tool_call: Optional[ToolCall] = None

# Tools
def list_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cursor.fetchall()]

def describe_table(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name});")
    return cursor.fetchall()

def sample_rows(cursor, table_name, limit=5):
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
    return cursor.fetchall()

def get_schema_and_samples(cursor, sample_limit=5):
    logger.info("Fetching database schema and sample data for prompt context...")
    schema_info = "Database schema and sample data:\n\n"

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        schema_info += f"Table `{table}`:\n"
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        schema_info += " Columns:\n"
        for col in columns:
            cid, name, ctype, notnull, dflt_value, pk = col
            schema_info += f"  - {name} ({ctype})\n"
        cursor.execute(f"SELECT * FROM {table} LIMIT {sample_limit};")
        rows = cursor.fetchall()
        if rows:
            schema_info += " Sample rows:\n"
            for row in rows:
                schema_info += f"  {row}\n"
        else:
            schema_info += " Sample rows: (no rows)\n"
        schema_info += "\n"
    logger.info("Schema and samples fetched.")
    return schema_info

def run_tool_call(cursor, tool_call: ToolCall):
    tool = tool_call.tool_name
    args = tool_call.args

    logger.info(f"Running tool call: {tool} with args {args}")
    if tool == "list_tables":
        return {"tables": list_tables(cursor)}

    elif tool == "describe_table":
        table_name = args.get("table_name")
        if not table_name:
            return {"error": "Missing 'table_name' argument"}
        desc = describe_table(cursor, table_name)
        return {
            "description": [
                {"cid": c[0], "name": c[1], "type": c[2], "notnull": c[3], "default_value": c[4], "pk": c[5]}
                for c in desc
            ]
        }

    elif tool == "sample_rows":
        table_name = args.get("table_name")
        limit = int(args.get("limit", 5))
        if not table_name:
            return {"error": "Missing 'table_name' argument"}
        rows = sample_rows(cursor, table_name, limit)
        return {"rows": rows}

    else:
        return {"error": f"Unknown tool '{tool}'"}

def generate_sql_with_tools(
    nl_query,
    cursor,
    prev_sql=None,
    prev_error=None,
    tool_result=None,
    max_steps=5
):
    schema_hint = get_schema_and_samples(cursor)

    prompt_content = schema_hint
    prompt_content += "\nYou can call these tools by returning JSON with 'tool_call' key:\n"
    prompt_content += "- list_tables: no arguments\n"
    prompt_content += '- describe_table: {"table_name": "TABLE_NAME"}\n'
    prompt_content += '- sample_rows: {"table_name": "TABLE_NAME", "limit": NUMBER}\n'
    prompt_content += "Respond with JSON in one of these forms:\n"
    prompt_content += '{"tool_call": {"tool_name": "list_tables", "args": {}}, "explanation": "Explain..."}\n'
    prompt_content += '{"tool_call": {"tool_name": "describe_table", "args": {"table_name": "Products"}}, "explanation": "Explain..."}\n'
    prompt_content += '{"sql": "SELECT ...", "explanation": "Explain..."}\n\n'
    prompt_content += "You only have access to these 3 tools, do not invent any other tools"

    if prev_sql is None:
        prompt_content += f"Convert the following natural language request into SQL and explain it:\n{nl_query}"
    else:
        prompt_content += (
            f"The last SQL query you generated was:\n{prev_sql}\n"
            f"It caused this error:\n{prev_error}\n"
            f"The original question was: {nl_query}\n"
            f"Please fix the SQL or use tools to get more info, explain your reasoning."
        )

    if tool_result:
        prompt_content += f"\nTool output from last call:\n{json.dumps(tool_result)}"

    for step in range(max_steps):
        logger.info(f"[Step {step + 1}] Sending prompt to model...")
        response = chat(
            messages=[{"role": "user", "content": prompt_content}],
            model="text2sql",
            format=SQLResponse.model_json_schema(),
        )
        resp_text = response.message.content
        logger.info(f"Model response:\n{resp_text}")

        try:
            resp = SQLResponse.model_validate_json(resp_text)
        except Exception as e:
            logger.error(f"Failed to parse model response JSON: {e}")
            return False

        if resp.tool_call:
            logger.info(f"Model requested tool call: {resp.tool_call.tool_name} with args {resp.tool_call.args}")
            tool_output = run_tool_call(cursor, resp.tool_call)
            logger.info(f"Tool '{resp.tool_call.tool_name}' output: {tool_output}")
            logger.info(f"Tool '{resp.tool_call.tool_name}' output:\n{json.dumps(tool_output, indent=2)}")
            prompt_content += f"\nTool output:\n{json.dumps(tool_output)}\n"
            continue

        elif resp.sql:
            sql_query = resp.sql.replace("WHEREING", "WHERE")
            logger.info(f"Executing SQL:\n{sql_query}")
            try:
                cursor.execute(sql_query)
                rows = cursor.fetchall()
                logger.info(f"SQL executed successfully. Rows returned: {len(rows)}")
                return True
            except Exception as e:
                logger.error(f"SQL execution error: {e}")
                prev_sql = sql_query
                prev_error = str(e)
                prompt_content += f"\nSQL error: {prev_error}\nPlease fix the query."
                continue

        else:
            logger.error("No 'sql' or 'tool_call' found in model response.")
            return False

    logger.error("Max steps exceeded without success.")
    return False

def benchmark_with_tools(queries, cursor):
    correct_count = 0
    for q in queries:
        logger.info(f"Processing query: {q}")
        if generate_sql_with_tools(q, cursor):
            correct_count += 1
    total = len(queries)
    print(f"\nBenchmark Score: {correct_count}/{total} correct")

# Queries to test
queries = [
    "Which product has the highest price?",
    "List all products with price greater than 500.",
    "Show all categories along with the count of products in each.",
    "Find the average price of electronics.",
    "Get all products that are out of stock.",

    # More complex queries
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
    benchmark_with_tools(queries, cursor)

