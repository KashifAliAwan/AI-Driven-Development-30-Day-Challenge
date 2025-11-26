# 📘 Study Notes Summarizer & Quiz Generator

This project provides a Streamlit-based agent that summarizes PDF documents and generates customizable quizzes from their content.

## Quick Start

Follow these steps to set up and run the application:

1.  **Create and Activate Virtual Environment with uv:**
    If you don't have `uv` installed, you can install it using `pip install uv`.
    ```bash
    uv venv
    source .venv/bin/activate
    ```
    (On Windows, use `.venv\Scripts\activate` instead of `source .venv/bin/activate`)

2.  **Install Dependencies:**
    ```bash
    uv sync
    ```

3.  **Set Up API Key:**
    Create a `.env` file in the root directory of the project and add your Gemini API key:
    ```
    GEMINI_API_KEY=your_gemini_api_key_here
    ```
    Replace `your_gemini_api_key_here` with your actual API key.

4.  **Run the Streamlit Application:**
    ```bash
    streamlit run main.py
    ```

    Your browser should automatically open to the Streamlit application.

## Folder Structure

-   `.env`: Environment variables, including `GEMINI_API_KEY`.
-   `pyproject.toml`: `uv`-managed project dependencies.
-   `main.py`: Streamlit UI and agent calls.
-   `tools.py`: SDK-compliant tools (`extract_pdf_text`, `generate_quiz`).
-   `memory/summaries.json`: Auto-created memory store for summaries.
-   `uploads/`: Temporary cache for uploaded PDF files.
-   `README.md`: This setup instructions.

## How to Use

1.  Upload a PDF file using the "Upload PDF" button.
2.  Click "Summarize" to generate a concise summary of the PDF content.
3.  Choose your desired quiz type (MCQ, Short, Mixed) and the number of questions.
4.  Click "Create Quiz" to generate a quiz based on the full raw text of the uploaded PDF.
5.  Download options for both the summary and quiz will be available as JSON.
