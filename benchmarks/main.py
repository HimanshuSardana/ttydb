import requests
import time
import json
import sqlparse
import logging
from jsonschema import validate, ValidationError

# --- Logging Setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("benchmark.log"),
        logging.StreamHandler()
    ]
)

# --- Ollama Config ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

# --- Structured Output Schema ---
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string"},
        "explanation": {"type": "string"}
    },
    "required": ["query", "explanation"]
}

# --- Sample NL Questions ---
questions = [
    "Show me the top 5 highest paid employees.",
    "List departments with more than 10 employees.",
    "Find the average salary per department.",
    "Who is the youngest employee?",
    "Show all employees hired in the last 2 years.",
    "Which employee has the highest salary?",
    "List employees who earn more than the average salary.",
    "Show number of employees in each department.",
    "Find employees with names starting with 'A'.",
    "Get all employees sorted by hire date."
]

# --- Table Schema (used in prompt) ---
TABLE_SCHEMA = "Employees(id INTEGER, name TEXT, salary DECIMAL, hire_date DATE, department TEXT)"

# --- Stats Trackers ---
durations = []
valid_responses = 0
invalid_json = 0
invalid_sql = 0
errors = 0

logging.info(f"🚀 Starting structured benchmark on model: {MODEL_NAME}")

# --- Benchmark Loop ---
for i, question in enumerate(questions, 1):
    logging.info(f"\n[{i}] Processing question: {question}")

    # Prompt designed to produce structured JSON
    prompt = f"""
Given the following table schema:

{TABLE_SCHEMA}

Write a valid SQL query to answer the question: "{question}"

Respond only with a JSON object matching this schema:
{json.dumps(RESPONSE_SCHEMA, indent=2)}
    """.strip()

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "format": "json",  # ← Forces true JSON output
        "stream": False
    }

    try:
        start_time = time.time()
        res = requests.post(OLLAMA_URL, json=payload)
        duration = time.time() - start_time
        durations.append(duration)

        logging.debug(f"[{i}] Raw response: {res.status_code}")
        res.raise_for_status()

        response = res.json().get("response", "")
        logging.debug(f"[{i}] Raw model output: {response}")

        try:
            response_json = json.loads(response)
        except json.JSONDecodeError:
            logging.error(f"[{i}] ❌ Failed to decode response as JSON.")
            invalid_json += 1
            continue

        # Validate JSON against schema
        try:
            validate(instance=response_json, schema=RESPONSE_SCHEMA)
        except ValidationError as ve:
            logging.error(f"[{i}] ❌ Response did not match schema.\n{json.dumps(response_json, indent=2)}")
            logging.debug(f"[{i}] Schema validation error: {ve}")
            invalid_json += 1
            continue

        # Check SQL validity (basic check)
        sql_query = response_json["query"]
        parsed = sqlparse.parse(sql_query)
        if not parsed or not sql_query.strip().lower().startswith("select"):
            logging.warning(f"[{i}] ⚠️ SQL might be invalid or unsupported:\n{sql_query}")
            invalid_sql += 1
        else:
            valid_responses += 1

        logging.info(f"[{i}] ✅ Valid response in {duration:.2f}s")
        logging.debug(f"[{i}] SQL Query:\n{sql_query}")
        logging.debug(f"[{i}] Explanation:\n{response_json['explanation']}")

    except Exception as e:
        logging.exception(f"[{i}] ❌ Request failed.")
        errors += 1

# --- Summary Report ---
total = len(questions)
logging.info("\n=== 🧾 Final Benchmark Report ===")
logging.info(f"Total Queries             : {total}")
logging.info(f"✅ Valid Structured Output : {valid_responses}")
logging.info(f"❌ Invalid JSON Structure  : {invalid_json}")
logging.info(f"⚠️ Potential SQL Issues     : {invalid_sql}")
logging.info(f"❌ Request Failures        : {errors}")
logging.info(f"⏱️ Avg Response Time       : {sum(durations)/total:.2f}s")
logging.info(f"⏱️ Fastest                 : {min(durations):.2f}s")
logging.info(f"⏱️ Slowest                 : {max(durations):.2f}s")

