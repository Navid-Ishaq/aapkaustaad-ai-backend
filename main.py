from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

with open("alnoor_knowledge.txt", "r", encoding="utf-8") as f:
    KNOWLEDGE = f.read()

app = FastAPI()

class Question(BaseModel):
    message: str

@app.post("/chat")
def chat(question: Question):

    prompt = f"""
You are AL-NOOR Educational Centre Assistant.

Use ONLY the information below.

{KNOWLEDGE}

Student Question:
{question.message}
"""

    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {
                "role":"system",
                "content":"You are a helpful AL-NOOR assistant."
            },
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return {
        "answer": response.choices[0].message.content
    }