# StudyPilot AI

StudyPilot AI is a Flask-based study assistant that uses Google Gemini to answer questions, explain topics, generate study materials, and answer questions using text extracted from uploaded PDFs.

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Solution](#solution)
3. [Features](#features)
4. [Study Modes](#study-modes)
5. [How Questions and AI Solutions Work](#how-questions-and-ai-solutions-work)
6. [PDF Upload and Document Retrieval](#pdf-upload-and-document-retrieval)
7. [Technology Stack](#technology-stack)
8. [Project Structure](#project-structure)
9. [Installation](#installation)
10. [Environment Variables](#environment-variables)
11. [How to Run](#how-to-run)
12. [How to Use](#how-to-use)
13. [Example Questions and Solutions](#example-questions-and-solutions)
14. [Deployment](#deployment)
15. [Future Enhancements](#future-enhancements)
16. [Author](#author)

## Problem Statement

Students often need to switch between different resources to understand concepts, revise material, prepare for exams, and find answers in their study documents.

## Solution

StudyPilot AI provides a single study assistant powered by Gemini. Students can ask questions using different study modes and upload text-based PDFs for document-aware answers.

## Features

- AI-generated study responses using Google Gemini.
- Study modes for explanations, summaries, quizzes, revision, and planning.
- Adjustable response styles, from beginner-friendly to advanced.
- PDF text extraction and question-relevant document retrieval.
- Responses that include source filenames and page numbers when PDF context is used.
- Recent conversation context, stored in application memory.
- Document listing and clearing endpoints.
- PDF upload limit of 15 MB.

PDFs must contain extractable text. Scanned or image-only PDFs are not processed with OCR.

## Study Modes

StudyPilot AI currently defines these modes:

- `explain` — explains a topic step by step, with an example and summary.
- `summarize` — summarizes provided material or an uploaded PDF.
- `quiz` — creates five questions with answers and explanations.
- `improve` — reviews and improves a student's answer.
- `plan` — creates a practical study plan.
- `timetable` — organizes study into focused sessions and breaks.
- `simple` — explains a topic in beginner-friendly language.
- `keypoints` — extracts important exam revision points.
- `deep_analysis` — provides a structured, in-depth topic analysis.
- `exam_answer` — formats a response as a college exam answer.
- `adaptive_quiz` — prompts Gemini to adjust quiz difficulty based on the student's responses and conversation context.
- `teach_back` — prompts Gemini to evaluate a student's explanation and ask a follow-up question.
- `weak_topics` — prompts Gemini to identify possible areas for practice based on available context.
- `smart_revision` — creates a focused revision session.
- `concept_connections` — explains relationships between concepts.
- `study_roadmap` — organizes learning from prerequisites through revision.

These are prompt-based modes sent to Gemini; they are not separate AI models.

## How Questions and AI Solutions Work

1. The `/ask` endpoint receives a question, study mode, and answer style.
2. StudyPilot selects relevant PDF text when documents are available and builds a prompt with the question, mode instructions, answer style, recent conversation, and document context.
3. The prompt is sent to the configured Gemini model.
4. The generated answer and any document sources are returned as JSON.
5. The question and answer are added to in-memory conversation history, which retains up to ten messages.

When no PDF is available, Gemini is instructed to answer using general knowledge.

## PDF Upload and Document Retrieval

1. A PDF is uploaded to the `/upload` endpoint.
2. StudyPilot extracts text page by page using `pypdf`.
3. Text is cleaned and split into overlapping chunks of 1,600 characters, with 250 characters of overlap.
4. For a question, TF-IDF vectorization and cosine similarity rank relevant chunks. Up to six chunks are selected.
5. Selected text is included in the Gemini prompt. Responses return source filenames and page numbers.

For `summarize` mode, all stored chunks are selected before the document context is limited to 14,000 characters. If retrieval returns no results while documents are loaded, the application falls back to the first six chunks.

Uploaded documents and conversation history are stored in memory. They are lost when the application process restarts and are not shared between separate application workers.

## Technology Stack

- Python
- Flask 3.1.3
- Google Gemini API through `google-genai` 2.25.0
- `pypdf` 6.19.0 for PDF text extraction
- scikit-learn 1.9.1 for TF-IDF and cosine similarity
- NumPy 2.5.3
- `python-dotenv` 1.2.3
- Gunicorn 23.0.0 for deployment

## Project Structure

```text
STUDYPILOT-AI/
├── static/
│   ├── script.js
│   └── style.css
├── templates/
│   └── index.html
├── app.py
├── requirements.txt
├── .env
└── README.md
```

The `.env` file contains private configuration and must not be committed to GitHub.

## Installation

1. Install Python.
2. Open a terminal in the project root.
3. Create and activate a virtual environment:

   **Windows PowerShell**

       python -m venv .venv
       .\.venv\Scripts\Activate.ps1

4. Install the dependencies:

       pip install -r requirements.txt

The pinned dependencies are:

- Flask==3.1.3
- Werkzeug==3.1.8
- google-genai==2.25.0
- python-dotenv==1.2.3
- pypdf==6.19.0
- scikit-learn==1.9.1
- numpy==2.5.3
- gunicorn==23.0.0

## Environment Variables

Set the following environment variables for the application:

- `GEMINI_API_KEY` — your private Google Gemini API key.
- `PORT` — optional port number; defaults to `5000`.

For local development, place them in a root-level `.env` file:

    GEMINI_API_KEY=your_gemini_api_key
    PORT=5000

Keep `.env` private. Do not commit it to GitHub or include your API key in source code, documentation, or public deployment logs. Configure `GEMINI_API_KEY` as a private environment variable in Render.

## How to Run

With the virtual environment activated and environment variables configured, run:

    python app.py

The application listens on `0.0.0.0` and uses port `5000` by default. Open `http://127.0.0.1:5000` in your browser.

## How to Use

1. Open the application in your browser.
2. Enter a question or topic.
3. Select a study mode and answer style if those controls are available in the interface.
4. Upload a text-based PDF to ask questions about its contents.
5. To manage documents through the API:
   - `GET /documents` lists uploaded filenames and pages.
   - `POST /clear-documents` clears stored documents.
   - `GET /health` returns application health, AI name, model, and document count.

The `/ask` endpoint accepts JSON with `message`, `mode`, and `style` fields. For example:

    {
      "message": "Explain photosynthesis",
      "mode": "simple",
      "style": "beginner"
    }

The `/upload` endpoint accepts a PDF as a multipart form field named `file`.

## Example Questions and Solutions

These are example requests. Gemini's responses will vary.

**Question:** “Explain photosynthesis in simple language.”  
**Mode:** `simple`  
**Expected response:** A beginner-friendly explanation with a simple example.

**Question:** “Create a quiz about cell structure.”  
**Mode:** `quiz`  
**Expected response:** Five easy-to-medium questions, followed by answers and short explanations.

**Question about an uploaded PDF:** “Summarize the main ideas in this document.”  
**Mode:** `summarize`  
**Expected response:** A summary based on the supplied PDF text, with available document sources returned by the API.

## Deployment

StudyPilot AI is deployed using Render and Gunicorn.

For a Render web service:

1. Connect the project repository.
2. Set the build command to:

       pip install -r requirements.txt

3. Set the start command to:

       gunicorn app:app

4. Add `GEMINI_API_KEY` in the Render service's environment variables. Do not commit the `.env` file or add it to the repository.
5. Deploy the service.

The Flask application reads the `PORT` environment variable when started directly. Gunicorn and Render manage the production web process and port configuration.

The application currently runs with `debug=True` when started directly with `python app.py`. Use Gunicorn for deployment rather than the Flask development server.

## Future Enhancements

- Persist documents and conversation history between restarts.
- Add user sessions and isolate each user's documents and history.
- Add OCR support for scanned PDFs.
- Add automated tests and additional production monitoring.
- Improve retrieval for large document collections.

## Author

vidhya9719