import sqlite3
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Setup in-memory SQLite database and example table
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
    (1, "Laptop", "Electronics", 1200.0, 25, "Available"),
    (2, "Phone", "Electronics", 800.0, 0, "Available"),
    (3, "Desk Chair", "Furniture", 150.0, 5, "Available"),
    (4, "Pen", "Stationery", 2.5, 200, "Available"),
    (5, "Monitor", "Electronics", 300.0, 15, "Discontinued"),
]
cursor.executemany("INSERT INTO Products VALUES (?, ?, ?, ?, ?, ?)", sample_data)
conn.commit()
logging.info("SQLite database and Products table created and populated.")

# Define prompt template
template = """
Question: {question}

Answer format:
SQL Query:
<your SQL query here>

Explanation:
<your explanation here>
"""

prompt = ChatPromptTemplate.from_template(template)
model = OllamaLLM(model="text2sql")
chain = prompt | model

def run_sql_and_handle(question):
    logging.info(f"Received question: {question}")

    # Get model response
    response = chain.invoke({"question": question})
    logging.info("Model response received.")

    # Parse model output to extract SQL and Explanation
    try:
        sql_start = response.index("SQL Query:") + len("SQL Query:")
        explanation_start = response.index("Explanation:")
        sql_query = response[sql_start:explanation_start].strip()
        explanation = response[explanation_start + len("Explanation:"):].strip()
        logging.info(f"Extracted SQL query: {sql_query}")
        logging.info(f"Extracted explanation: {explanation}")
    except Exception as e:
        logging.error(f"Failed to parse model output: {e}")
        return {"error": "Failed to parse model output", "model_output": response}

    # Try running the SQL query
    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        logging.info("SQL query executed successfully.")
        
        return {
            "query": sql_query,
            "explanation": explanation,
            "result_columns": columns,
            "result_rows": rows,
            "error": None,
        }
    except sqlite3.Error as e:
        logging.error(f"SQL execution error: {e}")
        # On error, ask model to fix the query by giving error message
        fix_prompt = f"""
The following SQL query produced an error:

{sql_query}

Error message:
{str(e)}

Please provide a corrected SQL query only.
"""
        fix_response = model.invoke(fix_prompt).strip()
        logging.info("Received fix suggestion from model.")
        return {
            "query": sql_query,
            "explanation": explanation,
            "error": str(e),
            "fix_suggestion": fix_response,
        }

# Example usage
question = "List all products with price greater than 500."
result = run_sql_and_handle(question)

if result.get("error") is None:
    logging.info("Final successful result:")
    print("SQL Query:\n", result["query"])
    print("Explanation:\n", result["explanation"])
    print("Results:")
    print(result["result_columns"])
    for row in result["result_rows"]:
        print(row)
else:
    logging.warning("Encountered error with SQL execution:")
    print("Error running query:", result["error"])
    print("Original query:", result["query"])
    print("Model fix suggestion:", result["fix_suggestion"])

