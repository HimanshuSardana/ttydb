from google import genai
from dotenv import load_dotenv
from google.genai import types
from pydantic import BaseModel, Field
import os
import json

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class Query(BaseModel):
    instruction: str = Field(..., description="The natural language instruction for the query. Do not enclose in quotes.")
    query: str = Field(..., description="The query corresponding to the natural language request. Do not enclose in quotes.")
    table_schema: str = Field(..., description="The schema of the table used in the query. Do not enclose in quotes.")
    explanation: str = Field(..., description="The explanation of the query. Do not enclose in quotes.")

class Generator:
    def __init__(self, topic):
        self.topic = topic
        self.client = genai.Client()

    def generate_data(self, num_rows):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
            You are a data generation model.

            Your task is to generate {num_rows} high-quality examples of text-to-SQL pairs for the topic: "{self.topic}".

            Each example must include the following fields:
            - instruction: A natural language question, request, or command.
            - query: A syntactically correct **SQLite-compatible** SQL query.
            - table_schema: The **relevant SQL table schema** used in the query. Include full schema (table and column names).
            - explanation: A brief, human-readable explanation of what the SQL query does.

            Constraints:
            - Use only SQL syntax supported by SQLite (e.g., no DATEDIFF; use `julianday()` or `DATE('now', ...)`).
            - Vary the complexity: include simple filters, joins, subqueries, aggregates, date operations, and edge cases.
            - Make sure table and column names are descriptive and realistic.
            - Do not return extra commentary or markdown. Return only a JSON list matching this Pydantic schema:
            """,
            config={
                'response_mime_type': 'application/json',
                'response_schema': list[Query],
            }
        )
        return json.loads(response.text)
