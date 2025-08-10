import os
import sqlite3
import pandas as pd
import uuid
import concurrent.futures
from flask import Flask, request, jsonify
from flask_cors import CORS
from ollama import chat
from pydantic import BaseModel
from typing import Optional

DB_PATH = "data.db"
timeout_seconds = 60
uploaded_tables = []  # keep schema info for prompt

# --- Flask app ---
app = Flask(__name__)
CORS(app)

# --- Models ---
class SQLResponse(BaseModel):
    sql: str
    explanation: str

# --- DB utils ---
def clear_all_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for (table_name,) in tables:
        print(f"[DB] Dropping table: {table_name}")
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    conn.close()
    print("[DB] All tables cleared.")

def get_table_schema(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    schema_info = cursor.fetchall()
    conn.close()
    return schema_info

# --- Ollama wrapper ---
def _chat_call(prompt_content: str) -> SQLResponse:
    print(f"[LLM] Sending prompt:\n{prompt_content}")
    response = chat(
        messages=[{"role": "user", "content": prompt_content}],
        model="text2sql",
        format=SQLResponse.model_json_schema(),
    )
    return SQLResponse.model_validate_json(response.message.content)

def generate_sql(nl_query: str, prev_sql: Optional[str] = None, prev_error: Optional[str] = None) -> SQLResponse:
    # Build schema hint dynamically from uploaded tables
    schema_hint = "Database schema:\n"
    for t in uploaded_tables:
        schema_hint += f"{t['name']}({', '.join([col[1] for col in t['schema']])})\n"

    if prev_sql is None or prev_error is None:
        prompt_content = schema_hint + f"\nConvert to SQLite SQL and explain:\n{nl_query}"
    else:
        prompt_content = schema_hint + f"\nPrevious SQL:\n{prev_sql}\nError:\n{prev_error}\nOriginal request:\n{nl_query}\nFix the SQL."

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(_chat_call, prompt_content)
        return future.result(timeout=timeout_seconds)

def execute_with_retry(nl_query: str, max_retries=5):
    attempt = 0
    last_sql = None
    last_error = None

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    while attempt < max_retries:
        attempt += 1
        print(f"[QUERY] Attempt {attempt} for: {nl_query}")
        try:
            sql_response = generate_sql(nl_query, prev_sql=last_sql, prev_error=last_error)
            sql_query = sql_response.sql.replace("WHEREING", "WHERE")
            print(f"[QUERY] Generated SQL:\n{sql_query}")
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            print(f"[QUERY] Success. Returned {len(rows)} rows.")
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
            print(f"[ERROR] Attempt {attempt} failed: {last_error}")

    print(f"[ERROR] Max retries reached. Last error: {last_error}")
    return {
        "success": False,
        "attempts": attempt,
        "sql": last_sql,
        "error": last_error
    }

# --- API routes ---
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        print("[UPLOAD] No file in request.")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        print("[UPLOAD] Empty filename.")
        return jsonify({"error": "Empty filename"}), 400

    table_name = os.path.splitext(file.filename)[0]
    table_name = table_name.replace(" ", "_").replace("-", "_")
    table_name = f"{table_name}_{uuid.uuid4().hex[:6]}"

    try:
        if file.filename.lower().endswith(".csv"):
            df = pd.read_csv(file)
        elif file.filename.lower().endswith(".json"):
            df = pd.read_json(file)
        else:
            print("[UPLOAD] Unsupported format.")
            return jsonify({"error": "Only CSV and JSON supported"}), 400

        conn = sqlite3.connect(DB_PATH)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        print(f"[DB] Created table '{table_name}' with {len(df)} rows.")

        schema_info = get_table_schema(table_name)
        uploaded_tables.append({"name": table_name, "schema": schema_info})

        return jsonify({
            "message": "File uploaded successfully",
            "table_name": table_name,
            "schema": schema_info
        })
    except Exception as e:
        print(f"[ERROR] Upload failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/tables", methods=["GET"])
def list_tables():
    print(f"[API] Returning {len(uploaded_tables)} uploaded tables.")
    return jsonify(uploaded_tables)

@app.route("/query", methods=["POST"])
def run_query():
    data = request.get_json()
    if not data or "nl_query" not in data:
        print("[QUERY] Missing 'nl_query'.")
        return jsonify({"error": "Missing 'nl_query'"}), 400
    return jsonify(execute_with_retry(data["nl_query"]))

# --- Startup ---
if __name__ == "__main__":
    print("[INIT] Clearing existing tables...")
    clear_all_tables()
    print("[SERVER] Starting Flask app...")
    app.run(debug=True)

