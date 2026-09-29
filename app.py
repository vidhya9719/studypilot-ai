from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from pypdf import PdfReader

from google import genai
import os
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# STUDYPILOT CONFIGURATION
# ============================================================

load_dotenv()

app = Flask(__name__)

# Maximum PDF upload size = 15 MB
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY was not found in .env")

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# Confirmed working Gemini model
MODEL = "gemini-3.5-flash-lite"


# ============================================================
# STORAGE
# ============================================================

# Uploaded PDF chunks
DOCUMENTS = []

# Recent conversation
CONVERSATION_HISTORY = []


# ============================================================
# STUDY MODES
# ============================================================

PROMPTS = {

    # ---------------- EXISTING MODES ----------------

    "explain": """
Explain the topic clearly and accurately.

Start with a simple definition.
Then explain the idea step by step.
Use a small example when useful.
End with a short summary.
""",

    "summarize": """
Summarize the provided material.

Give:

1. Main idea
2. Important concepts
3. Key facts
4. Important formulas or steps if present
5. Short final revision summary

When a PDF is provided, summarize the PDF itself.
Do not replace the document with a general explanation.
""",

    "quiz": """
Create a useful study quiz about the topic.

Include:
- 5 questions
- A mixture of easy and medium questions
- Answers after the questions
- Short explanations for the answers
""",

    "improve": """
Improve the student's answer.

First identify what is correct.
Then explain what could be improved.
Finally provide a clearer improved answer.
""",

    "plan": """
Create a practical study plan for this topic.

Include:
- What to study first
- Important concepts
- Practice activities
- Revision
- A short self-test
""",

    "timetable": """
Create a realistic study timetable.

Break the work into focused study sessions.
Include short breaks.
Prioritize difficult topics.
Finish with revision and practice questions.
""",

    "simple": """
Explain the topic in very simple language.

Assume the student is a beginner.
Avoid unnecessary technical words.
Use a simple example if possible.
""",

    "keypoints": """
Extract the most important points for exam revision.

Use clear bullet points.
Include important definitions, concepts,
formulas, steps, examples, and exam tips when relevant.
""",

    # ---------------- ADVANCED MODES ----------------

    "deep_analysis": """
You are in Advanced Deep Analysis mode.

Analyze the student's topic deeply and systematically.

Include:

1. Core concept
2. Important sub-concepts
3. Step-by-step explanation
4. Relationships between concepts
5. Practical or technical example
6. Common mistakes and misconceptions
7. Important points for exams
8. Short final summary

Break complex ideas into understandable sections.
Use examples wherever useful.
""",

    "exam_answer": """
You are in Advanced Exam Answer mode.

Convert the student's question into a high-quality
college exam answer.

Use this structure when appropriate:

1. Definition
2. Introduction
3. Detailed explanation
4. Important points
5. Example
6. Diagram, table, algorithm, formula, or format when useful
7. Advantages, disadvantages, or applications when relevant
8. Conclusion

Make the answer technically accurate and suitable
for writing in an examination.
""",

    "adaptive_quiz": """
You are in Advanced Adaptive Quiz mode.

Create an interactive quiz that adapts to the student's
performance.

Start with a moderate-difficulty question.

Do not immediately reveal the answer if the student
is expected to answer interactively.

Evaluate the student's response when they provide one.
Explain what was correct or incorrect.
Adjust the next question's difficulty.

Move gradually from basic understanding to application
and analysis.

Use different question types such as:
- MCQ
- Short answer
- Conceptual questions
- Application questions

At the end, summarize performance and areas needing practice.
""",

    "teach_back": """
You are in Advanced Teach-Back mode.

Ask the student to explain the selected concept in
their own words.

Analyze their explanation and identify:

1. Correct understanding
2. Missing concepts
3. Incorrect statements
4. Confusing areas
5. Concepts that should be reviewed

Then explain the missing or incorrect parts and ask
a short follow-up question.

The goal is to verify actual understanding rather
than memorization.
""",

    "weak_topics": """
You are in Advanced Weak Topic Analysis mode.

Analyze the student's questions, answers, conversation
context, and uploaded study material when available.

Identify concepts that may require additional practice.

For each potential weak area provide:

1. Topic name
2. Evidence from the interaction
3. What appears difficult
4. What should be revised
5. Recommended practice activity
6. One practice question
7. Suggested difficulty level

Do not claim a topic is definitely weak without enough evidence.
""",

    "smart_revision": """
You are in Advanced Smart Revision mode.

Create a focused revision session for the student's topic.

Include:

1. Most important concepts
2. Key definitions
3. Important formulas, rules, or syntax
4. Important examples
5. Quick recall questions
6. Common mistakes
7. Frequently tested concepts
8. Short self-test
9. Final revision checklist

If a study document is provided, prioritize information
from that document.
""",

    "concept_connections": """
You are in Advanced Concept Connections mode.

Build a clear mental map of the student's topic.

Explain:

1. Main concept
2. Related concepts
3. Prerequisite concepts
4. How concepts depend on each other
5. Similar concepts
6. Differences between related concepts
7. Cause-and-effect relationships
8. Real-world or technical connections

Use a structured format or table when useful.
""",

    "study_roadmap": """
You are in Advanced Study Roadmap mode.

Create an ordered learning roadmap.

Organize it into:

1. Prerequisites
2. Basic concepts
3. Intermediate concepts
4. Advanced concepts
5. Practice exercises
6. Application-based practice
7. Revision
8. Self-test

For each stage explain:
- What to learn
- Why it matters
- What the student should be able to do afterward

Arrange everything from easier concepts to harder concepts.

If a study document is provided, use its contents
to make the roadmap relevant.
"""
}


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """Clean extracted text."""

    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# PDF CHUNKING
# ============================================================

def split_into_chunks(text, chunk_size=1600, overlap=250):
    """
    Split PDF text into overlapping chunks.
    """

    text = clean_text(text)

    if not text:
        return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


# ============================================================
# REMOVE OLD DOCUMENT
# ============================================================

def remove_old_document(filename):

    global DOCUMENTS

    DOCUMENTS = [
        item
        for item in DOCUMENTS
        if item["filename"] != filename
    ]


# ============================================================
# RETRIEVE RELEVANT PDF CHUNKS
# ============================================================

def retrieve_relevant_chunks(query, top_k=6):

    if not DOCUMENTS:
        return []

    query = clean_text(query)

    if not query:
        return []

    documents = [
        item["text"]
        for item in DOCUMENTS
    ]

    try:

        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        matrix = vectorizer.fit_transform(
            documents + [query]
        )

        document_vectors = matrix[:-1]
        query_vector = matrix[-1]

        similarities = cosine_similarity(
            query_vector,
            document_vectors
        ).flatten()

        ranked_indexes = similarities.argsort()[::-1]

        results = []

        for index in ranked_indexes[:top_k]:

            score = float(
                similarities[index]
            )

            item = DOCUMENTS[index].copy()

            item["score"] = round(
                score,
                3
            )

            results.append(item)

        return results

    except Exception as error:

        print(
            "RETRIEVAL ERROR:",
            type(error).__name__,
            str(error)
        )

        return []


# ============================================================
# GET ALL PDF CONTENT
# ============================================================

def get_all_document_chunks():

    if not DOCUMENTS:
        return []

    return [
        item.copy()
        for item in DOCUMENTS
    ]


# ============================================================
# BUILD DOCUMENT CONTEXT
# ============================================================

def build_document_context(results, max_chars=14000):

    if not results:
        return ""

    context_parts = []
    total_chars = 0

    for number, item in enumerate(
        results,
        start=1
    ):

        text = item["text"]

        source_text = f"""
SOURCE {number}
File: {item['filename']}
Page: {item['page']}

{text}
"""

        if total_chars + len(source_text) > max_chars:

            remaining = max_chars - total_chars

            if remaining > 200:

                source_text = source_text[:remaining]

                context_parts.append(
                    source_text
                )

            break

        context_parts.append(
            source_text
        )

        total_chars += len(source_text)

    return "\n".join(context_parts)


# ============================================================
# BUILD SOURCES
# ============================================================

def build_sources(results):

    sources = []

    seen = set()

    for item in results:

        key = (
            item["filename"],
            item["page"]
        )

        if key in seen:
            continue

        seen.add(key)

        sources.append({

            "filename":
                item["filename"],

            "page":
                item["page"]

        })

    return sources


# ============================================================
# ANSWER STYLE
# ============================================================

def get_answer_style(style):

    styles = {

        "beginner": """
Use beginner-friendly language.
Explain terms before using them.
Use simple examples.
Do not assume advanced knowledge.
""",

        "intermediate": """
Use clear academic language.
Assume the student understands basic concepts.
Include useful detail and examples.
""",

        "advanced": """
Give a deeper technical explanation.
Include important reasoning, relationships,
edge cases, formulas, and advanced details
when relevant.
""",

        "detailed": """
Give a detailed but organized explanation.
Use headings, examples, and step-by-step reasoning.
""",

        "simple": """
Keep the explanation simple and easy to understand.
"""
    }

    return styles.get(
        style,
        styles["intermediate"]
    )


# ============================================================
# CONVERSATION HISTORY
# ============================================================

def add_history(
    user_message,
    assistant_message
):

    global CONVERSATION_HISTORY

    CONVERSATION_HISTORY.append({

        "role": "user",

        "content": user_message

    })

    CONVERSATION_HISTORY.append({

        "role": "assistant",

        "content": assistant_message

    })

    if len(
        CONVERSATION_HISTORY
    ) > 10:

        CONVERSATION_HISTORY = (
            CONVERSATION_HISTORY[-10:]
        )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "ok",

        "ai": "Gemini",

        "model": MODEL,

        "documents": len(DOCUMENTS)

    })


# ============================================================
# LIST DOCUMENTS
# ============================================================

@app.route(
    "/documents",
    methods=["GET"]
)
def documents():

    files = {}

    for item in DOCUMENTS:

        filename = item["filename"]

        if filename not in files:

            files[filename] = {

                "filename":
                    filename,

                "pages":
                    set()

            }

        files[
            filename
        ]["pages"].add(
            item["page"]
        )

    result = []

    for filename, data in files.items():

        result.append({

            "filename":
                filename,

            "pages":
                sorted(
                    list(
                        data["pages"]
                    )
                )

        })

    return jsonify({

        "documents":
            result

    })


# ============================================================
# CLEAR DOCUMENTS
# ============================================================

@app.route(
    "/clear-documents",
    methods=["POST"]
)
def clear_documents():

    global DOCUMENTS

    DOCUMENTS = []

    return jsonify({

        "success":
            True,

        "message":
            "All documents cleared."

    })


# ============================================================
# PDF UPLOAD
# ============================================================

@app.route(
    "/upload",
    methods=["POST"]
)
def upload():

    try:

        if "file" not in request.files:

            return jsonify({

                "error":
                    "No file was selected."

            }), 400

        file = request.files["file"]

        if not file.filename:

            return jsonify({

                "error":
                    "No filename found."

            }), 400

        filename = file.filename

        if not filename.lower().endswith(".pdf"):

            return jsonify({

                "error":
                    "Please upload a PDF file."

            }), 400

        # Remove old copy
        remove_old_document(
            filename
        )

        reader = PdfReader(file)

        total_pages = len(
            reader.pages
        )

        if total_pages == 0:

            return jsonify({

                "error":
                    "The PDF contains no pages."

            }), 400

        added_chunks = 0
        extracted_characters = 0

        # ---------------------------------------------
        # Extract every page
        # ---------------------------------------------

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            try:

                text = page.extract_text()

            except Exception as page_error:

                print(
                    "PAGE EXTRACTION ERROR:",
                    type(page_error).__name__,
                    str(page_error)
                )

                text = ""

            text = clean_text(text)

            if not text:
                continue

            extracted_characters += len(
                text
            )

            chunks = split_into_chunks(
                text,
                chunk_size=1600,
                overlap=250
            )

            for chunk in chunks:

                DOCUMENTS.append({

                    "filename":
                        filename,

                    "page":
                        page_number,

                    "text":
                        chunk

                })

                added_chunks += 1

        # ---------------------------------------------
        # Check extraction
        # ---------------------------------------------

        if added_chunks == 0:

            return jsonify({

                "error":
                    (
                        "The PDF uploaded successfully, "
                        "but no readable text was found. "
                        "It may be a scanned/image-only PDF."
                    )

            }), 400

        print(
            "PDF UPLOADED:",
            filename
        )

        print(
            "PAGES:",
            total_pages
        )

        print(
            "CHUNKS:",
            added_chunks
        )

        print(
            "EXTRACTED CHARACTERS:",
            extracted_characters
        )

        return jsonify({

            "success":
                True,

            "filename":
                filename,

            "pages":
                total_pages,

            "chunks":
                added_chunks,

            "characters":
                extracted_characters,

            "message":
                (
                    f"{filename} is ready. "
                    "Ask me anything about this document."
                )

        })

    except Exception as error:

        print(
            "UPLOAD ERROR:",
            type(error).__name__,
            str(error)
        )

        return jsonify({

            "error":
                (
                    "Could not process the PDF. "
                    "Check the Flask terminal for details."
                )

        }), 500


# ============================================================
# ASK STUDYPILOT
# ============================================================

@app.route(
    "/ask",
    methods=["POST"]
)
def ask():

    try:

        data = (
            request.get_json(
                silent=True
            ) or {}
        )

        user_input = str(
            data.get(
                "message",
                ""
            )
        ).strip()

        mode = str(
            data.get(
                "mode",
                "explain"
            )
        ).strip().lower()

        style = str(
            data.get(
                "style",
                "intermediate"
            )
        ).strip().lower()

        if not user_input:

            return jsonify({

                "error":
                    "Please enter a question."

            }), 400

        # ====================================================
        # PDF CONTEXT
        # ====================================================

        retrieved = []

        # ----------------------------------------------------
        # SUMMARIZE + PDF
        # ----------------------------------------------------

        if DOCUMENTS and mode == "summarize":

            retrieved = get_all_document_chunks()

        else:

            retrieved = retrieve_relevant_chunks(
                user_input,
                top_k=6
            )

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if DOCUMENTS and not retrieved:

            retrieved = get_all_document_chunks()[:6]

        # ----------------------------------------------------
        # BUILD CONTEXT
        # ----------------------------------------------------

        document_context = build_document_context(
            retrieved,
            max_chars=14000
        )

        sources = build_sources(
            retrieved
        )

        # ====================================================
        # MODE INSTRUCTION
        # ====================================================

        mode_instruction = PROMPTS.get(

            mode,

            PROMPTS["explain"]

        )

        # ====================================================
        # ANSWER STYLE
        # ====================================================

        style_instruction = get_answer_style(
            style
        )

        # ====================================================
        # CONVERSATION HISTORY
        # ====================================================

        history_text = ""

        if CONVERSATION_HISTORY:

            recent_history = (
                CONVERSATION_HISTORY[-6:]
            )

            history_parts = []

            for message in recent_history:

                role = message[
                    "role"
                ].upper()

                content = message[
                    "content"
                ]

                history_parts.append(

                    f"{role}: {content}"

                )

            history_text = "\n".join(
                history_parts
            )

        # ====================================================
        # DOCUMENT INSTRUCTIONS
        # ====================================================

        if document_context:

            document_instruction = """
A PDF study document has been uploaded.

The text under UPLOADED DOCUMENT CONTEXT is extracted
from the actual uploaded PDF.

Use that document content as the primary source when
the student's request is about the uploaded PDF.

For summarization:
- Summarize the uploaded document content.
- Do not say that no PDF was uploaded.
- Do not guess what the PDF is about.
- Do not replace the PDF with unrelated general knowledge.
- Cover the important ideas actually present in the
  supplied document context.

For questions about the document:
- Answer from the supplied document context.
- If the requested information is not present,
  clearly say that it was not found in the uploaded
  document.

You may use general knowledge only when it helps explain
something, and clearly distinguish it from information
found in the document.
"""

        else:

            document_instruction = """
No PDF document is currently available.

Answer the student's question using general knowledge.

Do not mention a PDF unless the student asks about one.
Do not say that a PDF is likely related to the topic.
"""

        # ====================================================
        # FINAL PROMPT
        # ====================================================

        final_prompt = f"""
You are StudyPilot, an educational AI assistant.

Your job is to help students learn clearly and accurately.

{style_instruction}

{mode_instruction}

{document_instruction}

IMPORTANT RULES:

- Be accurate.
- Do not invent information.
- Do not claim a PDF contains information unless that
  information appears in the provided document context.
- If a PDF is provided and the user asks for a summary,
  summarize the actual provided PDF context.
- Use headings and bullet points when useful.
- Give examples when they improve understanding.
- For technical questions, show important steps.
- For exam questions, make the answer useful for revision.
- If the question is simple, answer it directly.
- Do not unnecessarily mention retrieval, chunks,
  embeddings, TF-IDF, or internal system details.

RECENT CONVERSATION:
{history_text if history_text else "No previous conversation."}

UPLOADED DOCUMENT CONTEXT:
{document_context if document_context else "No document context is available."}

STUDENT QUESTION:
{user_input}
"""

        # ====================================================
        # GEMINI
        # ====================================================

        system_instruction = """
You are StudyPilot AI.

You are a helpful educational assistant.

Be accurate, friendly, clear, and patient.

When document context is provided,
treat it as the primary source for
document-related requests.

Never claim that information came
from a document unless it appears
in the supplied document context.
"""

        full_prompt = f"""
SYSTEM INSTRUCTIONS:
{system_instruction}

STUDYPILOT REQUEST:
{final_prompt}
"""

        response = client.models.generate_content(

            model=MODEL,

            contents=full_prompt

        )

        # ====================================================
        # EXTRACT ANSWER
        # ====================================================

        answer = ""

        try:

            answer = response.text or ""

        except Exception:

            answer = ""

        answer = answer.strip()

        if not answer:

            answer = (
                "I could not generate an answer. "
                "Please try again."
            )

        # ====================================================
        # SAVE HISTORY
        # ====================================================

        add_history(
            user_input,
            answer
        )

        # ====================================================
        # SEND RESPONSE
        # ====================================================

        return jsonify({

            "response":
                answer,

            "sources":
                sources,

            "document_mode":
                bool(DOCUMENTS),

            "demo_mode":
                False,

            "ai":
                "Gemini",

            "model":
                MODEL

        })

    except Exception as error:

        print(
            "STUDYPILOT ERROR:",
            type(error).__name__,
            str(error)
        )

        return jsonify({

            "error":
                (
                    "StudyPilot could not connect "
                    "to Gemini. Please check your "
                    "GEMINI_API_KEY and try again."
                )

        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=int(
            os.getenv(
                "PORT",
                5000
            )
        ),

        debug=True

    )