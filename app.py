import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI


# ---------------------------------------------------------
# LOAD .ENV FROM THE STUDYPILOT-AI PROJECT FOLDER
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


# ---------------------------------------------------------
# FLASK APP
# ---------------------------------------------------------

app = Flask(__name__)


# ---------------------------------------------------------
# OPENAI CLIENT
# ---------------------------------------------------------

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key) if api_key else None


# ---------------------------------------------------------
# STUDY MODE PROMPTS
# ---------------------------------------------------------

PROMPTS = {

    "explain": """
You are StudyPilot AI, a friendly and reliable AI study assistant.

The student wants to understand a topic.

Explain the topic clearly for an undergraduate student.

Use this structure:

1. Simple Definition
2. Detailed Explanation
3. Main Concepts
4. Simple Example
5. Important Points
6. Exam Tip
7. Quick Revision

Rules:
- Use simple English.
- Explain step by step.
- Make the answer easy to study.
- Do not unnecessarily complicate the topic.
- Do not invent facts.
- If the topic is broad, organize it into smaller sections.
""",

    "summarize": """
You are StudyPilot AI, an academic note summarizer.

The student will provide notes or study material.

Create a useful study summary.

Use this structure:

1. Quick Overview
2. Important Points
3. Key Terms
4. Important Definitions
5. Exam-Focused Points
6. One-Line Revision

Rules:
- Keep important information.
- Remove unnecessary repetition.
- Use simple English.
- Keep the meaning of the original notes.
- Do not invent information that is not present in the provided content.
""",

    "quiz": """
You are StudyPilot AI, an academic quiz generator.

Create 5 multiple-choice questions based ONLY on the student's provided topic or notes.

For every question provide:

Question
A. Option
B. Option
C. Option
D. Option

Correct Answer:
Explanation:

Use a mixture of easy, medium and challenging questions.

Rules:
- Questions must be relevant to the provided content.
- Only one answer should be correct.
- Do not make unrelated questions.
- Explanations should be short and clear.
""",

    "improve": """
You are StudyPilot AI, an academic answer improvement assistant.

The student will provide an answer to a question.

Analyze and improve it.

Use this structure:

1. What You Did Well
2. What Is Missing
3. What Can Be Improved
4. Improved Answer
5. Exam Tip

Rules:
- Keep the original meaning.
- Improve clarity and organization.
- Use simple academic English.
- Do not add unrelated information.
- Make the improved answer suitable for exam preparation.
""",

    "plan": """
You are StudyPilot AI, a practical study planner.

Create a realistic study plan based on the student's topic or notes.

Use this structure:

1. Study Goal
2. What to Learn First
3. Step-by-Step Study Order
4. Practice Task
5. Revision Method
6. Self-Test
7. Final Revision Tip

Rules:
- Make the plan realistic.
- Prioritize important concepts.
- Use simple English.
- Do not overload the student.
""",

    "timetable": """
You are StudyPilot AI, a smart timetable generator for students.

The student will provide:
- Subject or topic
- Available study time
- Number of days
- Optional notes or syllabus

Create a practical study timetable.

IMPORTANT:
Do not claim that something is an official exam question unless the student explicitly provides official questions.

Instead, identify:
- High-priority topics
- Important concepts
- Important practice questions based on the supplied content

Use this structure:

1. STUDY GOAL

2. HIGH-PRIORITY TOPICS
Rank the topics as:
HIGH
MEDIUM
LOW

3. SMART STUDY TIMETABLE
Create a clear day-by-day schedule.

For each day include:
- Time
- Topic
- What to study
- Practice/revision activity

4. IMPORTANT PRACTICE QUESTIONS
Give useful questions the student should practice based on the supplied topic/content.

5. FINAL REVISION
Give a short revision strategy.

6. SELF-TEST
Give 3 quick questions to check understanding.

Rules:
- Respect the available time.
- Give breaks where appropriate.
- Put difficult/high-priority topics earlier.
- Include revision.
- Do not invent syllabus content when the student has not supplied it.
- Use simple English.
"""
}


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------------------------------
# SAFE HEALTH CHECK
# ---------------------------------------------------------

@app.route("/health")
def health():
    return jsonify({
        "status": "StudyPilot is running",
        "api_key_configured": bool(api_key)
    })


# ---------------------------------------------------------
# AI REQUEST
# ---------------------------------------------------------

@app.route("/ask", methods=["POST"])
def ask():

    # Check API configuration
    if client is None:
        return jsonify({
            "error": "OpenAI API key is not configured. Please check your .env file."
        }), 500

    # Read JSON safely
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "No request data was received."
        }), 400

    # Get input
    user_input = str(data.get("input", "")).strip()
    tool = str(data.get("tool", "explain")).strip()

    # Validate empty input
    if not user_input:
        return jsonify({
            "error": "Please enter a topic, question, notes, or answer."
        }), 400

    # Validate input length
    if len(user_input) > 6000:
        return jsonify({
            "error": "Please keep your input below 6000 characters."
        }), 400

    # Validate selected tool
    if tool not in PROMPTS:
        return jsonify({
            "error": "Invalid StudyPilot mode selected."
        }), 400

    try:

        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions=PROMPTS[tool],
            input=user_input
        )

        answer = response.output_text.strip()

        if not answer:
            return jsonify({
                "error": "The AI returned an empty response. Please try again."
            }), 502

        return jsonify({
            "response": answer
        })

    except Exception as error:

        # Print only the error type to avoid accidentally exposing secrets
        print("STUDYPILOT AI ERROR:", type(error).__name__)

        return jsonify({
            "error": "StudyPilot could not connect to the AI service. Please check your API key and try again."
        }), 500


# ---------------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
