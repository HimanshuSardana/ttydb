import logging
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import concurrent.futures
import sqlite3
from ollama import chat
from pydantic import BaseModel
from typing import Optional

# -----------------------
# Logging setup
# -----------------------
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG gives you the most detail; can switch to INFO in production
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = "data.db"

# --- SQLite setup ---
logger.info("Initializing in-memory SQLite database...")
conn = sqlite3.connect(":memory:", check_same_thread=False)
cursor = conn.cursor()

# --- Create tables ---
logger.debug("Creating tables...")
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
logger.info("Tables created successfully.")

# --- Insert sample data ---
# (You'd keep your insert statements here)
logger.info("Inserting sample data...")
# Your inserts...
logger.info("Sample data inserted.")

# --- Pydantic model ---
class SQLResponse(BaseModel):
    sql: str
    explanation: str

# --- Ollama wrapper ---
def _chat_call(prompt_content: str) -> SQLResponse:
    logger.debug(f"Sending prompt to Ollama model:\n{prompt_content}")
    response = chat(
        messages=[{"role": "user", "content": prompt_content}],
        model="text2sql",
        format=SQLResponse.model_json_schema(),
    )
    logger.debug(f"Raw model response: {response}")
    return SQLResponse.model_validate_json(response.message.content)

timeout_seconds = 60

def generate_sql(nl_query: str, prev_sql: Optional[str] = None, prev_error: Optional[str] = None) -> SQLResponse:
    schema_hint = """
    Database schema:
    Employees(employee_id, first_name, last_name, hire_date)
    Customers(customer_id, name, email)
    Products(product_id, product_name, category, price, stock_quantity, status)
    Orders(order_id, customer_id, salesperson_id, order_date, total_amount)
    Reviews(review_id, product_id, customer_id, rating, review_date, review_text)
    OrderDetails(order_detail_id, order_id, product_id, quantity, unit_price)
    """
    if prev_sql is None or prev_error is None:
        prompt_content = schema_hint + f"\nConvert to SQLite SQL and explain:\n{nl_query}"
    else:
        prompt_content = schema_hint + f"\nPrevious SQL:\n{prev_sql}\nError:\n{prev_error}\nOriginal request:\n{nl_query}\nFix the SQL."

    logger.info(f"Generating SQL for query: {nl_query}")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(_chat_call, prompt_content)
        return future.result(timeout=timeout_seconds)

def execute_with_retry(nl_query: str, max_retries=5):
    attempt = 0
    last_sql = None
    last_error = None

    while attempt < max_retries:
        attempt += 1
        logger.info(f"Attempt {attempt} for query: {nl_query}")
        try:
            sql_response = generate_sql(nl_query, prev_sql=last_sql, prev_error=last_error)
            sql_query = sql_response.sql.replace("WHEREING", "WHERE")
            logger.debug(f"Generated SQL: {sql_query}")
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            logger.info(f"Query executed successfully, returned {len(rows)} rows.")
            return {
                "success": True,
                "attempts": attempt,
                "sql": sql_query,
                "explanation": sql_response.explanation,
                "rows": rows
            }
        except Exception as e:
            last_sql = sql_query if 'sql_query' in locals() else None
            last_error = str(e)
            logger.error(f"Error on attempt {attempt}: {last_error}")

    logger.error(f"Max retries reached. Last error: {last_error}")
    return {
        "success": False,
        "attempts": attempt,
        "sql": last_sql,
        "error": last_error
    }

app = Flask(__name__)
CORS(app)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = file.filename

    if not filename.lower().endswith((".csv", ".json")):
        return jsonify({"error": "Only CSV or JSON files allowed"}), 400

    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_json(file)

        # Connect to SQLite
        conn = sqlite3.connect(DB_PATH)

        # Use filename (without extension) as table name
        table_name = os.path.splitext(filename)[0]
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        conn.close()
        return jsonify({
            "message": "File uploaded and stored in SQLite",
            "table": table_name,
            "rows": len(df)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/query", methods=["POST"])
def run_query():
    logger.info("Received /query request.")
    data = request.get_json()
    if not data or "nl_query" not in data:
        logger.warning("Missing 'nl_query' in request body.")
        return jsonify({"error": "Missing 'nl_query'"}), 400
    logger.debug(f"Request body: {data}")
    return jsonify(execute_with_retry(data["nl_query"]))

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(debug=True)

