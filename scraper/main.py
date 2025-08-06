from google import genai
import csv
import logging
from src.generator import Generator

# print nothing except these logs
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s')

topics = ["Basic Selection", "Filtering (WHERE clause)", "Joins", "Aggregation (GROUP BY)", "Window Functions", "Subqueries", "Set Operations", "Date and Time Functions"]

def main():
    rows = 50
    for topic in topics:
        generator = Generator(topic)
        data = generator.generate_data(num_rows=rows)
        # print(data)

        with open(f"data.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Instruction", "Query", "Table Schema", "Explanation"])
            for item in data:
                writer.writerow([item['instruction'], item['query'], item['table_schema'], item['explanation']])
            logging.info(f"{rows} rows for topic '{topic}' written to data.csv")

if __name__ == "__main__":
    main()
