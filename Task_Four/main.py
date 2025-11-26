import os
import streamlit as st
import pathlib
import uuid
import json
import datetime
import dotenv

from openai import OpenAI
from agents import Agent
from tools import extract_pdf_text, generate_quiz
dotenv.load_dotenv()

# Check for GEMINI_API_KEY
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    st.error("❌GEMINI_API_KEY missing from .env file")
    st.stop()

# --- Configuration and Initialization ---
# ---------------- CLIENT ----------------
client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

agent = Agent(
    model="gemini-2.0-flash",
    tools=[extract_pdf_text, generate_quiz],
    system="You are a study assistant. Summarize clearly, then create accurate quizzes from the full text."
)

# --- File Paths ---
UPLOADS_DIR = pathlib.Path("uploads")
MEMORY_DIR = pathlib.Path("memory")
SUMMARIES_FILE = MEMORY_DIR / "summaries.json"

UPLOADS_DIR.mkdir(exist_ok=True)
MEMORY_DIR.mkdir(exist_ok=True)
if not SUMMARIES_FILE.exists():
    SUMMARIES_FILE.write_text("[]")

# --- Streamlit UI ---
st.set_page_config(layout="wide")

# Header
st.markdown(
    """
    <style>
    .reportview-container {
        background: #f0f2f6; /* Light gray background */
        background: linear-gradient(to right, #f0f2f6, #e6e9ee); /* Light gradient */
    }
    .stApp {
        background: linear-gradient(to right, #f0f2f6, #e6e9ee);
    }
    .stButton>button {
        background-color: #DC143C; /* Crimson Red */
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #B20C2D; /* Darken 10% */
    }
    .quiz-card {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        padding: 20px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📘 Study Notes Summarizer & Quiz Generator")

# File uploader
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    file_id = uuid.uuid4().hex
    file_path = UPLOADS_DIR / f"{file_id}.pdf"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Uploaded {uploaded_file.name}")

    if st.button("Summarize"):
        with st.spinner("Extracting text and summarizing..."):
            raw_text = extract_pdf_text(str(file_path))
            
            # Agent for summarization
            # The agent's system prompt already instructs it to summarize.
            # We'll just pass the text and let it do its work.
            summary_response = agent.chat(raw_text)
            summary = summary_response.text

            if summary:
                st.subheader("Summary")
                st.markdown(summary)

                # Save summary to memory
                with open(SUMMARIES_FILE, "r+") as f:
                    summaries_data = json.load(f)
                    summaries_data.append({
                        "id": file_id,
                        "filename": uploaded_file.name,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "summary": summary,
                        "raw_text": raw_text # Store raw text for quiz generation
                    })
                    f.seek(0)
                    json.dump(summaries_data, f, indent=4)
                    st.success("Summary saved to memory.")
            else:
                st.error("Failed to generate summary.")

    # Quiz generation options
    st.subheader("Generate Quiz")
    quiz_type = st.selectbox("Select Quiz Type", ["MCQ", "Short", "Mixed"])
    num_questions = st.slider("Number of Questions", min_value=3, max_value=10, value=5)

    if st.button("Create Quiz"):
        with st.spinner("Generating quiz..."):
            # Retrieve raw text for quiz generation (from the last saved summary for the current file_id)
            # This assumes that a summary has been generated for the current file.
            raw_text_for_quiz = ""
            with open(SUMMARIES_FILE, "r") as f:
                summaries_data = json.load(f)
                for entry in summaries_data:
                    if entry["id"] == file_id:
                        raw_text_for_quiz = entry["raw_text"]
                        break
            
            if raw_text_for_quiz:
                # Use the agent to generate the quiz using the generate_quiz tool
                quiz_response = agent.chat(
                    f"Generate a {quiz_type} quiz with {num_questions} questions from the following text:",
                    tools_to_use=[generate_quiz],
                    text_content=raw_text_for_quiz,
                    q_type=quiz_type,
                    n=num_questions
                )
                
                quiz_data = quiz_response.tool_code_results[0]
                
                if quiz_data:
                    st.subheader("Quiz")
                    for i, q in enumerate(quiz_data):
                        st.markdown(f"<div class='quiz-card'>", unsafe_allow_html=True)
                        st.markdown(f"**Question {i+1}:** {q['question']}")
                        if "options" in q:
                            for option_key, option_value in q["options"].items():
                                st.markdown(f"**{option_key}:** {option_value}")
                        st.markdown(f"**Answer:** {q['answer']}")
                        st.markdown(f"</div>", unsafe_allow_html=True)

                    # Download options for summary and quiz
                    st.subheader("Download Options")
                    
                    # Placeholder for summary download
                    summary_json = "" # Will be replaced with actual summary from memory
                    for entry in summaries_data:
                        if entry["id"] == file_id:
                            summary_json = json.dumps({"summary": entry["summary"]}, indent=4)
                            break

                    if summary_json:
                        st.download_button(
                            label="Download Summary (JSON)",
                            data=summary_json,
                            file_name=f"summary_{file_id}.json",
                            mime="application/json"
                        )
                    
                    # Quiz download
                    quiz_json = json.dumps(quiz_data, indent=4)
                    st.download_button(
                        label="Download Quiz (JSON)",
                        data=quiz_json,
                        file_name=f"quiz_{file_id}.json",
                        mime="application/json"
                    )
                else:
                    st.error("Failed to generate quiz.")
            else:
                st.error("Raw text not found for quiz generation. Please summarize the document first.")

# Optional sidebar for history - placeholder for now
st.sidebar.subheader("History")
st.sidebar.write("Previous PDFs and summaries will appear here.")