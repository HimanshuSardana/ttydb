from google import genai
from src.generator import Generator

topics = ["Basic Selection", "Filtering (WHERE clause)", "Joins", "Aggregation (GROUP BY)", "Window Functions", "Subqueries", "Set Operations", "Date and Time Functions"]

def main():
    for topic in topics:
        generator = Generator(topic)
        data = generator.generate_data(num_rows=10)
        print(f"Generated data for topic '{topic}':")
        print(data)
        break

if __name__ == "__main__":
    main()
