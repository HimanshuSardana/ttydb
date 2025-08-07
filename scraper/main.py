from google import genai
import csv
import logging
from src.generator import Generator

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s')

for name in logging.root.manager.loggerDict:
    if "AFC" in name:
        logging.getLogger(name).setLevel(logging.WARNING)
        logging.getLogger(name).propagate = False

topics = [
    "Basic Column Selection and Aliasing",
    "Row Filtering with WHERE and Logical Operators",
    "INNER JOINs and Table Relationships",
    "LEFT JOINs and Emulated OUTER JOINs (for SQLite)",
    "Aggregations with GROUP BY and HAVING",
    "Window Functions (e.g., RANK, ROW_NUMBER, LAG, LEAD)",
    "Correlated and Uncorrelated Subqueries",
    "Set Operations: UNION, INTERSECT, EXCEPT",
    "Date and Time Functions (e.g., julianday, DATE())",
    "Sorting and Limiting Results (ORDER BY, LIMIT, OFFSET)",
    "IN, EXISTS, BETWEEN, and LIKE Operators",
    "Nested SELECTs in SELECT, FROM, or WHERE",
    "Handling NULLs: IS NULL, COALESCE, IFNULL",
    "Derived Tables and CTEs (WITH clauses)",
    "Case Expressions and Conditional Logic",
    "Schema Inference and Multi-Table Reasoning"
]

def main():
    rows = 30
    for topic in topics:
        generator = Generator(topic)
        data = generator.generate_data(num_rows=rows)
        # print(data)

        with open(f"data.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            # writer.writerow(["Instruction", "Query", "Table Schema", "Explanation"])
            for item in data:
                writer.writerow([item['instruction'], item['query'], item['table_schema'], item['explanation']])
            logging.info(f"{rows} rows for topic '{topic}' written to data.csv")

if __name__ == "__main__":
    main()
