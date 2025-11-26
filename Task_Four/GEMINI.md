# Role: Senior Python AI Engineer – Study Notes Summarizer & Quiz Generator Agent

> Deliver a single, self-contained repo that turns any PDF into concise study notes + a customizable quiz.  
> Use only the OpenAI-Agents SDK (no openai library) wired to Gemini 2.0 Flash via the official OpenAI-compatible endpoint.

---

## 1. Tech Stack & Constraints (non-negotiable)

| Component        | Choice                                                                 |
|------------------|------------------------------------------------------------------------|
| LLM SDK          | openai-agents (latest)                                                 |
| Model            | gemini-2.0-flash                                                       |
| Base URL         | https://generativelanguage.googleapis.com/v1beta/openai/               |
| PDF parser       | pypdf                                                                  |
| Doc search       | Context7 MCP Docs Reader                                               |
| UI framework     | Streamlit                                                              |
| Python manager   | uv                                                                     |
| Code style       | Zero-bloat, no unused imports, no decorators                           |

---

## 2. What the Agent Must Do

1. Accept a PDF upload through Streamlit.  
2. Extract text using PyPDF.  
3. Generate a concise, clean, student-friendly summary in markdown.  
4. Save summary into memory/summaries.json.  
5. User chooses:
   - Quiz type: MCQ | Short | Mixed  
   - Number of questions: ≥ 3  
6. Generate quiz **from full raw text**, not the summary.  
7. Display quiz inside cards (MCQ gets A/B/C/D options).  
8. Allow download of both summary and quiz as JSON or PDF.

Folder layout:

| Path                    | Description                        |
| ----------------------- | ---------------------------------- |
| .env                    | GEMINI_API_KEY=…                   |
| pyproject.toml          | uv-managed dependencies            |
| main.py                 | Streamlit UI + agent calls         |
| tools.py                | SDK-compliant tools                |
| memory/summaries.json   | Auto-created memory store          |
| uploads/                | Temporary PDF cache                |
| README.md               | Setup instructions                 |

---

## 3. Tools (tools.py)

from openai_agents import tool
import pypdf, pathlib, uuid, json, datetime, os

@tool
def extract_pdf_text(file_path: str) -> str:
    """Extract plain text from a local PDF file."""
    reader = pypdf.PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

@tool
def generate_quiz(text: str, q_type: str, n: int) -> list[dict]:
    """
    Generate n quiz questions from the provided text.
    q_type: 'MCQ' | 'Short' | 'Mixed'
    Returns: list of dicts → {id, question, options?, answer}
    (Agent performs the real LLM work.)
    """
    return []

---

## 4. Agent Initialization (main.py)

import os, streamlit as st, pathlib, uuid, json, datetime
from openai_agents import Agent, OpenAI
from tools import extract_pdf_text, generate_quiz

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

agent = Agent(
    model="gemini-2.0-flash",
    tools=[extract_pdf_text, generate_quiz],
    system="You are a study assistant. Summarize clearly, then create accurate quizzes from the full text."
)

---

## 5. Streamlit Flow

1. st.file_uploader("Upload PDF", type="pdf") → save to uploads/  
2. “Summarize” button → extract text → agent creates summary → save to memory/summaries.json  
3. User picks quiz type (MCQ/Short/Mixed)  
4. User picks question count  
5. “Create Quiz” button → agent generates quiz from raw text  
6. Display quizzes as cards  
7. Download buttons for JSON/PDF

---

## 6. UI Requirements

• Header: “📘 Study Notes Summarizer & Quiz Generator”  
• Light gradient background  
• Cards with subtle shadow + rounded corners  
• Buttons: crimson red, darken 10% on hover  
• Spinner during LLM operations  
• Optional sidebar: history of previous PDFs

---

## 7. Testing Requirements

| Test | Expected |
|------|----------|
| Upload 1-page PDF | Summary appears within 5 seconds |
| Create Quiz (5 MCQ) | 5 cards with A/B/C/D options |
| Upload 200-page PDF | Summary remains concise |
| Wrong file type | Error toast |
| Missing key | Helpful exit message |

---

## 8. README Quick Start

uv venv && source .venv/bin/activate  
uv add streamlit pypdf openai-agents  
echo "GEMINI_API_KEY=your_key" > .env  
streamlit run main.py

---

## 9. Delivery Checklist

[ ] No openai library — only openai-agents  
[ ] Tools follow SDK structure  
[ ] Quiz generated from RAW text  
[ ] Summary stored in memory/summaries.json  
[ ] UI meets layout specs  

