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