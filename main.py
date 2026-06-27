from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

from urllib.parse import quote, urlparse
from typing import List, Dict
import json
import os

# =========================
# LOAD ENV
# =========================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =========================
# LOAD DOMAIN MAP
# =========================

with open("domains.json", "r", encoding="utf-8") as f:
    DOMAIN_MAP = json.load(f)


# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="Universal AI Backend"
)

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# REQUEST MODEL
# =========================

from typing import List, Dict

class Question(BaseModel):
    message: str
    domain: str
    history: List[Dict] = []

# =========================
# HEALTH CHECK
# =========================

@app.get("/")
def home():

    return {
        "status": "running",
        "service": "Universal AI Backend"
    }

# =========================
# CHAT
# =========================

@app.post("/chat")
def chat(question: Question):
    
# =========================
# LOAD KNOWLEDGE FOR DOMAIN
# =========================

domain = urlparse(question.domain).netloc.lower()

knowledge_file = DOMAIN_MAP.get(
    domain,
    "knowledge/alnoor_knowledge.txt"
)

with open(knowledge_file, "r", encoding="utf-8") as f:
    KNOWLEDGE = f.read()    
prompt = f"""
You are an AI Assistant.

Always answer only using the provided Knowledge Base.

Rules:

- Never invent information.
- If information is unavailable, politely ask the user to contact the business.
- Always answer in the same language as the user's message whenever possible.
- Be friendly, concise and professional.
- Return plain text only.
- Do not use markdown.
- Do not use ** symbols.
- Preserve URLs exactly as written.

If the knowledge base contains registration or ordering instructions, follow them naturally during the conversation.

Knowledge Base

{KNOWLEDGE}

User Message

{question.message}
"""

    messages = [
        {
            "role": "system",
            "content": "You are a professional AI Business Assistant."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    # Previous conversation
    for msg in question.history:
        if msg.get("role") in ["user", "assistant"]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    answer = response.choices[0].message.content

    whatsapp = None

    if "REGISTRATION SUMMARY" in answer or "ORDER SUMMARY" in answer:
        whatsapp = (
            "https://wa.me/34663430258?text="
            + quote(answer)
        )

    return {
        "status": "success",
        "answer": answer,
        "whatsapp": whatsapp
    }
