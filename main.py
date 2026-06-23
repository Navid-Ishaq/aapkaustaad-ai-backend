from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os

# =========================
# LOAD ENV
# =========================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =========================
# LOAD KNOWLEDGE
# =========================

with open("alnoor_knowledge.txt", "r", encoding="utf-8") as f:
    KNOWLEDGE = f.read()

# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="AL-NOOR AI Backend"
)

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aapkaustaad.com",
        "https://www.aapkaustaad.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# REQUEST MODEL
# =========================

class Question(BaseModel):
    message: str

# =========================
# HEALTH CHECK
# =========================

@app.get("/")
def home():
    return {
        "status": "running",
        "service": "AL-NOOR AI Backend"
    }

# =========================
# CHAT ENDPOINT
# =========================

@app.post("/chat")
def chat(question: Question):

    prompt = f"""
You are AL-NOOR Educational Centre Assistant.

Rules:
- Answer only from the provided knowledge.
- If information is not available, say:
  "Please contact AL-NOOR Educational Centre for further information."
- Respond in the same language as the student's question whenever possible.
- Be concise and helpful.

Knowledge Base:

{KNOWLEDGE}

Student Question:
{question.message}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AL-NOOR Educational Centre assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "answer": response.choices[0].message.content
    }
