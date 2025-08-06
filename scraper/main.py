from google import genai
import csv
from src.generator import Generator

topics = ["Basic Selection", "Filtering (WHERE clause)", "Joins", "Aggregation (GROUP BY)", "Window Functions", "Subqueries", "Set Operations", "Date and Time Functions"]

def main():
    for topic in topics:
        generator = Generator(topic)
        data = generator.generate_data(num_rows=10)
        print(data)

        with open(f"data.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Instruction", "Query", "Table Schema", "Explanation"])
            for item in data:
                writer.writerow([item['instruction'], item['query'], item['table_schema'], item['explanation']])
            print(f"10 rows for topic '{topic}' written to data.csv")


if __name__ == "__main__":
    main()
