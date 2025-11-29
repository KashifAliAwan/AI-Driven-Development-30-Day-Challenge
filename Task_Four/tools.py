
import pypdf

def extract_pdf_text(file_path: str) -> str:
    """Extract plain text from a local PDF file."""
    reader = pypdf.PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def generate_quiz(text: str, q_type: str, n: int) -> list[dict]:
    """Generate quiz questions placeholder"""
    return []

