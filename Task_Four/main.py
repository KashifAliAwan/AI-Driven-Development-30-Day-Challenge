import os
import streamlit as st
import pathlib
import uuid
import json
import datetime
import dotenv

from openai import OpenAI
from agents import Agent, Runner
from tools import extract_pdf_text

dotenv.load_dotenv()

# Check for GEMINI_API_KEY
# gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_api_key = os.getenv("OPENAI_API_KEY")
if not gemini_api_key:
    st.error("❌ GEMINI_API_KEY missing from .env file")
    st.stop()

# ---------------- CLIENT ----------------
client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# ---------------- AGENT -----------------
agent = Agent(
    name="study-assistant",
    model="gemini-2.0-flash",
    instructions="You are a study assistant. Summarize clearly and generate structured quizzes in valid JSON."
)

# ---------------- FILE PATHS -----------------
UPLOADS_DIR = pathlib.Path("uploads")
MEMORY_DIR = pathlib.Path("memory")
SUMMARIES_FILE = MEMORY_DIR / "summaries.json"

UPLOADS_DIR.mkdir(exist_ok=True)
MEMORY_DIR.mkdir(exist_ok=True)
if not SUMMARIES_FILE.exists():
    SUMMARIES_FILE.write_text("[]")

# ---------------- UI CONFIG -----------------
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: white;
    }

    h1, h2, h3, p, label {
        color: white !important;
    }

    .stButton>button {
        background-color: #e43f5a;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
    }

    .stButton>button:hover {
        background-color: #b83245;
    }

    .quiz-card {
        background-color: #1e1e2f;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
    }

    .sidebar .sidebar-content {
        background-color: #0f172a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📘 Study Notes Summarizer & Quiz Generator")

# ---------------- FILE UPLOAD -----------------
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    file_id = uuid.uuid4().hex
    file_path = UPLOADS_DIR / f"{file_id}.pdf"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ Uploaded {uploaded_file.name}")

    # ---------------- SUMMARIZE -----------------
    if st.button("Summarize PDF"):
        with st.spinner("Summarizing document..."):
            raw_text = extract_pdf_text(str(file_path))

            try:
                result = Runner.run_sync(agent, raw_text)
                summary = result.final_output if result else ""
            except Exception as e:
                st.error(f"Agent Error: {e}")
                summary = ""

            if summary:
                st.subheader("📝 Summary")
                st.markdown(summary)

                # Save summary memory
                with open(SUMMARIES_FILE, "r+") as f:
                    data = json.load(f)
                    data.append(
                        {
                            "id": file_id,
                            "filename": uploaded_file.name,
                            "timestamp": datetime.datetime.now().isoformat(),
                            "summary": summary,
                            "raw_text": raw_text
                        }
                    )
                    f.seek(0)
                    json.dump(data, f, indent=4)

                st.success("✅ Summary saved")
            else:
                st.error("❌ Failed to generate summary")

    # ---------------- QUIZ OPTIONS -----------------
    st.subheader("🧠 Create Quiz")
    quiz_type = st.selectbox("Quiz Type", ["MCQ", "Short", "Mixed"])
    num_questions = st.slider("Number of Questions", 3, 10, 5)

    if st.button("Generate Quiz"):
        with st.spinner("Creating quiz..."):
            raw_text_for_quiz = ""

            with open(SUMMARIES_FILE, "r") as f:
                data = json.load(f)
                for entry in data:
                    if entry["id"] == file_id:
                        raw_text_for_quiz = entry["raw_text"]
                        summary = entry["summary"]
                        break

            if not raw_text_for_quiz:
                st.error("❌ Please summarize first.")
            else:
                prompt = f"""
Generate a {quiz_type} quiz with {num_questions} questions from the text below.

Return ONLY valid JSON in this format:
[
  {{
    "question": "string",
    "options": {{"A": "", "B": "", "C": "", "D": ""}},
    "answer": "string"
  }}
]

TEXT:
{raw_text_for_quiz}
"""

                try:
                    result = Runner.run_sync(agent, prompt)
                    quiz_text = result.final_output
                    quiz_data = json.loads(quiz_text)
                except Exception as e:
                    st.error(f"Quiz failed: {e}")
                    quiz_data = []

                if quiz_data:
                    st.subheader("📋 Quiz")
                    for i, q in enumerate(quiz_data):
                        st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
                        st.markdown(f"**Q{i+1}: {q['question']}**")

                        if "options" in q:
                            for k, v in q["options"].items():
                                st.markdown(f"- **{k}**: {v}")

                        st.markdown(f"✅ **Answer:** {q['answer']}")
                        st.markdown("</div>", unsafe_allow_html=True)

                    # Downloads
                    st.subheader("💾 Download")

                    st.download_button(
                        "Download Summary",
                        json.dumps({"summary": summary}, indent=4),
                        f"summary_{file_id}.json",
                        "application/json"
                    )

                    st.download_button(
                        "Download Quiz",
                        json.dumps(quiz_data, indent=4),
                        f"quiz_{file_id}.json",
                        "application/json"
                    )
                else:
                    st.warning("⚠️ No quiz generated.")

# ---------------- SIDEBAR -----------------
st.sidebar.title("📂 History")
st.sidebar.write("Previous summaries coming soon.")
