# 📚 StudyPilot AI

> Study smarter. Understand better. Learn with AI. ✨

StudyPilot AI is an AI-powered study assistant designed to help students understand concepts, summarize material, generate quizzes, improve answers, prepare for exams, revise topics, identify areas for practice, create study plans, and learn from uploaded PDF documents.

It brings learning tools for explanations, summaries, quizzes, revision, document learning, and planning together in one platform, powered by Google Gemini.

## 🚀 Live Demo

**🌐 Live Website:**  
https://studypilot-ai.onrender.com

**💻 GitHub Repository:**  
https://github.com/vidhya9719/studypilot-ai

## 🎯 What is StudyPilot AI?

StudyPilot AI is a web-based study assistant for students. It provides different prompt-based learning modes for tasks such as understanding a topic, practicing questions, revising material, improving answers, and planning study sessions.

Students can also upload text-based PDFs and ask questions using their study material. These task-specific modes make StudyPilot AI more than a basic chatbot: the selected mode provides Gemini with instructions suited to the learning task.

## 💡 Problem Statement

Students may find it challenging to:

- Understand difficult concepts.
- Work through large amounts of study material.
- Identify important points for revision.
- Keep revision structured.
- Explain concepts clearly in their own words.
- Prepare exam-ready answers.
- Identify areas that may need more practice.
- Search large PDF notes manually.
- Manage different study tasks across multiple tools.

StudyPilot AI brings these learning tasks into one study-focused platform.

## ✨ Solution

Students select a study mode, enter a topic or question, and can upload a PDF for document-based learning. When relevant, StudyPilot retrieves document text and includes it as context in a prompt sent to Gemini.

```text
Student → Study Mode → Question/PDF → Document Retrieval when needed → Google Gemini → Learning Response
```

## 🧠 Key Features

| Feature | Description |
|---|---|
| Explain | Provides a step-by-step explanation of a topic. |
| Summarize | Summarizes a topic or provided study material. |
| Quiz | Generates five questions with answers and explanations. |
| Improve | Reviews and improves a student's answer. |
| Plan | Creates a practical study plan for a topic. |
| Timetable | Organizes study into focused sessions with breaks. |
| Simple | Explains a topic in beginner-friendly language. |
| Key Points | Extracts important points for revision. |
| PDF Learning | Retrieves relevant text from uploaded PDFs for question context. |
| Deep Analysis | Gives a structured analysis of a topic and related concepts. |
| Exam Answer | Structures a response in an exam-answer format. |
| Adaptive Quiz | Prompts Gemini to adjust quiz difficulty based on responses and context. |
| Teach-Back | Prompts Gemini to review a student's explanation and ask a follow-up question. |
| Weak Topic Analysis | Prompts Gemini to suggest potential areas for practice from available context. |
| Smart Revision | Creates a focused revision session with key concepts and a self-test. |
| Concept Connections | Explains relationships between concepts. |
| Study Roadmap | Organizes learning from prerequisites through revision. |

These modes guide Gemini with task-specific prompts; they are not separate AI models.

## 📚 Study Modes

### 🌱 Core Study Modes

| Mode | Purpose |
|---|---|
| Explain | Explain a topic step by step. |
| Summarize | Summarize provided material or a topic. |
| Quiz | Create questions with answers and explanations. |
| Improve | Review and improve a student's answer. |
| Plan | Create a practical study plan. |
| Timetable | Arrange study sessions and breaks. |
| Simple | Explain a topic in beginner-friendly language. |
| Key Points | Extract important revision points. |

### 🚀 Advanced Study Modes

| Mode | Purpose |
|---|---|
| Deep Analysis | Explore a topic, its sub-concepts, and common misconceptions. |
| Exam Answer | Structure a response for an exam. |
| Adaptive Quiz | Prompt Gemini to adjust quiz difficulty based on responses. |
| Teach-Back | Review a student's explanation and identify possible gaps. |
| Weak Topic Analysis | Suggest possible areas for practice based on available context. |
| Smart Revision | Create a focused revision session. |
| Concept Connections | Explain how related concepts connect. |
| Study Roadmap | Arrange learning stages from prerequisites to revision. |

## 📄 PDF Learning

Students can upload their own study PDFs and ask questions about their contents. StudyPilot uses PyPDF to extract page text, splits it into overlapping chunks, and uses TF-IDF retrieval with Scikit-learn to select relevant text for the Gemini prompt.

```text
Upload PDF → Extract Text → Chunk Text → TF-IDF Retrieval → Relevant Context → Gemini → Response
```

This can help students work with class notes, subject material, revision notes, and other study PDFs.

**Current limitations:**

- Text-based PDFs are supported.
- Scanned or image-only PDFs are not supported because OCR is not implemented.
- Uploaded documents are stored in application memory.
- Documents may need to be uploaded again after a server restart or redeployment.
- The application limits PDF uploads to 15 MB.

## 🔍 How It Works

The selected study mode determines the instructions included in the prompt sent to Gemini.

### Normal Questions

```text
User → Study Mode → Prompt → Gemini → Response
```

### PDF-Based Questions

```text
User + PDF → Text Extraction → Chunking → TF-IDF → Context → Gemini → Response
```

StudyPilot uses TF-IDF and cosine similarity for document retrieval. Uploaded documents and recent conversation history are held in application memory.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application programming language. |
| Flask | Backend web framework and API routes. |
| Google Gemini API | Generates AI learning responses. |
| HTML | Web page structure. |
| CSS | Web page styling. |
| JavaScript | Frontend interactions. |
| PyPDF | Extracts text from PDFs. |
| Scikit-learn | Provides TF-IDF and cosine-similarity retrieval. |
| TF-IDF | Helps rank PDF text chunks for a question. |
| Gunicorn | Production WSGI server. |
| Render | Application hosting and deployment. |

The configured Gemini model is `gemini-3.5-flash-lite`.

## 📁 Project Structure

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
├── README.md
└── .gitignore
```

- `app.py` — Flask application, Gemini integration, and API routes.
- `templates/index.html` — main page template.
- `static/script.js` — frontend JavaScript.
- `static/style.css` — page styling.
- `requirements.txt` — Python dependencies.
- `.env` — private local environment variables. **Never commit this file or expose its contents.**
- `.gitignore` — specifies files Git should ignore.
- `README.md` — project documentation.

## ⚙️ Installation

Clone the repository and open its project directory:

```bash
git clone https://github.com/vidhya9719/studypilot-ai.git
cd studypilot-ai
```

Create and activate a virtual environment on Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a root-level `.env` file for local development:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Use your own key. Keep `.env` private and do not commit it to GitHub.

## ▶️ Run Locally

With the virtual environment activated and `.env` configured, run:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## 📖 How to Use

1. Open the website.
2. Select a study mode.
3. Enter a question or topic.
4. Upload a PDF if you want to use your own study material.
5. Submit your request.
6. Read the generated response.
7. Try other modes for practice or revision.

Example requests:

- “Explain photosynthesis in simple language.”
- “Create a quiz about cell structure.”
- “Improve my answer about the causes of climate change.”
- Upload a text-based PDF and ask, “Summarize the main ideas in this document.”

Responses are generated by Gemini and may vary.

## 🔌 API Endpoints

The Flask application provides these routes:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Serves the main page. |
| `GET` | `/health` | Returns application health information. |
| `POST` | `/ask` | Sends a question, study mode, and answer style for an AI response. |
| `POST` | `/upload` | Uploads and processes a PDF. |
| `GET` | `/documents` | Lists uploaded document information. |
| `POST` | `/clear-documents` | Clears documents stored in application memory. |

## ☁️ Deployment

StudyPilot AI is deployed on Render using Gunicorn.

**Build command:**

```bash
pip install -r requirements.txt
```

**Start command:**

```bash
gunicorn app:app
```

Configure `GEMINI_API_KEY` as a private environment variable in the Render service. Do not commit `.env` or put a real API key in the repository.

Live deployment:

https://studypilot-ai.onrender.com

## ⚠️ Current Limitations

- OCR is not implemented, so scanned or image-only PDFs are not supported.
- PDF documents are stored in application memory.
- Documents may need to be uploaded again after a restart or redeployment.
- Gemini availability and usage limits can affect responses.

## 🔮 Future Enhancements

- Persistent document storage.
- OCR support for scanned documents.
- User accounts.
- Personalized study history.
- Progress tracking and performance analytics.
- Spaced repetition.
- Weak-topic visualization.
- Support for more document formats.
- Personalized learning recommendations.

## 🎓 Project Goal

StudyPilot AI demonstrates practical use of generative AI, prompt engineering, document processing, information retrieval, Flask, frontend development, and web application deployment.

## 💙 Why StudyPilot AI?

The goal is to make studying more structured by bringing understanding, practice, revision, document learning, and planning together in one place.

> Learn with purpose. Revise with confidence. Grow with every concept. ✨

## 👩‍💻 Author

**Vidhya**

**GitHub:**  
https://github.com/vidhya9719

**Repository:**  
https://github.com/vidhya9719/studypilot-ai

**Live Demo:**  
https://studypilot-ai.onrender.com