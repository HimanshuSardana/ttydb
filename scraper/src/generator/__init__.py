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
            Generate {num_rows} pairs of NL and SQL queries for the topic '{self.topic}'.

            Generate NL, SQL, table scgema and explanation for each pair in JSON format:
            """,
            config={
                'response_mime_type': 'application/json',
                'response_schema': list[Query],
            }
        )
        return json.loads(response.text)
